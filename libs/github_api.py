import os
import base64
import json
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import urllib.parse

def log(message):
    """统一的日志打印方法"""
    print(f"[GitHubAPI] {message}")

class GitHubAPI:
    def __init__(self):
        """初始化 GitHub API"""
        log("初始化 GitHub API...")
        self.token = os.environ.get('GITHUB_TOKEN')
        self.repo = os.environ.get('GITHUB_REPO')
        self.owner = os.environ.get('GITHUB_OWNER')
        self.branch = os.environ.get('GITHUB_BRANCH', 'master')
        
        # 只打印非敏感的配置信息
        log("GitHub Configuration:")
        log(f"Owner: {self.owner}")
        log(f"Repo: {self.repo}")
        log(f"Branch: {self.branch}")
        log("GitHub API 初始化完成")
        
    def get_file_sha(self, path):
        """获取文件的 SHA"""
        log(f"正在获取文件 SHA: {path}")
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            log("发送 GET 请求获取文件信息...")
            request = Request(url, headers=headers)
            response = urlopen(request)
            data = json.loads(response.read().decode('utf-8'))
            sha = data.get('sha')
            log(f"成功获取文件 SHA: {sha}")
            return sha
        except HTTPError as e:
            if e.code == 404:
                # 文件不存在，这是正常的情况
                log(f"文件 {path} 不存在，将创建新文件")
                return None
            else:
                log(f"HTTP 错误: {e.code} - {e.reason}")
                return None
        except Exception as e:
            log(f"获取文件 SHA 时发生错误: {str(e)}")
            return None
        
    def create_post(self, post_data):
        """创建或更新文章"""
        log("开始创建/更新文章...")
        if not post_data:
            log("文章数据为空，取消操作")
            return False
            
        try:
            # 使用固定的测试文件名
            filename = "source/_posts/test-post.md"
            log(f"使用文件名: {filename}")
            
            # 生成文章内容
            log("生成文章内容...")
            content = f"""---
title: {post_data['title']}
date: {time.strftime('%Y-%m-%d %H:%M:%S')}
---

{post_data['content']}
"""
            # 确保内容是 UTF-8 编码
            log("对内容进行 UTF-8 编码...")
            content_bytes = content.encode('utf-8')
            
            # 创建文件
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{filename}"
            
            # 打印请求 URL（调试用）
            log(f"请求 URL: {url}")
            
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json; charset=utf-8'
            }
            
            # 获取文件的 SHA（如果文件已存在）
            log("检查文件是否已存在...")
            sha = self.get_file_sha(filename)
            
            data = {
                'message': f'Update test post: {post_data["title"]}',
                'content': base64.b64encode(content_bytes).decode('utf-8'),
                'branch': self.branch
            }
            
            # 如果文件已存在，添加 SHA
            if sha:
                log(f"更新已存在的文件: {filename}")
                data['sha'] = sha
            else:
                log(f"创建新文件: {filename}")
            
            log("发送 PUT 请求...")
            request = Request(url, 
                            data=json.dumps(data).encode('utf-8'),
                            headers=headers,
                            method='PUT')
            response = urlopen(request)
            success = response.status == 200 or response.status == 201
            log(f"{'成功' if success else '失败'} {'更新' if sha else '创建'}文件")
            return success
            
        except Exception as e:
            log(f"创建文章时发生错误: {str(e)}")
            log(f"请求详情:")
            log(f"URL: {url}")
            return False 