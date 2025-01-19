import hashlib

def generate_test_signature(token, timestamp, nonce):
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    signature = hashlib.sha1(tmp_str.encode()).hexdigest()
    return signature

# 测试参数
token = "mytoken"          # 这应该和你的 WECHAT_TOKEN 环境变量值一致
timestamp = "1704891234"   # 一个时间戳
nonce = "randomstring123"  # 一个随机字符串
echostr = "hello"          # 回显字符串

# 生成签名
signature = generate_test_signature(token, timestamp, nonce)

# 打印完整的测试 URL
print("\n测试 URL:")
print(f"http://localhost:3000/api/webhook?signature={signature}&timestamp={timestamp}&nonce={nonce}&echostr={echostr}")

# 打印 curl 命令
print("\ncurl 命令:")
print(f'curl "http://localhost:3000/api/webhook?signature={signature}&timestamp={timestamp}&nonce={nonce}&echostr={echostr}"')

# 打印参数值（用于调试）
print("\n参数值:")
print(f"signature: {signature}")
print(f"timestamp: {timestamp}")
print(f"nonce: {nonce}")
print(f"echostr: {echostr}")