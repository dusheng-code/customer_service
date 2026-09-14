"""
@Author:du_sheng
@Desc:
"""
from app.domain.messages import UserMessage, ProcessResult, BotMessage
from app.domain.state import DialogueState

class DialogueEngine:
    '''
    占位实现
    '''
    async def process_message(self,state:DialogueState,user_message:UserMessage)->ProcessResult:
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=[BotMessage(text="我已经接收到你的消息了")]
        )