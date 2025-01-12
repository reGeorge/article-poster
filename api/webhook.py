from http.client import HTTPException
from libs.wechat import WeChatMessage
from libs.github_api import GitHubAPI
from libs.utils import validate_signature

async def handler(request):
    # 处理GET请求（微信服务器验证）
    if request.method == 'GET':
        query = request.query
        if validate_signature(query):
            return Response(query.get('echostr', ''))
        return Response('Invalid signature', status_code=403)
    
    # 处理POST请求（接收消息）
    if request.method == 'POST':
        try:
            message = WeChatMessage(await request.body())
            if message.msg_type == 'text':
                github = GitHubAPI()
                await github.create_post(message.format_post())
                return Response('success')
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return Response('success')  # 总是返回success避免微信服务器重试
            
    return Response('Method not allowed', status_code=405) 