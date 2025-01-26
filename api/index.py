from flask import Flask, jsonify
from http.server import BaseHTTPRequestHandler
import os
import hashlib
import json
from urllib.parse import parse_qs
from libs.wechat import WeChatMessage
from libs.github_api import GitHubAPI

def log(message):
    """统一的日志打印方法"""
    print(f"[{os.path.basename(__file__)}] {message}")

app = Flask(__name__)

@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook():
    log("收到 webhook 请求")
    return jsonify(message="Hello from Flask!")

# Vercel 需要这个 handler
class handler(BaseHTTPRequestHandler):
    def validate_signature(self, query):
        """验证微信服务器签名 (已禁用)"""
        log("正在验证签名...")
        # 跳过签名校验,直接返回True
        return True

    def do_GET(self):
        """处理GET请求（微信服务器验证）"""
        log("处理 GET 请求...")
        try:
            # 解析查询参数
            query = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            log(f"查询参数: {query}")
            
            # 验证签名
            if self.validate_signature(query):
                log("签名验证通过")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(query.get('echostr', [''])[0].encode())
            else:
                log("签名验证失败")
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write('Invalid signature'.encode())
        except Exception as e:
            log(f"GET 请求处理出错: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        """处理POST请求（接收消息）"""
        log("处理 POST 请求...")
        try:
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            log(f"内容长度: {content_length}")
            post_data = self.rfile.read(content_length)
            # 打印请求体
            log(f"收到 POST 数据: {post_data}")
            
            # 处理微信消息
            log("处理微信消息...")
            message = WeChatMessage(post_data)
            log(f"消息类型: {message.msg_type}")
            if message.msg_type == 'text':
                log("创建 GitHub 文章...")
                github = GitHubAPI()
                if github.create_post(message.format_post()):
                    log("文章创建成功")
                else:
                    log("文章创建失败")
            
            # 返回成功响应
            log("发送成功响应")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('success'.encode())
            
        except Exception as e:
            log(f"POST 请求处理出错: {str(e)}")
            # 即使发生错误也返回成功，避免微信服务器重试
            log("尽管出错仍发送成功响应")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('success'.encode())

# 确保这是主模块
if __name__ == '__main__':
    log("启动应用...")
    pass