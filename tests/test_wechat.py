import pytest
from libs.wechat import WeChatMessage

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