import os
import base64
from datetime import datetime
import httpx

class GitHubAPI:
    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN')
        self.repo = os.environ.get('GITHUB_REPO')
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    async def create_post(self, post_data):
        # 生成文件名
        filename = f"source/_posts/{datetime.now().strftime('%Y%m%d')}_{post_data['title']}.md"
        
        # 生成文章内容
        content = f"""---
title: {post_data['title']}
date: {post_data['date']}
categories:
  - 博客
tags:
  - 随笔
---

{post_data['content']}
"""
        
        # 创建或更新文件
        url = f'https://api.github.com/repos/{self.repo}/contents/{filename}'
        data = {
            'message': f'Add post: {post_data["title"]}',
            'content': base64.b64encode(content.encode()).decode()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=data, headers=self.headers)
            response.raise_for_status() 