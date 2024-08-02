from fastapi import APIRouter, HTTPException
import httpx
import csv
from config import WEBHOOK_KEY
import os


router = APIRouter(
    tags=["Import"]
)


BITRIX24_API_URL = f"https://b24-r7ve9v.bitrix24.ru/rest/1/{WEBHOOK_KEY}"


def csv_to_dict_list(file_path, delimiter):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        return [row for row in reader]


@router.post("/upload_clients/")
async def upload_clients():

    file_path = os.path.join(os.path.dirname(__file__), 'many_clients.csv')

    clients = csv_to_dict_list(file_path, ';')

    if not clients:
        raise HTTPException(status_code=400, detail="Error reading CSV file or file is empty")

    batch_size = 50
    total_clients = len(clients)
    steps = (total_clients // batch_size) + (1 if total_clients % batch_size > 0 else 0)

    print(f"Total clients: {total_clients}")
    print(f"Total steps: {steps}")

    async with httpx.AsyncClient() as client:
        for step in range(steps):
            batch = {}
            start_idx = step * batch_size
            end_idx = min(start_idx + batch_size, total_clients)

            for relative_idx in range(start_idx, end_idx):
                client_data = clients[relative_idx]
                cmd_key = f"cmd{relative_idx - start_idx + 1}"
                batch[cmd_key] = (
                    "crm.contact.add?"
                    f"FIELDS[NAME]={client_data['NAME']}&"
                    f"FIELDS[LAST_NAME]={client_data['LAST_NAME']}&"
                    f"FIELDS[EMAIL][0][VALUE]={client_data['EMAIL']}&"
                    f"FIELDS[EMAIL][0][VALUE_TYPE]=WORK&"
                    f"FIELDS[PHONE][0][VALUE]={client_data['PHONE']}&"
                    f"FIELDS[PHONE][0][VALUE_TYPE]=WORK"
                )

            print(f"Batch for step {step + 1}")

            response = await client.post(
                f"{BITRIX24_API_URL}/batch",
                json={'cmd': batch}
            )

            print(f"Response status code for step {step + 1}: {response.status_code}")

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Error in Bitrix24 API call: {response.text}")

            result = response.json()

            print(result)
            print(f"Response JSON for step {step + 1}: ")

            if 'error' in result:
                raise HTTPException(status_code=400, detail=result['error'])

            if 'result' in result:
                if result['result']['result_error'] != []:
                    raise HTTPException(status_code=400, detail=f"Bitrix24 API error: {result['result']['result_error']}")\

            if not result['result']:
                raise HTTPException(status_code=400, detail="No results returned from Bitrix24 API.")

    return {"message": "Clients uploaded successfully"}

async def get_all_contacts():
    start = 0
    contacts = []
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"{BITRIX24_API_URL}/crm.contact.list",
                params={
                    'start': start,
                    'filter': [],
                    'select': ['ID']
                }
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Error fetching contacts: {response.text}")

            result = response.json()
            contacts.extend(result.get("result", []))

            if 'next' in result:
                start = result['next']
            else:
                break

    return contacts



@router.delete("/delete_all_contacts")
async def delete_all_contacts():
    contacts = await get_all_contacts()
    if not contacts:
        return {"message": "No contacts found"}

    batch_size = 50
    total_contacts = len(contacts)
    steps = (total_contacts // batch_size) + (1 if total_contacts % batch_size > 0 else 0)

    print(f"Total contacts: {total_contacts}")
    print(f"Total steps: {steps}")

    async with httpx.AsyncClient() as client:
        for step in range(steps):
            batch = {}
            start_idx = step * batch_size
            end_idx = min(start_idx + batch_size, total_contacts)

            for relative_idx in range(start_idx, end_idx):
                contact_id = contacts[relative_idx]['ID']
                cmd_key = f"cmd{relative_idx - start_idx + 1}"
                batch[cmd_key] = f"crm.contact.delete?id={contact_id}"

            print(f"Batch for step {step + 1}")

            response = await client.post(
                f"{BITRIX24_API_URL}/batch",
                json={'cmd': batch}
            )

            print(f"Response status code for step {step + 1}: {response.status_code}")

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Error in Bitrix24 API call: {response.text}")

            result = response.json()

            print(result)
            print(f"Response JSON for step {step + 1}: {result}")

            if 'error' in result:
                raise HTTPException(status_code=400, detail=result['error'])

            if 'result' in result and result['result']['result_error'] != []:
                raise HTTPException(status_code=400, detail=f"Bitrix24 API error: {result['result']['result_error']}")

            if not result['result']:
                raise HTTPException(status_code=400, detail="No results returned from Bitrix24 API.")

    return {"message": "All contacts deleted successfully"}