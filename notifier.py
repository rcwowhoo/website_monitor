import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, EMAIL_PASSWORD, RECEIVER_EMAIL

def send_email_with_pdfs(pdf_files, subject="【自动抓取】网站新数据更新", body_text="今日有新的数据发布，请查看附件中的 PDF 文件。"):
    if not SENDER_EMAIL or not EMAIL_PASSWORD or not RECEIVER_EMAIL:
        print("错误：发件人、授权码或收件人邮箱未配置。无法发送邮件。")
        return False
        
    print(f"准备发送邮件，共 {len(pdf_files)} 个附件...")
    
    # 构建邮件
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    
    # 邮件正文
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    
    # 添加附件
    for pdf_path in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"附件文件不存在: {pdf_path}")
            continue
            
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            
        # 获取纯文件名
        file_name = os.path.basename(pdf_path)
        
        # 将 PDF 附加到邮件中
        part = MIMEApplication(pdf_data, Name=file_name)
        part['Content-Disposition'] = f'attachment; filename="{file_name}"'
        msg.attach(part)
        
    # 连接服务器并发送
    try:
        # 尝试使用 SSL 端口 (465)
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("邮件发送成功！")
        return True
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        return False
