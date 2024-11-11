from typing import Optional

from fastapi import FastAPI, Request, APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from jinja2 import Template

from sdk.crest import CRest

router = APIRouter(
    tags=["sdk"]
)

@router.head("/install_app", response_class=HTMLResponse)
async def install_app_post(request: Request):
    request_data = await request.json()
    result = CRest.install_app(request_data)

    if not result['rest_only']:
        html_template = '''
        <!doctype html>
        <html lang="en">
        <head>
            <script src="//api.bitrix24.com/api/v1/"></script>
            {% if result.install %}
            <script>
                BX24.init(function(){
                    BX24.installFinish();
                });
            </script>
            {% endif %}
        </head>
        <body>
            {% if result.install %}
                <p>Installation has been finished</p>
            {% else %}
                <p>Installation error</p>
            {% endif %}
        </body>
        </html>
        '''
        template = Template(html_template)
        return HTMLResponse(content=template.render(result=result))
    else:
        return HTMLResponse(content="Installation only available through REST API.")

@router.post("/install_app", response_class=HTMLResponse)
async def install_app_post(request: Request):
    request_data = await request.json()
    result = CRest.install_app(request_data)


    if not result['rest_only']:
        html_template = '''
        <!doctype html>
        <html lang="en">
        <head>
            <script src="//api.bitrix24.com/api/v1/"></script>
            {% if result.install %}
            <script>
                BX24.init(function(){
                    BX24.installFinish();
                });
            </script>
            {% endif %}
        </head>
        <body>
            {% if result.install %}
                <p>Installation has been finished</p>
            {% else %}
                <p>Installation error</p>
            {% endif %}
        </body>
        </html>
        '''
        template = Template(html_template)
        return HTMLResponse(content=template.render(result=result))
    else:
        return HTMLResponse(content="Installation only available through REST API.")