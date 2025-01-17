from flask import Flask, jsonify
from http.server import BaseHTTPRequestHandler
import os
import hashlib
import json
from urllib.parse import parse_qs
from libs.wechat import WeChatMessage
from libs.github_api import GitHubAPI
import threading
import logging
import time
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook():
    return jsonify(message="Hello from Flask!")

# Vercel 需要这个 handler
class handler(BaseHTTPRequestHandler):
    def validate_signature(self, query):
        """验证微信服务器签名"""
        token = os.environ.get('WECHAT_TOKEN')
        timestamp = query.get('timestamp', [''])[0]
        nonce = query.get('nonce', [''])[0]
        signature = query.get('signature', [''])[0]
        
        # 按字典序排序
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        
        # SHA1加密
        tmp_str = ''.join(tmp_list)
        hash_obj = hashlib.sha1(tmp_str.encode())
        
        return hash_obj.hexdigest() == signature

    def do_GET(self):
        """处理GET请求（微信服务器验证）"""
        try:
            # 解析查询参数
            query = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            
            # 验证签名
            if self.validate_signature(query):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(query.get('echostr', [''])[0].encode())
            else:
                self.send_response(403)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write('Invalid signature'.encode())
        except Exception as e:
            print(f"Error in GET: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        """处理POST请求（接收消息）"""
        start_time = time.time()
        try:
            # 1. 立即返回成功响应
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('success'.encode())

            # 记录响应时间
            response_time = time.time() - start_time
            logger.info(f"Response time: {response_time:.3f} seconds")
            
            
            # 2. 异步处理消息
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            def process_message():
                try:
                    message = WeChatMessage(post_data)
                    if message.msg_type == 'text':
                        github = GitHubAPI()
                        github.create_post(message.format_post())
                        logger.info("Message processed successfully")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
            
            # 在新线程中处理消息
            threading.Thread(target=process_message).start()
            
        except Exception as e:
            logger.error(f"Error in POST handler: {str(e)}")
            # 确保即使出错也返回成功
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('success'.encode())

# 确保这是主模块
if __name__ == '__main__':
    pass 