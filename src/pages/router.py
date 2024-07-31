import httpx
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from config import WEBHOOK_KEY

router = APIRouter(
    tags=["Pages"],
    prefix="/form"
)

class ContactForm(BaseModel):
    name: str
    lastname: str
    phone: str


templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "submitted": False})

@router.post("/", response_class=HTMLResponse)
async def submit_form(request: Request, exampleInputName: str = Form(...), exampleInputLastName: str = Form(...), exampleInputPhone: str = Form(...)):
    form_data = ContactForm(name=exampleInputName, lastname=exampleInputLastName, phone=exampleInputPhone)

    WEBHOOK_URL = f"https://b24-r7ve9v.bitrix24.ru/rest/1/{WEBHOOK_KEY}/crm.contact.add.json"

    lead_data = {
        'fields': {
            'NAME': form_data.name,
            'LAST_NAME': form_data.lastname,
            'PHONE': [{
                'VALUE': form_data.phone,
                'VALUE_TYPE': 'work',
            }]
        },
        'params': {"REGISTER_SONET_EVENT": "Y"}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(WEBHOOK_URL, json=lead_data)
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "submitted": True,
        "name": form_data.name,
        "lastname": form_data.lastname,
        "phone": form_data.phone
    })


