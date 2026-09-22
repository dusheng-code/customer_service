import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.infrastructure.llm import llm
from app.plan.turn_plan import ClarifyReason
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt


# 反问澄清
class ClarifyResponder:

    async def respond(
            self,
            state: DialogueState,
            reason: ClarifyReason,
    ) -> list[BotMessage]:
        # 1 找到提示词需要那些数据
        # 根据传递过来原因，调用方法返回对应中文回复
        clarify_message = (
            self.build_clarify_message(reason=reason,state=state))

        # 历史记录
        history_str = HistoryBuilder.build(state.current_session().turns[-10:])

        # focused_object
        focused_object_str = json.dumps(state.focused_object.to_dict() if state.focused_object is not None else None, ensure_ascii=False)

        user_message_str = json.dumps(state.pending_turn.user_message.to_dict(), ensure_ascii=False)

        # 2 加载提示词模版
        prompt_text = load_prompt("clarify_respond")
        prompt_template = PromptTemplate.from_template(
                                     template=prompt_text,
                                     template_format="jinja2")

        # 3 根据提示词调用llm得到结果
        chain = prompt_template | llm | StrOutputParser()
        result = await chain.ainvoke(
            {
                "history":history_str,
                "focused_object":focused_object_str,
                "clarify_message":clarify_message,
                "reason":reason.value,
                "user_message":user_message_str
            }
        )
        return [BotMessage(text=result)]


    def build_clarify_message(self,
                              reason: ClarifyReason,
                              state: DialogueState,
                              ) -> str:
        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办业务还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_FOCUSED_OBJECT:
            return "请先发送你想咨询的商品或订单，我再继续帮你看。"

        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return "你是想了解商品信息、订单信息，还是售后配送规则呢？"

        if reason is ClarifyReason.MISSING_TRACK:
            return "你是想先处理业务问题，还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return "你这次是想办理什么业务呢？比如查订单、查物流，或者申请退款。"

        if reason is ClarifyReason.OBJECT_REQUIRES_INTENT:
            focused_object = state.focused_object
            if focused_object is not None and focused_object.type == "order":
                return "我已经收到这个订单了。你想查订单状态、查物流，还是申请退款呢？"
            if focused_object is not None and focused_object.type == "product":
                return "我已经收到这个商品了。你想了解它的商品信息、发货情况，还是售后相关问题呢？"

        return "我还需要再确认一下你的意思，你可以换个更具体的说法告诉我。"