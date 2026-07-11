import os
import sys
import datetime
import json
import hashlib
import requests
from pypdf import PdfWriter
from playwright.sync_api import sync_playwright
from config import SITES_CONFIG, GITEE_TOKEN, GITEE_REPO, GITEE_ISSUE_NUM, SENDER_EMAIL
from scraper import check_for_new_articles, save_article_as_pdf
from notifier import send_email_with_pdfs

def get_cloud_history():
    """从 Gitee 仓库指定 Issue 的评论中读取最新已发文章的 URL 集合"""
    repo = GITEE_REPO if GITEE_REPO else os.environ.get("GG_REPOSITORY", "")
    token = GITEE_TOKEN
    issue_num = GITEE_ISSUE_NUM
    
    if not token or not repo:
        print("提示：未配置 GITEE_TOKEN 或 GITEE_REPO，本地运行或流水线运行将不使用去重。")
        return set()
        
    url = f"https://gitee.com/api/v5/repos/{repo}/issues/{issue_num}/comments?access_token={token}"
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"正在从 Gitee 仓库 {repo} 的 Issue #{issue_num} 评论中拉取已发送历史记录...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            comments = response.json()
            if not comments:
                print("Gitee Issue 暂无评论，云端暂无历史发送记录。")
                return set()
            # 拿到最新发表的一条评论（即列表的最后一条）
            latest_comment = comments[-1]
            body_text = latest_comment.get("body", "")
            if not body_text or body_text.strip() == "":
                print("最新评论内容为空，云端去重历史判定为空。")
                return set()
            try:
                # 解析评论正文里的 JSON 列表
                urls = json.loads(body_text.strip())
                print(f"成功从 Gitee 评论获取去重历史，共 {len(urls)} 条记录。")
                return set(urls)
            except json.JSONDecodeError:
                print("最新评论内容非合法 JSON 列表格式，判定为空历史。")
                return set()
        elif response.status_code == 404:
            print(f"错误：未在 Gitee 上找到 Issue #{issue_num}。请确认您在 Gitee 仓库的“任务”中已经新建了该 Issue！")
            return set()
        else:
            print(f"Gitee 历史评论读取失败，HTTP 状态码: {response.status_code}，响应: {response.text}")
            return set()
    except Exception as e:
        print(f"Gitee 历史评论读取网络异常: {str(e)}，本次运行将不使用去重。")
        return set()

def save_cloud_history(sent_urls):
    """将已发文章的 URL 列表作为新评论同步到 Gitee Issue 中"""
    repo = GITEE_REPO if GITEE_REPO else os.environ.get("GG_REPOSITORY", "")
    token = GITEE_TOKEN
    issue_num = GITEE_ISSUE_NUM
    
    if not token or not repo:
        print("提示：未配置 GITEE_TOKEN 或 GITEE_REPO，跳过 Gitee 去重历史更新。")
        return False
        
    url = f"https://gitee.com/api/v5/repos/{repo}/issues/{issue_num}/comments?access_token={token}"
    headers = {
        "Content-Type": "application/json"
    }
    
    # 限制列表长度，防止数据过大（只保留最近 200 条）
    history_list = list(sent_urls)[-200:]
    json_data = json.dumps(history_list, ensure_ascii=False, indent=2)
    
    print(f"正在将最新已发送文章历史作为新评论同步更新至 Gitee Issue #{issue_num}...")
    try:
        # 使用 POST 创建评论
        response = requests.post(url, headers=headers, json={"body": json_data}, timeout=15)
        if response.status_code == 201:
            print("Gitee Issue 评论去重历史记录同步成功！")
            return True
        else:
            print(f"Gitee Issue 评论同步失败，HTTP 状态码: {response.status_code}，响应: {response.text}")
            return False
    except Exception as e:
        print(f"Gitee Issue 评论同步发生网络异常: {str(e)}")
        return False


# 是否开启本地测试模式（开启后只下载 PDF，不发送邮件）
TEST_MODE = False

def merge_pdfs(pdf_paths, output_filename):
    """将多个 PDF 文件合并为一个"""
    if not pdf_paths:
        return None
    
    merger = PdfWriter()
    for pdf in pdf_paths:
        try:
            merger.append(pdf)
        except Exception as e:
            print(f"合并 {pdf} 时出错: {e}")
            
    merger.write(output_filename)
    merger.close()
    
    # 清理零散的单篇 PDF 文件
    for pdf in pdf_paths:
        try:
            os.remove(pdf)
        except:
            pass
            
    return output_filename

def main():
    all_pdf_paths = []
    output_folder = "test_downloads" if TEST_MODE else "output"
    
    # 1. 强行构造东八区（北京时间）时区对象，保证在任何云端/本地环境均准确
    tz_beijing = datetime.timezone(datetime.timedelta(hours=8))
    beijing_now = datetime.datetime.now(tz_beijing)
    current_hour = beijing_now.hour
    
    # 2. 启动时拉取云端历史去重数据
    sent_history = get_cloud_history()
    
    # 3. 动态决定需要扫描的日期范围与邮件时段后缀
    if current_hour < 12:
        beijing_yesterday = beijing_now - datetime.timedelta(days=1)
        scan_dates = [beijing_yesterday, beijing_now]
        check_range_text = "昨天及今天发布的文章 (双日防漏)"
        time_suffix = "上午"
    else:
        scan_dates = [beijing_now]
        check_range_text = "今天发布的文章"
        time_suffix = "下午"
  
    beijing_now_str = beijing_now.strftime("%Y-%m-%d %H:%M")
    
    # 构造动态邮件元信息报头
    summary_lines = [
        "=================================",
        "【爬虫任务简报】",
        f"爬取时间：{beijing_now_str} (北京时间)",
        f"检查范围：{check_range_text}",
        "去重状态：已自动过滤之前发送过的文章",
        "=================================\n",
        "【网站更新情况通报】：\n"
    ]
    
    # 用于收集首页目录的列表
    article_catalog = []
    
    with sync_playwright() as p:
        # 启动浏览器 (无头模式)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 1024},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        
        for site in SITES_CONFIG:
            page = context.new_page()
            try:
                # 分别获取日期列表中各日期的文章并合并
                new_articles = []
                for date_dt in scan_dates:
                    date_str = date_dt.strftime(site['date_format'])
                    articles = check_for_new_articles(page, site, target_date=date_str)
                    new_articles.extend(articles)
                
                # 过滤掉已发送的文章
                filtered_articles = []
                for article in new_articles:
                    if article['url'] not in sent_history:
                        filtered_articles.append(article)
                    else:
                        print(f"[已发过滤] {site['name']} - 标题: {article['title']} 已发送过，跳过。")
                
                # 记录通报情况
                if filtered_articles:
                    summary_lines.append(f"🟢 [有更新] {site['name']}：共更新了 {len(filtered_articles)} 篇文章")
                else:
                    summary_lines.append(f"⚪ [无更新] {site['name']}")
                
                for article in filtered_articles:
                    pdf_path = save_article_as_pdf(page, article, site, output_dir=output_folder)
                    if pdf_path:
                        all_pdf_paths.append(pdf_path)
                        article_catalog.append({
                            'title': article['title'],
                            'source': site['name'],
                            'url': article['url']  # 记录URL用于发送成功后的历史更新
                        })
            except Exception as e:
                print(f"处理网站 {site['name']} 时发生错误: {str(e)}")
                summary_lines.append(f"🔴 [抓取报错] {site['name']}：{str(e)}")
            finally:
                page.close()
                
        browser.close()
        
    date_prefix = beijing_now.strftime("%m-%d")
    
    # 如果抓取到了新的 PDF
    if all_pdf_paths:
        print(f"\n共成功抓取到 {len(all_pdf_paths)} 篇新文章！")
        
        print("正在生成今日目录首页...")
        # ======================= 生成目录 PDF =======================
        toc_html = f"""
        <html><head><meta charset='UTF-8'>
        <style>
            body {{ font-family: 'Microsoft YaHei', sans-serif; padding: 40px; line-height: 2; color: #333; }}
            h1 {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #e0e0e0; padding-bottom: 20px; }}
            ul {{ font-size: 18px; list-style-type: none; padding-left: 0; }}
            li {{ margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px dashed #eee; }}
            .title {{ font-weight: bold; color: #111; display: block; }}
            .source {{ font-size: 14px; color: #888; margin-top: 5px; display: block; }}
        </style>
        </head><body>
        <h1>今日更新简报目录</h1><ul>
        """
        for i, item in enumerate(article_catalog):
            toc_html += f"<li><span class='title'>{i+1}. {item['title']}</span><span class='source'>来源: {item['source']}</span></li>"
        toc_html += "</ul></body></html>"
        
        # 利用 playwright 再开一个页面渲染目录
        with sync_playwright() as p2:
            toc_browser = p2.chromium.launch(headless=True)
            toc_page = toc_browser.new_page()
            toc_page.set_content(toc_html)
            toc_pdf_path = os.path.join(output_folder, "00_目录首页.pdf")
            toc_page.pdf(path=toc_pdf_path, format="A4", print_background=True, margin={"top":"2cm", "bottom":"2cm", "left":"1.5cm", "right":"1.5cm"})
            toc_browser.close()
            
        # 将生成的目录文件插入到要合并的文件列表最前面
        all_pdf_paths.insert(0, toc_pdf_path)
        # ============================================================
        
        # === 方案二：多文件合并 ===
        today_str = beijing_now.strftime("%Y-%m-%d")
        merged_pdf_name = f"{today_str}_每日监控简报合集.pdf"
        merged_pdf_path = os.path.join(output_folder, merged_pdf_name)
        
        print("正在将所有文章合并为一本 PDF 电子书...")
        final_pdf_path = merge_pdfs(all_pdf_paths, merged_pdf_path)
        
        # 构造带有前置日期与下午/上午后缀的主题
        subject_title = f"【{date_prefix}】网站数据更新简报 ({time_suffix})"
        
        if TEST_MODE:
            print(f"【测试模式已开启】已跳过发送邮件。")
            print(f"生成的【终极合集 PDF】已保存到：{final_pdf_path}")
            print(f"拟发送的主题为：{subject_title}")
            print("\n=== 以下是准备发送的邮件正文 ===")
            print("\n".join(summary_lines))
            print("=================================")
        else:
            print("准备发送邮件...")
            # 将收集好的通报内容组合成邮件正文
            body_text = "\n".join(summary_lines)
            
            # 现在我们只发送合并后的这唯一一个 PDF
            success = send_email_with_pdfs([final_pdf_path], subject=subject_title, body_text=body_text)
            if success:
                print("所有任务执行完毕。")
                # 2. 邮件发送成功后，把本次发送的文章 URL 合并存回云端
                new_sent_urls = set(item['url'] for item in article_catalog)
                updated_history = sent_history.union(new_sent_urls)
                save_cloud_history(updated_history)
            else:
                print("发送失败，退出。")
                sys.exit(1)
    else:
        print("指定范围内没有任何网站发布新文章。")
        subject_title = f"【{date_prefix}】今日网站无更新通报 ({time_suffix})"
        
        # 发送无更新通报邮件，让你知道系统在正常运行
        body_text = "\n".join(summary_lines)
        send_email_with_pdfs([], subject=subject_title, body_text=body_text)

if __name__ == "__main__":
    main()
