"""
@Author:du_sheng
@Desc:
"""
from app.config.config import settings
from app.infrastructure import http_client

#方法:获取中台系统id+端口号信息
#http://127.0.0.1:18081/orders/A20260408002/logistics
def _get_base_url()->str:
    return settings.commerce_api_base_url

#根据订单id查询物流信息
async def get_logistics(order_id:str)->dict:
    try:
        result=await http_client.http_client.get(f"{_get_base_url()}/"
                                     f"orders/{order_id}/logistics")
        result_json=result.json()
        data=result_json.get("data")
        return data
    except Exception as error:
        raise Exception(error)