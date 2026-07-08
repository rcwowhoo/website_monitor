import os
import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
try:
    from openai import OpenAI
except ImportError:
    print("请先安装 openai 库: pip install openai")
    exit(1)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ================= 配置大模型 API =================
# 这里默认使用 DeepSeek 作为示例 (性价比极高，非常适合写代码和分析)
# 您可以换成阿里云千问(DashScope)、Kimi(Moonshot) 或直接使用 OpenAI
API_KEY = os.environ.get("LLM_API_KEY", "") 
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com") 
MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "deepseek-chat")

URLS_FILE = "urls.txt"
OUTPUT_FILE = "new_configs.txt"

def clean_html(html_content):
    """精简 HTML，去除无关标签以节省大模型的 Token"""
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(["script", "style", "svg", "noscript", "iframe", "footer", "header"]):
        tag.decompose()
    # 进一步移除所有元素的 style 和长段的 class 属性，保留 id 和必要的 class
    for tag in soup.find_all(True):
        if 'style' in tag.attrs:
            del tag['style']
        # 移除太长的属性，防止干扰
        for attr in list(tag.attrs):
            if attr not in ['id', 'class', 'href']:
                del tag[attr]
    
    # 获取精简后的 html 字符串
    text = str(soup)
    # 如果还是太长，截取前 30000 个字符（通常列表都在前面）
    if len(text) > 30000:
        text = text[:30000]
    return text

def analyze_with_llm(client, prompt_content):
    """调用大模型进行分析"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个资深的爬虫工程师，精通 CSS 选择器。请严格按照用户要求的 JSON 格式返回分析结果，不要附带任何 Markdown 标记或多余的解释，确保结果可以直接被 json.loads 解析。"},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.1
        )
        # 清理可能带有的 markdown 格式 (比如 ```json ... ```)
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        return json.loads(result_text.strip())
    except Exception as e:
        print(f"大模型调用失败或解析 JSON 失败: {e}")
        return None

def analyze_list_page(client, page, url):
    """分析列表页"""
    print(f"正在访问列表页: {url}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000) # 等待渲染
        html = page.content()
    except Exception as e:
        print(f"访问列表页失败: {e}")
        return None, None
        
    cleaned_html = clean_html(html)
    
    prompt = f"""
    以下是一个新闻文章列表页的精简 HTML 代码：
    ```html
    {cleaned_html}
    ```
    请分析这段 HTML，找出网页的名称和文章列表的 CSS 选择器。
    请返回一个 JSON 对象，必须包含以下四个键：
    1. "site_name": 这个网页的栏目名称（例如："广东省统计局-统计快讯"，可以结合网页的 title 标签或面包屑导航提取）
    2. "list_selector": 每一行新闻的 CSS 选择器（例如 ".news-list li"）
    3. "link_selector": 相对于 list_selector，提取标题链接的 CSS 选择器（通常是 "a" 或 "a.title"）
    4. "date_selector": 相对于 list_selector，提取发布日期的 CSS 选择器（通常是 "span.date" 或 ".time"）
    """
    
    print("正在请求大模型分析列表页结构...")
    result = analyze_with_llm(client, prompt)
    if not result:
        return None, None
        
    # 尝试验证并获取第一个详情页链接
    try:
        first_item = page.locator(result['list_selector']).first
        link_element = first_item.locator(result['link_selector']).first
        # 尝试获取 href 属性
        href = link_element.get_attribute("href")
        
        # 补全 URL
        if href and not href.startswith("http"):
            from urllib.parse import urljoin
            href = urljoin(url, href)
            
        print(f"✅ 列表页分析成功！找到第一篇文章链接: {href}")
        return result, href
    except Exception as e:
        print(f"❌ 大模型给出的选择器似乎不准确，验证失败: {e}")
        return result, None

def analyze_detail_page(client, page, url):
    """分析详情页"""
    print(f"正在访问详情页: {url}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        html = page.content()
    except Exception as e:
        print(f"访问详情页失败: {e}")
        return None
        
    cleaned_html = clean_html(html)
    
    prompt = f"""
    以下是一篇新闻详情页的精简 HTML 代码：
    ```html
    {cleaned_html}
    ```
    请分析这段 HTML，找出新闻的大标题和正文所在区域的 CSS 选择器。
    请返回一个 JSON 对象，必须包含以下两个键：
    1. "title_selector": 文章标题的 CSS 选择器（例如 ".article-title" 或 "h1"）
    2. "content_selector": 文章正文内容最外层容器的 CSS 选择器（例如 ".article-content" 或 "#zw"）
    """
    
    print("正在请求大模型分析详情页结构...")
    result = analyze_with_llm(client, prompt)
    if result:
        print("✅ 详情页分析成功！")
    return result

def main():
    if not API_KEY:
        print("【错误】未配置大模型 API Key！")
        print("请在 .env 文件中添加 LLM_API_KEY=your_key")
        print("或者在 batch_add_sites.py 顶部直接修改 API_KEY 变量。")
        return

    if not os.path.exists(URLS_FILE):
        print(f"未找到 {URLS_FILE}，已为您自动创建。")
        with open(URLS_FILE, "w", encoding="utf-8") as f:
            f.write("# 在此填入需要自动分析的网站列表页URL，每行一个\n")
            f.write("https://stats.gd.gov.cn/tjkx185/index.html\n")
        print(f"请在 {URLS_FILE} 中填入网址后重新运行。")
        return

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
    if not urls:
        print(f"{URLS_FILE} 为空，请输入网址。")
        return

    print(f"准备分析 {len(urls)} 个网站...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    generated_configs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for url in urls:
            print(f"\n=======================================")
            # 1. 分析列表页
            list_config, detail_url = analyze_list_page(client, page, url)
            
            detail_config = {}
            if detail_url:
                # 2. 分析详情页
                detail_config = analyze_detail_page(client, page, detail_url)
            else:
                print("未提取到详情页链接，跳过详情页分析。")

            # 3. 组合配置
            if list_config:
                domain_prefix = ""
                # 简单推断是否需要 domain_prefix
                # 这里暂时留空，大部分现代爬虫可通过 urljoin 自动处理
                
                config_dict = {
                    "name": list_config.get("site_name", f"自动抓取站点_{int(time.time())}"),
                    "url": url,
                    "list_selector": list_config.get("list_selector", ""),
                    "link_selector": list_config.get("link_selector", "a"),
                    "date_selector": list_config.get("date_selector", "span"),
                    "title_selector": detail_config.get("title_selector", "h1") if detail_config else "",
                    "content_selector": detail_config.get("content_selector", "") if detail_config else "",
                    "date_format": "%Y-%m-%d",
                    "domain_prefix": domain_prefix
                }
                generated_configs.append(config_dict)
                print(f"-> 该网站配置生成完毕！\n{json.dumps(config_dict, indent=4, ensure_ascii=False)}")
                
        browser.close()

    if generated_configs:
        # 将生成的配置格式化为 Python 列表字符串并追加到文件
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n# === 自动生成于 {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            for config in generated_configs:
                f.write("    {\n")
                for k, v in config.items():
                    f.write(f"        \"{k}\": \"{v}\",\n")
                f.write("    },\n")
        
        print(f"\n🎉 恭喜！已成功生成 {len(generated_configs)} 个网站配置！")
        print(f"请打开 {OUTPUT_FILE} 查看结果。")
        print("确认无误后，只需将里面的字典复制粘贴到 config.py 的 SITES_CONFIG 列表中即可。")

if __name__ == "__main__":
    main()
