import pytest
from libs.wechat import WeChatMessage
import hashlib

def test_wechat_message_parsing():
    xml_data = """
    <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[测试标题\n测试内容]]></Content>
        <MsgId>1234567890123456</MsgId>
    </xml>
    """
    
    message = WeChatMessage(xml_data.encode())
    assert message.msg_type == 'text'
    assert message.from_user == 'fromUser'
    
    post_data = message.format_post()
    assert post_data['title'] == '测试标题'
    assert post_data['content'] == '测试内容' 

def generate_test_signature(token, timestamp, nonce):
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    signature = hashlib.sha1(tmp_str.encode()).hexdigest()
    return signature

# 使用示例
token = "test_token"  # 替换为你的 WECHAT_TOKEN
timestamp = "1234567890"
nonce = "test123"
signature = generate_signature(token, timestamp, nonce)
print(f"signature={signature}&timestamp={timestamp}&nonce={nonce}") 