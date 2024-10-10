from fastapi import Request, HTTPException, APIRouter
import time
import random
import json
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import parse_qs
import requests

from config import BOT_ID, CLIENT_ID

load_dotenv()

router = APIRouter(
    tags=["bot"]
)

TMP_DIR = Path("tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/bot_answer")
async def handle_event(request: Request):
    body = await request.body()
    body_str = body.decode('utf-8')
    parsed_body = parse_qs(body_str)

    if 'event' not in parsed_body or parsed_body['event'][0] not in ['ONIMBOTJOINCHAT', 'ONIMBOTMESSAGEADD']:
        raise HTTPException(status_code=400, detail="Invalid event")

    timestamp = time.time()
    random_number = random.randint(1, 9999)
    log_file = TMP_DIR / f"{int(timestamp)}_{random_number}.txt"

    with log_file.open("w") as f:
        f.write(json.dumps({
            'request': {
                'event': parsed_body['event'][0],
                'data': parsed_body['data[PARAMS][MESSAGE]'][0],
                'ts': parsed_body['ts'][0],
                'auth': parsed_body['auth[member_id]'][0]
            }
        }, indent=4))

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