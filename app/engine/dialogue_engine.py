"""
@Author:du_sheng
@Desc:
"""
import time

from app.domain.messages import UserMessage, ProcessResult, BotMessage, MessageType
from app.domain.state import DialogueState, FocusedObject
from app.plan.turn_planner import TurnPlanner
from app.plan.validator import TurnPlanValidator
from app.task.handler import TaskHandler, KnowledgeHandler, ChitchatHandler


class DialogueEngine:
    def __init__(
            self,
            turn_planner: TurnPlanner,
            task_handler: TaskHandler,
            knowledge_handler: KnowledgeHandler,
            chitchat_handler: ChitchatHandler,
            #clarify_responder: ClarifyResponder,
            turn_plan_validator: TurnPlanValidator
    ) -> None:
        self.turn_planner = turn_planner
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chitchat_handler = chitchat_handler
        #self.clarify_responder = clarify_responder
        self.turn_plan_validator = turn_plan_validator
        
    async def process_message(self,state:DialogueState,user_message:UserMessage)->ProcessResult:
        #1.准备会话
        self._prepare_session(state)
        #2.开启本轮 turn
        self._begin_turn(state,user_message)
        #3.按消息类型分流
        if user_message.type is MessageType.TEXT:
            messages= await self._handle_text_msg(state,user_message)
        else:
            #对象消息（暂时不实现）
            messages=await self._handle_object_message(state,user_message)
        #4.把本轮回复写入turn，并提交
        state.pending_turn.bot_messages.extend(messages)
        state.commit_turn()
        #5.组装返回结果
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=messages
        )

    def _prepare_session(self, state:DialogueState)->None:
        session=state.current_session()
        now=time.time()
        if session is None:
            state.start_session()
            return
        if now-session.last_activity_at>=60*60:
            state.close_current_session()
            state.reset_runtime_state_for_new_session()
            state.start_session()
        else:
            session.last_activity_at = now

    @staticmethod
    def _begin_turn(state: DialogueState, user_message: UserMessage) -> None:
        state.begin_turn(user_message)

    # 3 处理文本类型消息
    def _hande_text_msg(self):
        # 1 调用TurnPlanner方法意图识别
        ## 构建提示词，调用LLM，得到执行哪条轨道 （任务流程、知识查询、闲聊）
        # 2 调用TurnPlanValidator校验
        # 3 如果校验通过，调用对应处理器执行消息处理
        # 处理器包含： 任务流程、知识查询、闲聊、反问澄清
        pass

    # 处理对象类型消息
    def handle_object_msg(self):
        pass
