import os
import sys
import datetime
from pypdf import PdfWriter
from playwright.sync_api import sync_playwright
from config import SITES_CONFIG
from scraper import check_for_new_articles, save_article_as_pdf
from notifier import send_email_with_pdfs

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
    
    # 用于收集邮件正文通报的列表
    summary_lines = ["【今日网站更新情况通报】\n"]
    # 用于收集首页目录的列表
    article_catalog = []
    
    with sync_playwright() as p:
        # 启动浏览器 (无头模式)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 1024})
        
        for site in SITES_CONFIG:
            page = context.new_page()
            try:
                # 获取新文章（默认检查当天的日期）
                new_articles = check_for_new_articles(page, site)
                
                # 记录通报情况
                if new_articles:
                    summary_lines.append(f"🟢 [有更新] {site['name']}：共更新了 {len(new_articles)} 篇文章")
                else:
                    summary_lines.append(f"⚪ [无更新] {site['name']}")
                
                for article in new_articles:
                    pdf_path = save_article_as_pdf(page, article, site, output_dir=output_folder)
                    if pdf_path:
                        all_pdf_paths.append(pdf_path)
                        article_catalog.append({
                            'title': article['title'],
                            'source': site['name']
                        })
            except Exception as e:
                print(f"处理网站 {site['name']} 时发生错误: {str(e)}")
                summary_lines.append(f"🔴 [抓取报错] {site['name']}：{str(e)}")
            finally:
                page.close()
                
        browser.close()
        
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
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        merged_pdf_name = f"{today_str}_每日监控简报合集.pdf"
        merged_pdf_path = os.path.join(output_folder, merged_pdf_name)
        
        print("正在将所有文章合并为一本 PDF 电子书...")
        final_pdf_path = merge_pdfs(all_pdf_paths, merged_pdf_path)
        
        if TEST_MODE:
            print(f"【测试模式已开启】已跳过发送邮件。")
            print(f"生成的【终极合集 PDF】已保存到：{final_pdf_path}")
            print("\n=== 以下是准备发送的邮件正文 ===")
            print("\n".join(summary_lines))
            print("=================================")
        else:
            print("准备发送邮件...")
            # 将收集好的通报内容组合成邮件正文
            body_text = "\n".join(summary_lines)
            
            # 现在我们只发送合并后的这唯一一个 PDF
            success = send_email_with_pdfs([final_pdf_path], body_text=body_text)
            if success:
                print("所有任务执行完毕。")
            else:
                print("发送失败，退出。")
                sys.exit(1)
    else:
        print("今天没有任何网站发布新文章。")
        # 即使没有 PDF，也可以发送一封无更新通报邮件 (按需开启)
        # body_text = "\n".join(summary_lines)
        # send_email_with_pdfs([], subject="【自动抓取】今日所有网站均无更新", body_text=body_text)

if __name__ == "__main__":
    main()
