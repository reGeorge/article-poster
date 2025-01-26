import xml.etree.ElementTree as ET
from datetime import datetime

def log(message):
    """统一的日志打印方法"""
    print(f"[WeChatMessage] {message}")

class WeChatMessage:
    def __init__(self, xml_data):
        """解析微信消息"""
        log("开始解析微信消息...")
        try:
            root = ET.fromstring(xml_data)
            
            # 清理文本内容，去除多余的空白字符和换行符
            def clean_text(element):
                if element is None:
                    return ''
                return element.text.strip() if element.text else ''
            
            self.msg_type = clean_text(root.find('MsgType'))
            self.from_user = clean_text(root.find('FromUserName'))
            self.to_user = clean_text(root.find('ToUserName'))
            self.create_time = clean_text(root.find('CreateTime'))
            
            log(f"消息类型: {self.msg_type}")
            log(f"发送者: {self.from_user}")
            log(f"接收者: {self.to_user}")
            
            # 根据消息类型获取内容
            if self.msg_type == 'text':
                self.content = root.find('Content').text
                log(f"消息内容: {self.content[:100]}...")  # 只打印前100个字符
            else:
                log(f"不支持的消息类型: {self.msg_type}")
                
            log("微信消息解析完成")
            
        except ET.ParseError as e:
            log(f"XML解析错误: {str(e)}")
            raise
        except AttributeError as e:
            log(f"消息格式错误,缺少必要字段: {str(e)}")
            raise
        except Exception as e:
            log(f"解析消息时发生未知错误: {str(e)}")
            raise
        
    def format_post(self):
        """格式化文章内容"""
        log("开始格式化文章内容...")
        try:
            if self.msg_type != 'text':
                log("非文本消息,无法格式化")
                return None
                
            # 分割标题和内容
            lines = self.content.split('\n', 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ''
            
            log(f"标题: {title}")
            log(f"内容长度: {len(content)} 字符")
            
            formatted = {
                'title': title,
                'content': content
            }
            log("文章格式化完成")
            return formatted
            
        except Exception as e:
            log(f"格式化文章时发生错误: {str(e)}")
            return None