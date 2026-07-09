# config.py

# 网站监控配置列表
# 您可以在这里添加更多想要监控的网站
SITES_CONFIG = [
      {
        "name": "广东省统计局-统计快讯",
        "url": "http://stats.gd.gov.cn/tjkx185/index.html",
        "list_selector": ".overview-news-list li",
        "link_selector": "a.news-link",
        "date_selector": "span.news-date",
        "title_selector": ".article-title",
        "content_selector": ".article-content",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "广州市统计局-数据解读",
        "url": "http://tjj.gz.gov.cn/stats_newtjyw/sjjd/index.html",
        "list_selector": ".newslist2 li",
        "link_selector": "a",
        "date_selector": "span",
        "title_selector": ".zw-title",
        "content_selector": "#zoomcon",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "统计快报-深圳市统计局网站",
        "url": "https://tjj.sz.gov.cn/zwgk/zfxxgkml/tjsj/tjkb/index.html",
        "list_selector": ".list-article ul.column-article li",
        "link_selector": "a",
        "date_selector": "a p.article-time",
        "title_selector": ".text-title",
        "content_selector": ".articleBox",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "珠海市统计局-统计分析",
        "url": "https://tjj.zhuhai.gov.cn/tjsj/tjzl/tjfx/",
        "list_selector": ".list-01 ul li.item",
        "link_selector": "a.link",
        "date_selector": "span.time",
        "title_selector": ".info-tit-box .tit",
        "content_selector": ".content-box",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "汕头市统计局-综合",
        "url": "https://www.shantou.gov.cn/tjj/tjsj/jdsj/zh/index.html",
        "list_selector": ".list_div.mar-top2",
        "link_selector": ".list-right_title a",
        "date_selector": "table td:first-child",
        "title_selector": ".title_cen ucaptitle",
        "content_selector": "#zoomcon ucapcontent",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "佛山市统计局-统计分析",
        "url": "https://www.foshan.gov.cn/gzjg/stjj/tjfx_1110960/index.html",
        "list_selector": ".list.inlist3 li",
        "link_selector": "a",
        "date_selector": "span",
        "title_selector": "h3.conetent-title",
        "content_selector": ".TRS_Editor.zhengwen",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "梅州市人民政府门户网站-数据解读分析",
        "url": "https://www.meizhou.gov.cn/zwgk/zfjg/stjj/tjsj/tjfx/index.html",
        "list_selector": ".list li",
        "link_selector": "a",
        "date_selector": "span.date",
        "title_selector": ".show_ti",
        "content_selector": ".show_con",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "惠州市统计局-统计数据",
        "url": "http://www.huizhou.gov.cn/bmpd/hzstjj/tjsj/index.html",
        "list_selector": "#div_list .ul_art_row",
        "link_selector": ".li_art_title a",
        "date_selector": ".li_art_date",
        "title_selector": "h1.info_title",
        "content_selector": "#content-container",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "汕尾市统计局-统计数据",
        "url": "https://www.shanwei.gov.cn/swtjj/tjsj/index.html",
        "list_selector": ".list_div",
        "link_selector": ".list-right_title a",
        "date_selector": "table td:first-child",
        "title_selector": ".title_cen",
        "content_selector": "#zoom",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "东莞市统计调查信息网-统计数据",
        "url": "http://tjj.dg.gov.cn/sjfb/tjsj/index.html",
        "list_selector": ".list li",
        "link_selector": "h4 a",
        "date_selector": ".fix1 span.fl",
        "title_selector": "h1",
        "content_selector": ".article-detail",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "中山市统计局-统计数据",
        "url": "http://stats.zs.gov.cn/zwgk/tjxx/tjzl/",
        "list_selector": "#recordlist li:not(.gap)",
        "link_selector": "a",
        "date_selector": "span",
        "title_selector": ".open_show h2",
        "content_selector": ".sc",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "江门市统计局-数据解读与统计分析",
        "url": "http://www.jiangmen.gov.cn/bmpd/jmstjj/zwgk/zcjd/index.html",
        "list_selector": ".infoList li",
        "link_selector": "a",
        "date_selector": "span",
        "title_selector": "h1",
        "content_selector": "#zhengwen",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "阳江市统计局政府信息公开平台",
        "url": "http://www.yangjiang.gov.cn/yjtjj/gkmlpt/index",
        "list_selector": "#postList tr",
        "link_selector": "td.first-td a",
        "date_selector": "td:nth-child(2)",
        "title_selector": "h1.title",
        "content_selector": ".article-content",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "湛江市统计信息网-统计月报",
        "url": "https://www.zhanjiang.gov.cn/zjsfw/bmdh/tjxxw/zwgk/tjsjzl/tjyb/index.html",
        "list_selector": ".newsList ul.list li",
        "link_selector": "a",
        "date_selector": ".time",
        "title_selector": ".cont h3",
        "content_selector": ".article",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "茂名市统计局-法定主动公开内容",
        "url": "http://www.maoming.gov.cn/mmtjj/gkmlpt/index",
        "list_selector": "#postList table.table-content tbody tr",
        "link_selector": "a.document-number",
        "date_selector": "td:nth-child(2)",
        "title_selector": "h1.title",
        "content_selector": ".article-content",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "肇庆市统计局-统计数据",
        "url": "https://www.zhaoqing.gov.cn/zqtjj/gkmlpt/index#4468",
        "list_selector": ".table-content tbody tr",
        "link_selector": "a.document-number",
        "date_selector": "td:nth-child(2)",
        "title_selector": "h1.title.document-number",
        "content_selector": ".article-content",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "潮州市统计局-部门文件",
        "url": "https://www.chaozhou.gov.cn/zwgk/szfgz/stjj/bmwj/index.html",
        "list_selector": ".ul_news li",
        "link_selector": "a",
        "date_selector": "b",
        "title_selector": ".detail_content h2",
        "content_selector": ".info",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "揭阳统计信息网-月报",
        "url": "http://www.jieyang.gov.cn/tjj/tjsj/yb/index.html",
        "list_selector": ".list ul li",
        "link_selector": "a",
        "date_selector": "span",
        "title_selector": ".tit",
        "content_selector": ".cont",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "云浮市统计局-统计月报",
        "url": "https://www.yunfu.gov.cn/tjj/zdht/sy/tjyb/index.html",
        "list_selector": ".ny_right_list li",
        "link_selector": "a",
        "date_selector": "span",
        "title_selector": ".ny_min_txt",
        "content_selector": "#Zoom",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "河源市人民政府门户网站-统计月报",
        "url": "http://www.heyuan.gov.cn/zwgk/tjsj/tjyb/index.html",
        "list_selector": "ul.list li.list-item",
        "link_selector": "a.list-item-cnt",
        "date_selector": "span.list-date",
        "title_selector": ".content-title",
        "content_selector": ".content-text",
        "date_format": "%Y-%m-%d",
        "domain_prefix": "",
    },
    {
        "name": "韶关市统计局-法定主动公开内容",
        "url": "https://www.sg.gov.cn/sgtjj/gkmlpt/index",
        "list_selector": ".table-content tbody tr, #postList table tbody tr",
        "link_selector": "a.document-number, td.first-td a",
        "date_selector": "td:nth-child(2)",
        "title_selector": "h1.title",
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

def _clean_env_value(value):
    """Gitee Go 有时会把变量包成 ["value"] 格式，统一清理"""
    if not value:
        return value
    if value.startswith('["') and value.endswith('"]'):
        return value[2:-2]
    if value.startswith('[') and value.endswith(']'):
        inner = value[1:-1]
        if inner.startswith('"') and inner.endswith('"'):
            inner = inner[1:-1]
        return inner
    return value

SMTP_SERVER = _clean_env_value(os.environ.get("SMTP_SERVER", "smtp.qq.com")) # 默认使用QQ邮箱服务器，可修改
SMTP_PORT = int(_clean_env_value(os.environ.get("SMTP_PORT", "465")))        # 默认SSL端口为465
SENDER_EMAIL = _clean_env_value(os.environ.get("SENDER_EMAIL", ""))
EMAIL_PASSWORD = _clean_env_value(os.environ.get("EMAIL_PASSWORD", ""))      # 这里填授权码
RECEIVER_EMAIL = _clean_env_value(os.environ.get("RECEIVER_EMAIL", ""))
