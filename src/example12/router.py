import httpx
from fastapi import FastAPI, Request, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import json
from urllib.parse import parse_qs, unquote

router = APIRouter(
    tags=["Vidjet"],
)
templates = Jinja2Templates(directory="templates")

BITRIX24_API_URL = "https://b24-r7ve9v.bitrix24.ru/rest/1/47141xo4txiasuro/"

def display_value(value):
    if isinstance(value, list):
        return ', '.join(map(str, value))
    return str(value)

@router.post("/read_root", response_class=HTMLResponse)
async def read_root(request: Request):

    body = await request.body()
    body_str = body.decode('utf-8')
    print(body_str)

    parsed_body = parse_qs(body_str)

    placement_options_encoded = parsed_body.get('PLACEMENT_OPTIONS', [''])[0]
    placement_options_str = unquote(placement_options_encoded)

    placement_options = json.loads(placement_options_str)
    contact_id = placement_options.get('ID')

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BITRIX24_API_URL}crm.contact.get", params={"ID": contact_id})
        contact = response.json()

    return templates.TemplateResponse("index.html", {"request": request, "contact": contact["result"], "display_value": display_value})
