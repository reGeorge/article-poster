# article-poster
文章推送助手 - 通过微信公众号推送文章到 GitHub Pages

## 项目结构
```bash
article-poster/
├── api/
│   └── index.py        # 处理微信消息的主函数
├── libs/
│   ├── github_api.py   # GitHub API 操作
│   └── wechat.py       # 微信消息处理
├── tests/              # 测试文件
├── requirements.txt    # 依赖管理
└── vercel.json         # Vercel配置
```

## 核心代码实现

1. **Webhook 处理函数**
```python
# api/index.py
from http.server import BaseHTTPRequestHandler
from libs.wechat import WeChatMessage
from libs.github_api import GitHubAPI

class handler(BaseHTTPRequestHandler):
    def validate_signature(self, query):
        """验证微信服务器签名"""
        token = os.environ.get('WECHAT_TOKEN')
        timestamp = query.get('timestamp', [''])[0]
        nonce = query.get('nonce', [''])[0]
        signature = query.get('signature', [''])[0]
        
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        hash_obj = hashlib.sha1(tmp_str.encode())
        
        return hash_obj.hexdigest() == signature

    def do_GET(self):
        """处理GET请求（微信服务器验证）"""
        query = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
        if self.validate_signature(query):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(query.get('echostr', [''])[0].encode())
        else:
            self.send_response(403)
            self.end_headers()

    def do_POST(self):
        """处理POST请求（接收消息）"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        message = WeChatMessage(post_data)
        if message.msg_type == 'text':
            github = GitHubAPI()
            github.create_post(message.format_post())
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('success'.encode())
```

2. **微信消息处理**
```python
# libs/wechat.py
import xml.etree.ElementTree as ET

class WeChatMessage:
    def __init__(self, xml_data):
        root = ET.fromstring(xml_data)
        self.msg_type = root.find('MsgType').text
        self.content = root.find('Content').text if root.find('Content') is not None else ''
        self.from_user = root.find('FromUserName').text
        self.create_time = root.find('CreateTime').text
        
    def format_post(self):
        if self.msg_type != 'text':
            return None
            
        lines = self.content.split('\n', 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ''
        
        return {
            'title': title,
            'content': content
        }
```

3. **GitHub API 操作**
```python
# libs/github_api.py
import os
import base64
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import urllib.parse

class GitHubAPI:
    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN')
        self.repo = os.environ.get('GITHUB_REPO')
        self.owner = os.environ.get('GITHUB_OWNER')
        self.branch = os.environ.get('GITHUB_BRANCH', 'master')
        
    def create_post(self, post_data):
        """创建或更新文章"""
        filename = "source/_posts/test-post.md"
        content = f"""---
title: {post_data['title']}
date: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

{post_data['content']}
"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{filename}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # 获取现有文件的 SHA（如果存在）
        sha = self.get_file_sha(filename)
        
        data = {
            'message': f'Update post: {post_data["title"]}',
            'content': base64.b64encode(content.encode()).decode(),
            'branch': self.branch
        }
        if sha:
            data['sha'] = sha
            
        request = Request(url, 
                        data=json.dumps(data).encode(),
                        headers=headers,
                        method='PUT')
        response = urlopen(request)
        return response.status == 200 or response.status == 201
```

## 环境变量配置

```env
# .env
WECHAT_TOKEN=your_wechat_token
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_repo_name
GITHUB_OWNER=your_github_username
GITHUB_BRANCH=master
```

## 本地开发

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **启动开发服务器**
```bash
vercel dev
```

3. **测试微信验证**
```bash
# 生成测试 URL
python tests/test_signature.py
# 使用生成的 URL 测试验证
curl "http://localhost:3000/api/webhook?signature=XXX&timestamp=XXX&nonce=XXX&echostr=XXX"
```

4. **测试消息发送**
```bash
# 测试发送消息
curl -X POST http://localhost:3000/api/webhook \
  -H "Content-Type: application/xml" \
  -d '<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>1704891234</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[测试文章标题
这是文章内容，
可以包含多行
支持换行符]]></Content>
    <MsgId>1234567890123456</MsgId>
  </xml>'
```

## 部署到 Vercel

1. **安装 Vercel CLI**
```bash
npm i -g vercel
```

2. **部署**
```bash
vercel
```

3. **配置环境变量**
在 Vercel 项目设置中配置相同的环境变量