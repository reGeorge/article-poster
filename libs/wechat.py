import xml.etree.ElementTree as ET
from datetime import datetime

class WeChatMessage:
    def __init__(self, xml_data):
        """解析微信消息"""
        root = ET.fromstring(xml_data)
        self.msg_type = root.find('MsgType').text
        self.from_user = root.find('FromUserName').text
        self.to_user = root.find('ToUserName').text
        self.create_time = root.find('CreateTime').text
        
        # 根据消息类型获取内容
        if self.msg_type == 'text':
            self.content = root.find('Content').text
        
    def format_post(self):
        """格式化文章内容"""
        if self.msg_type != 'text':
            return None
            
        # 分割标题和内容
        lines = self.content.split('\n', 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ''
        
        return {
            'title': title,
            'content': content
        } 