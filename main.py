import os
import sys

from fastapi import Request, FastAPI, HTTPException

from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.exceptions import (InvalidSignatureError)
from linebot.v3.webhooks import (MessageEvent,TextMessageContent)
from google import genai
from dotenv import load_dotenv

load_dotenv()
# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if GEMINI_API_KEY is None:
    print('Specify GEMINI_API_KEY as environment variable.')

configuration = Configuration(
    access_token=channel_access_token
)

# 建立一個紀錄使用者資訊的字典
user_session = {}

client = genai.Client()

async_api_client = AsyncApiClient(configuration)

class LineService:
    def __init__(self, channel_secret, channel_access_token):
        self.parser = WebhookParser(channel_secret)
        self.async_api = AsyncMessagingApi(async_api_client)

    async def get_events(self, request:Request):
        signature = request.headers.get('X-Line-Signature')
        body = (await request.body()).decode()
        try:
            return self.parser.parse(body, signature)
        except InvalidSignatureError:
            raise HTTPException(status_code=400)
        
    async def reply_text(self, reply_token, gemini_reply_text):
        await self.async_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=gemini_reply_text)]
            )
        )

class Gemini_service:
    def __init__(self, user_id):
        self.user_id = user_id
        self.interaction_id = None
    def get_response(self, user_text):
        try:
            interaction = client.interactions.create(
            model = "gemini-3-flash-preview",
            input = f"請用繁體中文簡短回答以下問題:{user_text}",
            previous_interaction_id = self.interaction_id
            )
            self.interaction_id = interaction.id
            return(interaction.outputs[-1].text)
        except:
            return('抱歉，目前無法處理您的訊息，請稍後再試')

line_service = LineService(channel_secret, channel_access_token)

app = FastAPI()

@app.post("/callback")
async def handle_callback(request: Request):
    events = await line_service.get_events(request)
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue
        user_id = event.source.user_id
        user_text = event.message.text
        if user_id not in user_session:
            user_session[user_id] = Gemini_service(user_id)
        current_user = user_session[user_id]
        gemini_reply_text = current_user.get_response(user_text)
        await line_service.reply_text(event.reply_token, gemini_reply_text)
    return 'OK'