# 🚀 自动化网页监测与 PDF 简报生成系统 (Gitee Go 云端去重版)

本项目是一个全自动化的资讯监控与邮件简报分发系统。它能够按照预设的定时计划，自动爬取目标网站的更新内容，将其转换为纯净版 PDF，并合并打包发送至指定的邮箱中。

系统内置了**智能时区校准**、**多时间段智能扫描（上午防漏、下午汇总结案）**以及基于**云端轻量 Key-Value 数据库（`kvdb.io`）的无状态去重机制**，在确保不漏掉任何一篇下午及夜间更新的同时，绝对避免在一天多次执行时发送重复文章邮件。

---

## 📂 项目文件结构说明

* **[main.py](file:///d:/VS_saveit/website_monitor/main.py)**：主程序运行入口。负责全局流程控制、北京时间时区计算、上午/下午抓取日期判定、云端去重接口交互以及邮件发送调度。
* **[config.py](file:///d:/VS_saveit/website_monitor/config.py)**：配置文件。定义了被监控网站的爬取规则（选择器、日期格式等）以及邮件服务器基本参数。
* **[scraper.py](file:///d:/VS_saveit/website_monitor/scraper.py)**：网页爬取与解析模块。使用 Playwright 控制无头浏览器访问目标页面，提供精准选择器抓取以及智能阅读模式（基于 Readability 算法自动识别正文），并最终渲染输出为标准 A4 PDF。
* **[notifier.py](file:///d:/VS_saveit/website_monitor/notifier.py)**：邮件投递客户端模块。使用 Python `smtplib` 库封装，支持 SSL/TLS 安全通道，负责将生成的 PDF 简报发送至收件箱。
* **[batch_add_sites.py](file:///d:/VS_saveit/website_monitor/batch_add_sites.py)**：大模型辅助配置工具。读取 `urls.txt` 中的新网页链接，调用大模型自动解析提取规则并写入 `new_configs.txt`，用于快速扩展监控站点。
* **[requirements.txt](file:///d:/VS_saveit/website_monitor/requirements.txt)**：依赖包声明文件。列出了项目运行所依赖的第三方库。
* **[.gitee/.gitee-ci.yml](file:///d:/VS_saveit/website_monitor/.gitee/.gitee-ci.yml)**：Gitee Go 流水线配置文件。定义了云端容器的自动调度时间表与运行命令。

---

## 💻 本地运行与调试指南

### 1. 环境准备
确保您的计算机已安装 Python 3.8 或更高版本。在项目根目录下打开终端，执行以下命令安装依赖项：
```bash
# 安装 Python 依赖包
pip install -r requirements.txt

# 安装 Playwright 浏览器内核驱动
playwright install chromium
```

### 2. 环境变量配置
在项目根目录下创建一个名为 **`.env`** 的隐藏配置文件（可复制 `.env.example` 进行重命名），并填入您的个人邮件服务器及 API 授权配置：
```ini
# ===== SMTP 发信邮箱配置 =====
SMTP_SERVER=smtp.qq.com
SMTP_PORT=465
SENDER_EMAIL=your_sender_email@qq.com
EMAIL_PASSWORD=your_smtp_auth_code          # 必须使用邮箱网页端申请的“授权码”，非邮箱密码
RECEIVER_EMAIL=your_receiver_email@qq.com

# ===== 大模型配置 (用于自动生成爬取规则，可选) =====
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL_NAME=deepseek-chat
```
> ⚠️ **安全提示**：请保管好 `.env` 文件，切勿将其提交到公开的代码仓库。本项目已在 `.gitignore` 中将其屏蔽。

### 3. 本地运行测试
直接在终端执行主程序：
```bash
python main.py
```
若需要调试且不发送真实邮件，可修改 `main.py` 顶部的 `TEST_MODE = True`，此时程序运行后只会在本地生成 PDF 文件，不会投递邮件。**测试完毕后请务必恢复为 `TEST_MODE = False`**。

---

## 🤖 使用大模型自动生成与扩展监控站点

当您需要监控新的资讯网站时，无需手动去分析复杂的 HTML DOM 结构（CSS 选择器）。本项目提供了基于大模型辅助的半自动规则生成工具：

### 1. 配置大模型 API 环境变量
请确保您本地的 `.env` 文件中已正确配置了 LLM 变量（默认推荐使用 DeepSeek，您也可以配置任何兼容 OpenAI 格式的 API 服务）：
```ini
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx        # 大模型平台的真实 API Key
LLM_BASE_URL=https://api.deepseek.com          # API 服务请求的 Base URL
LLM_MODEL_NAME=deepseek-chat                   # 调用的模型名称
```

### 2. 写入目标网站 URL
1. 在项目根目录下找到 **[urls.txt](file:///d:/VS_saveit/website_monitor/urls.txt)** 文件（若不存在则新建）。
2. 将您想要监控的新站点“列表页”的网址复制并粘贴进去。支持一次写入多个网址，**每行一个**，格式如下：
   ```text
   http://stats.gd.gov.cn/tjkx185/index.html
   http://tjj.gz.gov.cn/stats_newtjyw/sjjd/index.html
   ```

### 3. 执行自动解析脚本
在终端中运行以下命令：
```bash
python batch_add_sites.py
```
* **执行逻辑**：脚本会通过 Playwright 加载您在 `urls.txt` 中写入的每一个列表页，自动保存该页面的 DOM 骨架并进行精简压缩；随后将页面结构作为上下文发送给大模型，大模型会在 10 秒内自动分析出列表中包含的文章链接、日期、标题等选择器规则，并输出为标准的 Python 配置字典格式。

### 4. 规则合并与上线
1. 解析完成后，大模型生成的 Python 配置代码会被自动保存在项目根目录下的 **`new_configs.txt`** 文件中。
2. 打开 `new_configs.txt`，复制生成的配置字典，其标准的结构如下：
   ```python
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
   }
   ```
3. 打开 **[config.py](file:///d:/VS_saveit/website_monitor/config.py)** 文件，将上述复制的配置字典粘贴插入到顶部的 `SITES_CONFIG = [...]` 列表当中即可。
4. 运行 `python main.py` 进行本地验证，或直接推送代码，云端便会自动启动对该站点的监控。

---

## ☁️ Gitee Go 流水线云端部署步骤

为了实现免开机、无服务器的定时自动爬取，您可以使用 Gitee 免费提供的流水线服务（Gitee Go）：

### 1. 推送代码至 Gitee 仓库
在 Gitee 上新建一个私有或公开代码仓库，将除了 `.env` 之外的所有项目代码推送到远程的 `main` 分支。

### 2. 开通 Gitee Go 服务
在您的 Gitee 仓库主页中，点击顶部导航栏中的 **“服务”** -> 选择 **“Gitee Go”** -> 点击 **“开通服务”**（首次使用需同意开通协议）。

### 3. 配置变量管理 (环境变量保护)
由于邮箱密码与授权码无法写入代码，必须将 `.env` 中的配置项保存在 Gitee 的云端变量中：
1. 进入 Gitee Go 页面，点击右上角的 **“变量管理”**。
2. 依次添加以下 5 个全局环境变量（变量名必须完全一致）：

| 变量键名 (Key) | 示例值 | 说明 |
| :--- | :--- | :--- |
| `SMTP_SERVER` | `smtp.qq.com` | 邮件服务器地址（如 QQ 邮箱为 smtp.qq.com） |
| `SMTP_PORT` | `465` | SSL 加密端口，通常为 465 |
| `SENDER_EMAIL` | `xxxxxx@qq.com` | 发件人邮箱 |
| `EMAIL_PASSWORD` | `mvlxaenjokcbdggg` | 您的邮箱授权码（非登录密码） |
| `RECEIVER_EMAIL` | `xxxxxx@qq.com` | 收件人邮箱 |

### 4. 运行流水线
回到 Gitee Go 页面，系统会自动根据项目中的 `.gitee/.gitee-ci.yml` 识别出 `gitee-email-test` 流水线。
* **手动测试**：点击列表右侧的 **“立即运行”**，验证各步骤是否全部绿灯通过，并检查邮箱是否成功收到 PDF 简报。
* **定时自动运行**：系统将根据 yml 文件中配置的 Cron 定时任务，在**每天上午 09:00 和下午 16:00（采用北京时间）** 自动启动并执行。

---

## ⚙️ 核心运行机制与黑科技解析

### 1. 北京时区校准机制
Gitee Go 等云端流水线服务器的默认系统时区通常是 UTC 时间（慢北京时间 8 小时）。
本系统在 `main.py` 内部引入了基于 Python 标准库 `datetime.timezone` 的显式东八区重置逻辑。无论容器部署在全球哪台服务器上，均能**保证 100% 准确地返回北京时间**，从而不会使上午/下午的逻辑触发发生偏差。

### 2. 智能时间段分流扫描
系统根据北京时间当前的小时数自动划分执行逻辑，并在发送的邮件中进行动态体现：
* ☀️ **上午时段 (12:00 前运行)**：
  * **扫描范围**：自动爬取**“今天全天 + 昨天全天”**的文章。这能无缝捕获昨天下午 17:00 后至深夜更新的漏网内容。
  * **邮件主题**：`【月-日】网站数据更新简报 (上午)`
* 🌙 **下午/晚上时段 (12:00 后运行)**：
  * **扫描范围**：仅爬取**“今天全天”**的文章，保证下午下班前的新闻简报效率。
  * **邮件主题**：`【月-日】网站数据更新简报 (下午)`
  * *(无更新时，对应主题会自动变更为：`【月-日】今日网站无更新通报 (上午/下午)`)*
* **正文报头**：邮件正文顶部会自动注入包含“爬取时间”、“检查范围（今天或昨天+今天）”以及“去重状态”的醒目汇总元数据框，便于新闻稿编写时对比和归档。

### 3. 轻量化云端去重数据库 (kvdb.io)
由于云端流水线容器是无状态的（运行完毕即被销毁，无法保存状态文件），为了实现多次运行不重复，系统使用了 `kvdb.io` 作为轻量云端缓存：
* **专属桶隔离**：系统会自动使用您的发信邮箱 `SENDER_EMAIL` 进行不可逆的 MD5 运算，作为云端去重桶（Bucket）的唯一标识，在保证唯一性的同时免去手动配置的繁琐。
* **过滤机制**：每次启动时，通过 HTTP GET 请求拉取已发 URL 历史；在爬取循环中对已发送的 URL 执行强制拦截，只下载和投递新发布的内容。
* **防溢出与降级**：
  * **截断机制**：同步时仅保存最近 200 条 URL 记录（约 20 KB），确保网络传输极速（0.1 秒内完成）。
  * **故障防灾**：若 `kvdb.io` 超时或服务中断，程序捕获异常后将自动降级运行（即本次直接不使用去重发送），保障了爬虫流水线的健壮度。
* **去重历史查看与管理**：
  您可以在浏览器中访问以下专属链接直接查看当前云端保存的已发网址列表：
  [https://kvdb.io/bucket_6e670623dba8b48c0037ac1b837455b7/sent_history](https://kvdb.io/bucket_6e670623dba8b48c0037ac1b837455b7/sent_history)
  *(注：初次成功发信前该页面会显示 404，属于正常现象)*
  * **重置历史**：如需测试重新发送，可在终端运行 `curl -X DELETE https://kvdb.io/bucket_6e670623dba8b48c0037ac1b837455b7/sent_history` 清空云端缓存。
