# 🇨🇳 Gitee 部署教程（国内备选方案）

如果 GitHub Actions 访问国内政府网站太慢，可以把项目部署到 Gitee（码云）。

---

## 第一步：把代码推到 Gitee

1. 注册 [gitee.com](https://gitee.com) 账号
2. 新建仓库，名称随意（如 `website_monitor`），设为**公开**

3. 回到本地电脑，添加 Gitee 远程地址：

```bash
cd d:/VS_saveit/website_monitor
git remote add gitee https://gitee.com/你的用户名/仓库名.git
git push gitee main
```

> 以后每次修改代码，先 `git push origin main`（GitHub），再 `git push gitee main`（Gitee）
> 或者本地改完直接用 Gitee 网页编辑

---

## 第二步：开启 Gitee Go 服务

1. 进入你的 Gitee 仓库 → 顶部点 **"服务"** → 选择 **"Gitee Go"**
2. 首次使用需要同意协议，开通服务（免费）

---

## 第三步：配置流水线

Gitee Go 的配置文件和 GitHub Actions 不同，需要在网页上操作：

1. 进入 Gitee Go 页面 → 点击 **"新建流水线"**
2. 选择 **"YAML 编排"**
3. 来源选择 **"master/main 分支"**
4. 把下面的内容粘贴进去：

```yaml
name: daily-scraper
displayName: 每日资讯监控

# 定时触发器：每天 UTC 10:00 = 北京时间 18:00
triggers:
  schedule:
    - cron: '0 10 * * *'

# 运行环境
runner:
  tags: linux

stages:
  - name: run-scraper
    displayName: 执行抓取与发送
    steps:
      # 1. 拉取代码
      - name: checkout
        uses: checkout@v1

      # 2. 安装 Python
      - name: setup-python
        uses: setup-python@v1
        with:
          python-version: '3.10'

      # 3. 安装依赖
      - name: install-deps
        script: |
          pip install -r requirements.txt
          pip install playwright
          playwright install-deps chromium
          playwright install chromium

      # 4. 运行主程序
      - name: run
        script: python main.py
        env:
          SMTP_SERVER: $SMTP_SERVER
          SMTP_PORT: $SMTP_PORT
          SENDER_EMAIL: $SENDER_EMAIL
          EMAIL_PASSWORD: $EMAIL_PASSWORD
          RECEIVER_EMAIL: $RECEIVER_EMAIL
```

---

## 第四步：配置密钥（环境变量）

Gitee Go 里叫"变量"，配置方式：

1. 仓库页面 → **"服务"** → **"Gitee Go"**
2. 右上角 **"变量管理"**
3. 逐个添加以下变量（值根据你的 `.env` 填写）：

| 变量名 | 示例值 |
|------|------|
| `SMTP_SERVER` | `smtp.qq.com` |
| `SMTP_PORT` | `465` |
| `SENDER_EMAIL` | `2867612710@qq.com` |
| `EMAIL_PASSWORD` | `mvlxaenjokcbdggg` |
| `RECEIVER_EMAIL` | `2867612710@qq.com` |

---

## 第五步：手动测试

1. Gitee Go 页面 → 找到你的流水线
2. 点击 **"立即运行"**
3. 查看运行日志，确认是否成功

---

## 后续维护

| 操作 | 方法 |
|------|------|
| 加新网站 | 网页打开 `config.py` → 编辑 → 提交 |
| 改运行时间 | 编辑流水线，改 `cron` 值 |
| 改邮箱密码 | Gitee Go → 变量管理 → 修改对应变量 |

---

## 注意事项

- Gitee Go 的 YAML 语法可能会更新，如果粘贴报错，以 Gitee Go 网页上的可视化编辑器为准
- Gitee 和 GitHub 两边可以同时运行，互不影响
- 建议以一方为主（比如 GitHub 主力 + Gitee 备份），免得两边都发邮件重复
