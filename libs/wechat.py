import xml.etree.ElementTree as ET
from datetime import datetime

class WeChatMessage:
    def __init__(self, xml_data):
        root = ET.fromstring(xml_data)
        self.msg_type = root.find('MsgType').text
        self.content = root.find('Content').text
        self.from_user = root.find('FromUserName').text
        self.create_time = int(root.find('CreateTime').text)

    def format_post(self):
        # 将消息转换为博客文章格式
        lines = self.content.split('\n', 1)
        title = lines[0]
        content = lines[1] if len(lines) > 1 else ''
        
        return {
            'title': title,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'content': content
        } 