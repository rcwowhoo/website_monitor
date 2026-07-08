# config.py

# 网站监控配置列表
# 您可以在这里添加更多想要监控的网站
SITES_CONFIG = [
    {
        "name": "广州市统计局-数据解读",
        "url": "https://tjj.gz.gov.cn/stats_newtjyw/sjjd/index.html",
        # 列表项的 CSS 选择器
        "list_selector": ".newslist2.common_list ul li",
        # 链接的选择器（相对于 list_selector）
        "link_selector": "a",
        # 日期的选择器（相对于 list_selector）
        "date_selector": "span",
        # 文章详情页的标题选择器
        "title_selector": ".zw-title",
        # 文章详情页的正文选择器
        "content_selector": ".zw",
        # 日期格式化字符串，用于解析提取出的时间文本
        "date_format": "%Y-%m-%d",
        # 域名前缀（如果提取到的链接是相对路径，需要拼上这个前缀）
        "domain_prefix": "", 
    },
    {
        "name": "广东省统计局-统计快讯",
        "url": "https://stats.gd.gov.cn/tjkx185/index.html",
        # 列表项的 CSS 选择器
        "list_selector": ".overview-news-list .news-item",
        # 链接的选择器（相对于 list_selector）
        "link_selector": "a.news-link",
        # 日期的选择器（相对于 list_selector）
        "date_selector": "span.news-date",
        # 文章详情页的标题选择器
        "title_selector": ".article-title",
        # 文章详情页的正文选择器
        "content_selector": ".article-content",
        # 日期格式化字符串，用于解析提取出的时间文本
        "date_format": "%Y-%m-%d",
        # 域名前缀（如果提取到的链接是相对路径，需要拼上这个前缀）
        "domain_prefix": "", 
    },
    {
        "name": "广东省发展和改革委员会 - 商品价格",
        "url": "https://drc.gd.gov.cn/spjg/index.html",
        "list_selector": ".comlist1 li",
        "link_selector": "a",
        "date_selector": "span",
        "title_selector": "h4.wdtit",
        "content_selector": "#content1",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "广东省统计局-统计公报",
        "url": "https://stats.gd.gov.cn/tjgb/index.html",
        "list_selector": ".overview-news-list li",
        "link_selector": "a.news-link",
        "date_selector": "span.news-date",
        "title_selector": ".article-title",
        "content_selector": ".article-content",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
]

# 邮件发送相关配置 (这些值将从系统环境变量中读取，为了安全，请勿直接写在代码中)
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.qq.com") # 默认使用QQ邮箱服务器，可修改
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))          # 默认SSL端口为465
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")      # 这里填授权码
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "")
