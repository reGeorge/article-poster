import os
import base64
import json
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import urllib.parse

class GitHubAPI:
    def __init__(self):
        """初始化 GitHub API"""
        self.token = os.environ.get('GITHUB_TOKEN')
        self.repo = os.environ.get('GITHUB_REPO')
        self.owner = os.environ.get('GITHUB_OWNER')
        self.branch = os.environ.get('GITHUB_BRANCH', 'master')
        
        # 只打印非敏感的配置信息
        print(f"GitHub Configuration:")
        print(f"Owner: {self.owner}")
        print(f"Repo: {self.repo}")
        print(f"Branch: {self.branch}")
        
    def get_file_sha(self, path):
        """获取文件的 SHA"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            request = Request(url, headers=headers)
            response = urlopen(request)
            data = json.loads(response.read().decode('utf-8'))
            return data.get('sha')
        except HTTPError as e:
            if e.code == 404:
                # 文件不存在，这是正常的情况
                print(f"File {path} does not exist yet, will create new")
                return None
            else:
                print(f"HTTP Error: {e.code} - {e.reason}")
                return None
        except Exception as e:
            print(f"Error getting file SHA: {str(e)}")
            return None
        
    def create_post(self, post_data):
        """创建或更新文章"""
        if not post_data:
            return False
            
        try:
            # 使用固定的测试文件名
            filename = "source/_posts/test-post.md"
            
            # 生成文章内容
            content = f"""---
title: {post_data['title']}
date: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

{post_data['content']}
"""
            # 确保内容是 UTF-8 编码
            content_bytes = content.encode('utf-8')
            
            # 创建文件
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{filename}"
            
            # 打印请求 URL（调试用）
            print(f"Requesting URL: {url}")
            
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json; charset=utf-8'
            }
            
            # 获取文件的 SHA（如果文件已存在）
            sha = self.get_file_sha(filename)
            
            data = {
                'message': f'Update test post: {post_data["title"]}',
                'content': base64.b64encode(content_bytes).decode('utf-8'),
                'branch': self.branch
            }
            
            # 如果文件已存在，添加 SHA
            if sha:
                print(f"Updating existing file: {filename}")
                data['sha'] = sha
            else:
                print(f"Creating new file: {filename}")
            
            request = Request(url, 
                            data=json.dumps(data).encode('utf-8'),
                            headers=headers,
                            method='PUT')
            response = urlopen(request)
            success = response.status == 200 or response.status == 201
            print(f"{'Successfully' if success else 'Failed to'} {'updated' if sha else 'created'} the file")
            return success
            
        except Exception as e:
            print(f"Error creating post: {str(e)}")
            print(f"Request details:")
            print(f"URL: {url}")
            return False 