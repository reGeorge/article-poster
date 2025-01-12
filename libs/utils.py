import os
import hashlib

def validate_signature(query):
    """验证微信服务器签名"""
    token = os.environ.get('WECHAT_TOKEN')
    timestamp = query.get('timestamp', '')
    nonce = query.get('nonce', '')
    signature = query.get('signature', '')
    
    # 按字典序排序
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    
    # SHA1加密
    tmp_str = ''.join(tmp_list)
    hash_obj = hashlib.sha1(tmp_str.encode())
    
    return hash_obj.hexdigest() == signature 