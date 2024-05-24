from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
line_bot_api = LineBotApi('lHTtqayJe1MN429GbyJjmgrcWbIkUUZ9Rm2pnyHRsZU7mmED1S/dM0FVaqPpXq+uX/G1E3BBfL81xHI66sT+4Hl/DOMjKyVc5u8OwnYLczc5 /QdB04t89/1O/w1cDnyilFU=')
line_bot_api.push_message('U4a2b6c651a48061d8408b40b25c03b3c', TextSendMessage(text='Hello World!!!'))