from fastapi import Request, HTTPException, APIRouter
import time
import random
import json
from urllib.parse import parse_qs
import requests

from config import BOT_ID, CLIENT_ID



router = APIRouter(
    tags=["app"]
)




@router.post("/bot_answer")
async def handle_event(request: Request):
    body = await request.body()
    body_str = body.decode('utf-8')
    parsed_body = parse_qs(body_str)

    dialog_id = parsed_body['data[PARAMS][DIALOG_ID]'][0]
    message = f"reply: '{parsed_body['data[PARAMS][MESSAGE]'][0]}'"

    response = requests.post(
        'https://b24-9py8k8.bitrix24.com/rest/1/26shjpa7oin54uvn/imbot.message.add',
        json={
            'BOT_ID': BOT_ID,
            'CLIENT_ID': CLIENT_ID,
            'DIALOG_ID': dialog_id,
            'MESSAGE': message
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {"status": "success", "message": "Event processed"}



