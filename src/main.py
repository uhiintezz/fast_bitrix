from typing import Annotated

import httpx
from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from config import WEBHOOK_KEY, APPLICATION_TOKEN

import requests
import os
import time
import random
from urllib.parse import parse_qs
from pages.router import router as router_pages


app = FastAPI()

app.include_router(router_pages)


class ContactAdd(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    email_type: str
    phone: str
    phone_type: str



class ContactUpdate(ContactAdd):
    contact_id: int

class DealUpdate(BaseModel):
    id: int
    stage_id: str
    closed: int = 1




@app.post("/add-contact")
async def create_lead(
        contact: Annotated[ContactAdd, Depends()]
):

    WEBHOOK_URL = f"https://b24-r7ve9v.bitrix24.ru/rest/1/{WEBHOOK_KEY}/crm.contact.add.json"

    lead_data = {
        'fields': {
            'NAME': contact.name,
            'LAST_NAME': contact.last_name,
            'EMAIL': [{
                'VALUE': contact.email,
                'VALUE_TYPE': contact.email_type,
            }],
            'PHONE': [{
                'VALUE': contact.phone,
                'VALUE_TYPE': contact.phone_type,
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




BITRIX24_DOMAIN = 'b24-r7ve9v.bitrix24.ru'


@app.post("/update-contact/")
async def update_contact(contact: ContactUpdate):
    update_data = {
        'fields': {
            'NAME': contact.name,
            'LAST_NAME': contact.last_name,
            'EMAIL': [{
                'VALUE': contact.email,
                'VALUE_TYPE': contact.email_type,
            }],
            'PHONE': [{
                'VALUE': contact.phone,
                'VALUE_TYPE': contact.phone_type,
            }]
        },
        'params': {"REGISTER_SONET_EVENT": "Y"}
    }

    # URL для обновления контакта через вебхук
    url = f'https://{BITRIX24_DOMAIN}/rest/1/{WEBHOOK_KEY}/crm.contact.update'

    # Параметры запроса
    params = {
        'ID': contact.contact_id,
        **update_data
    }


    # Отправка запроса
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=params)
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data:
                return {"error": response_data['error_description']}
            else:
                return {"result": response_data}
        else:
            return {"error": f"Ошибка при подключении к Bitrix24. Статус код: {response.status_code}"}




def log_event(data):
    dir_path = 'tmp/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    filename = f"{dir_path}{int(time.time())}_{random.randint(1, 9999)}.txt"
    with open(filename, 'w') as f:
        f.write(str(data))

@app.post("/update-contact2/")
async def update_contact(request: Request):
    print(request)
    body = await request.body()
    #print(f"Request body: {body}")
    body_str = body.decode('utf-8')
    print(body_str)
    try:
        body_str = body.decode('utf-8')
        req_data = {key: value[0] for key, value in parse_qs(body_str).items()}
        print(req_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid form data: {str(e)}")

    if not req_data.get('auth[application_token]') == APPLICATION_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid application token")

    if req_data.get('event') != 'ONCRMCONTACTUPDATE':
        raise HTTPException(status_code=400, detail="Invalid event type")

    contact_id = req_data.get('data[FIELDS][ID]')
    if not contact_id:
        raise HTTPException(status_code=400, detail="Contact ID not provided")

    get_contact_url = f"https://b24-r7ve9v.bitrix24.ru/rest/1/{WEBHOOK_KEY}/crm.contact.get.json?"
    response = requests.get(get_contact_url, params={'ID': contact_id})

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching contact data")

    contact_data = response.json()


    log_event({
        'result': contact_data,
        'request': req_data
    })

    return {"message": "Контакт успешно обновлен", "contact_data": contact_data}


@app.post("/update-deal/")
async def update_contact(deal: DealUpdate):
    update_data = {
        'fields': {
            "STAGE_ID": "PREPAYMENT_INVOICE",
            "ClOSED": '0'
        },
        'params': {"REGISTER_SONET_EVENT": "Y"}
    }

    # URL для обновления контакта через вебхук
    url = f'https://{BITRIX24_DOMAIN}/rest/1/{WEBHOOK_KEY}/crm.deal.update'

    # Параметры запроса
    params = {
        'ID': deal.id,
        **update_data
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=params)
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data:
                return {"error": response_data['error_description']}
            else:
                return {"result": response_data}
        else:
            return {"error": f"Ошибка при подключении к Bitrix24. Статус код: {response.status_code}"}



