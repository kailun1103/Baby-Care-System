import requests, json

# 替換為您的Channel Access Token
ACCESS_TOKEN = 'lHTtqayJe1MN429GbyJjmgrcWbIkUUZ9Rm2pnyHRsZU7mmED1S/dM0FVaqPpXq+uX/G1E3BBfL81xHI66sT+4Hl/DOMjKyVc5u8OwnYLczc5 /QdB04t89/1O/w1cDnyilFU='

headers = {
    'Authorization': 'Bearer ' + ACCESS_TOKEN, 
    'Content-Type':'application/json'
}

body = {
    'replyToken':'U4a2b6c651a48061d8408b40b25c03b3c',
    'messages':[
        {
            'type': 'text',
            'text': '幹你娘'
        }
    ]
}

req = requests.request('POST', 'https://api.line.me/v2/bot/message/push', headers=headers, data=json.dumps(body).encode('utf-8'))
print(req.status_code)
print(req.text)