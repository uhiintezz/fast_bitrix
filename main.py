from typing import Annotated

import httpx
from fastapi import FastAPI, Depends, APIRouter
from pydantic import BaseModel, EmailStr
from config import WEBHOOK_KEY


app = FastAPI()


class Lead(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    email_type: str
    phone: str
    phone_type: str





WEBHOOK_URL = f"https://b24-r7ve9v.bitrix24.ru/rest/1/{WEBHOOK_KEY}/crm.contact.add.json"

@app.post("/create-lead")
async def create_lead(
        lead: Annotated[Lead, Depends()]
):

    lead_data = {
        'fields': {
            'NAME': lead.name,
            'LAST_NAME': lead.last_name,
            'EMAIL': [{
                'VALUE': lead.email,
                'VALUE_TYPE': lead.email_type,
            }],
            'PHONE': [{
                'VALUE': lead.phone,
                'VALUE_TYPE': lead.phone_type,
            }]
        },
        'params': {"REGISTER_SONET_EVENT": "Y"}
    }


    async with httpx.AsyncClient() as client:
        response = await client.post(WEBHOOK_URL, json=lead_data)
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data:
                return {"error": response_data['error_description']}
            else:
                return {"result": response_data}
        else:
            return {"error": f"Ошибка при подключении к Bitrix24. Статус код: {response.status_code}"}
