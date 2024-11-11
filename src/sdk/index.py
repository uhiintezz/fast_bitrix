from sdk.crest import CRest
from fastapi import APIRouter
import pprint

router = APIRouter(
    tags=["profile"]
)

@router.head("/profile")
async def get_profile():
    print('index')
    result = CRest.call('profile', {})
    #
    pprint.pprint(result)

@router.post("/profile")
async def get_profile():
    print('index')
    result = CRest.call('profile', {})
    pprint.pprint(result)
    return result
