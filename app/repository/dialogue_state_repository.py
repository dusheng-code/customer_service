"""
@Author:du_sheng
@Desc:
"""
import json

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.state import DialogueState
from app.models import dialogue_state
from app.models.dialogue_state import DialogueStateRecord

class DialogueStateRepository:
    def __init__(self,session:AsyncSession):
        self.session=session

async def load_state(self,sender_id:str)-> DialogueState:
    sql=select(DialogueStateRecord).where(
        DialogueStateRecord.sender_id==sender_id
    )
    result= await self.session.execute(sql)
    state=result.scalar_one_or_none()
    if state:
        #将state.state_json按序列化成一个DialogueState对象
        dialogue_state:DialogueState = DialogueState.from_dict(
            json.loads(state.state_json)
        )
        return dialogue_state
    else:
        return DialogueState(sender_id=sender_id)

async def save_state(self,state:DialogueState):
    #将state序列化为一个json 字符串
    state_json:str = json.dumps(state.to_dict())
    insert_stmt=insert(DialogueStateRecord).values(
        sender_id=state.sender_id,state_json=state_json
    )
    upsert_stmt=insert_stmt.on_duplicate_key_update(
        state_json=insert_stmt.inserted.state_json
    )
    await self.session.execute(upsert_stmt)
    await self.session.commit()