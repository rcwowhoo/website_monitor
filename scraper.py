import re
import os
from datetime import datetime
import requests

def build_clean_html(title_html, content_html, site_name="", publish_date="", source_url=""):
    meta_html = ""
    if site_name or publish_date or source_url:
        meta_html = f"""
        <div class="meta-info">
            {'<span>来源站点: ' + site_name + '</span>' if site_name else ''}
            {'<span>发布日期: ' + publish_date + '</span>' if publish_date else ''}
            {'<span><a href="' + source_url + '">查看原文</a></span>' if source_url else ''}
        </div>
        """
        
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif; padding: 20px; line-height: 1.8; color: #333; }}
            h1 {{ text-align: center; font-size: 24px; margin-bottom: 10px; color: #000; }}
            .meta-info {{ text-align: center; font-size: 14px; color: #888; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee; }}
            .meta-info span {{ margin: 0 10px; }}
            .meta-info a {{ color: #1a73e8; text-decoration: none; }}
            p {{ font-size: 16px; margin-bottom: 12px; text-indent: 2em; text-align: justify; }}
            img {{ max-width: 100% !important; height: auto !important; display: block; margin: 10px auto; }}
            table {{ width: 100% !important; border-collapse: collapse; margin-bottom: 15px; }}
            table, th, td {{ border: 1px solid #ccc; padding: 8px; }}
        </style>
    </head>
    <body>
        {title_html}
        {meta_html}
        <div>{content_html}</div>
    </body>
    </html>
    """

def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    # 移除 Windows 文件名非法字符 + 换行/制表等控制字符
    filename = re.sub(r'[\\/*?:"<>|\r\n\t]', '', filename)
    return filename.strip()

def check_for_new_articles(page, site_config, target_date=None):
    """
    检查指定网站是否有指定日期的新文章
    """
    if not target_date:
        target_date = datetime.now().strftime(site_config['date_format'])
        
    new_articles = []
    
    print(f"正在检查网站: {site_config['name']} ({site_config['url']})")
    print(f"目标日期: {target_date}")
    
    try:
        page.goto(site_config['url'], wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"列表页加载可能未完全完成，尝试继续解析 ({e})")

    # 等待列表加载
    try:
        page.wait_for_selector(site_config['list_selector'], timeout=30000)
    except Exception as e:
        print(f"列表选择器未在预期时间内出现，尝试继续解析 ({e})")
    
    # 【极速优化】：使用 JavaScript 批量提取，将几十秒的逐行解析缩短到几毫秒
    try:
        items_data = page.evaluate(f"""() => {{
            const items = document.querySelectorAll('{site_config["list_selector"]}');
            return Array.from(items).map(item => {{
                const dateElem = item.querySelector('{site_config["date_selector"]}');
                const linkElem = item.querySelector('{site_config["link_selector"]}');
                return {{
                    date: dateElem ? dateElem.innerText.trim() : '',
                    title: linkElem ? linkElem.innerText.trim() : '',
                    href: linkElem ? linkElem.getAttribute('href') : ''
                }};
            }});
        }}""")
    except Exception as e:
        print(f"批量解析页面失败: {e}")
        return new_articles
        
    print(f"找到 {len(items_data)} 条列表记录。")
    
    for item in items_data:
        date_text = item['date']
        title = item['title']
        href = item['href']
        
        if not title or not href:
            continue
            
        # 拼接完整链接
        domain_prefix = site_config.get('domain_prefix', '')
        if domain_prefix and not href.startswith('http'):
            full_url = domain_prefix + href
        elif not href.startswith('http'):
            from urllib.parse import urljoin
            full_url = urljoin(site_config['url'], href)
        else:
            full_url = href
            
        # 由于日志太多也会卡顿，我们只打印匹配日期的文章，历史文章直接跳过
        if target_date in date_text:
            print(f"[发现新文章] 日期: {date_text}, 标题: {title}")
            new_articles.append({
                'title': title,
                'url': full_url,
                'date': date_text
            })
            
    return new_articles

def save_article_as_pdf(page, article, site_config, output_dir="output"):
    """
    访问文章页面并将其保存为纯净版 PDF
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    title_clean = sanitize_filename(article['title'])
    pdf_path = os.path.join(output_dir, f"{title_clean}.pdf")
    
    print(f"正在转换 PDF: {title_clean}")
    print(f"访问URL: {article['url']}")
    
    # 针对部分政府网站直接提供 PDF 附件链接的特殊处理
    if article['url'].lower().endswith('.pdf'):
        print("检测到原生的 PDF 文件链接，启动直接下载...")
        import requests
        try:
            # 下载原生 PDF
            response = requests.get(article['url'], stream=True, timeout=30)
            if response.status_code == 200:
                with open(pdf_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"成功下载原生 PDF: {pdf_path}")
                return pdf_path
            else:
                print(f"原生 PDF 下载失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"下载原生 PDF 时出错: {e}")
            return None
            
    try:
        page.goto(article['url'], wait_until="domcontentloaded", timeout=60000)
        # 等待一小会儿确保正文加载
        page.wait_for_timeout(2000)
        
        # 提取到的最终纯净 HTML
        clean_html = ""
        
        title_selector = site_config.get('title_selector')
        content_selector = site_config.get('content_selector')
        
        # 准备元数据
        site_name = site_config.get('name', '未知站点')
        pub_date = article.get('date', '')
        src_url = article.get('url', '')
        
        # 方案A：如果用户手工配置了精准的选择器，优先使用
        if title_selector and content_selector:
            try:
                page.wait_for_selector(content_selector, timeout=5000)
                title_html = page.locator(title_selector).inner_html() if page.locator(title_selector).count() > 0 else f"<h1>{article['title']}</h1>"
                content_html = page.locator(content_selector).inner_html()
                clean_html = build_clean_html(title_html, content_html, site_name, pub_date, src_url)
            except Exception as extract_e:
                print(f"使用选择器提取内容失败: {extract_e}")
                
        # 方案B：智能阅读模式。如果用户没填规则，或者规则失效，自动触发！
        if not clean_html:
            print(f"  -> 正在启动【智能阅读模式】自动识别正文...")
            try:
                # 注入 Mozilla 官方的 Readability 算法（与主流浏览器阅读模式相同）
                page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/readability/0.4.4/Readability.min.js")
                # 执行解析
                article_data = page.evaluate("""() => {
                    var documentClone = document.cloneNode(true);
                    return new Readability(documentClone).parse();
                }""")
                
                if article_data and article_data.get('content'):
                    title_html = f"<h1>{article_data.get('title', article['title'])}</h1>"
                    content_html = article_data['content']
                    clean_html = build_clean_html(title_html, content_html, site_name, pub_date, src_url)
                else:
                    print("  -> 智能识别失败，将保存原始网页页面。")
            except Exception as e:
                print(f"  -> 智能提取时出错: {e}")

        # 如果成功生成了纯净 HTML，覆盖当前页面
        if clean_html:
            page.set_content(clean_html)

        # 直接保存为 PDF（正文中的文件链接自然保留为可点击链接）
        page.pdf(path=pdf_path, format="A4", print_background=True, margin={"top":"2cm", "bottom":"2cm", "left":"1.5cm", "right":"1.5cm"})

        print(f"成功保存: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"保存 PDF 失败: {article['url']} - {str(e)}")
        return None
