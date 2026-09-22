"""
@Author:du_sheng
@Desc:
"""
from typing import Dict, Any

from app.domain.state import DialogueState
from app.knowledge.intents import KnowledgeIntent, KNOWLEDGE_INTENTS
from app.knowledge.provider import KnowledgeChunk
from app.knowledge.registry import KnowledgeProviderRegistry
from app.knowledge.responder import KnowledgeResponder
from app.domain.messages import BotMessage

class KnowLedgeHandler:

    def __init__(self,
                 knowledge_intents:Dict[str,KnowledgeIntent],
                 provider_registry:KnowledgeProviderRegistry,
                 knowledge_responder:KnowledgeResponder):
        self.knowledge_intents=knowledge_intents
        self.provider_registry=provider_registry
        self.knowledge_responder=knowledge_responder

    # 1 获取意图识别结果
    # ["product_info","order_info","refund_policy","return_policy"]

    # 2 根据意图识别结果，获取问题到什么地方找到答案(去重处理)
    # ["api.product", "api.order" ,"faq.default", "rag.default"]

    # 3 根据答案位置，找到对应对象，执行的结果（答案）

    # 4 把上一步获取那些答案 构建提示词，调用LLM得到最终答案
    async def handler(self,state:DialogueState,
                     knowledge_intents:list[str])->list[BotMessage]:
        # 1 获取knowledge_intents是llm意图识别列表
        # ["product_info","order_info","refund_policy","return_policy"]

        # 2 根据意图识别结果，获取问题到什么地方找到答案(去重处理)
        # ["api.product", "api.order" ,"faq.default", "rag.default"]
        provier_ids:list[str] = self._get_provider_ids(knowledge_intents)

        # 3 根据答案位置，找到对应对象，执行的结果（答案）
        final_result:list[KnowledgeChunk] = []
        for provier_id in provier_ids:
            provider_obj = self.provider_registry.get(provier_id)
            result = await provider_obj.retrieve(state)
            final_result.extend(result)

        # 4 把上一步获取那些答案 构建提示词，调用LLM得到最终答案
        response = await self.knowledge_responder.respond(
            user_message=state.pending_turn.user_message,
            recent_turns=state.current_session().turns[-5:],
            chunks=final_result)
        return response

    # ["product_info","order_info","refund_policy","return_policy"]
    def _get_provider_ids(self,
                          knowledge_intents:list[str])->list[str]:
        final_provider_ids:list[str] = []
        for intent in knowledge_intents:
            intent_obj = KNOWLEDGE_INTENTS.get(intent)
            if intent_obj is None:
                # LLM 可能返回未注册的意图，跳过以避免 KeyError 崩溃
                continue
            final_provider_ids.extend(
                intent_obj.provider_ids)
        # (去重处理)
        return list(set(final_provider_ids))

