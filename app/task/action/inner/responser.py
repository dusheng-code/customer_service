"""
@Author:du_sheng
@Desc:
"""
from typing import Any

from jinja2 import Template
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from app.domain.messages import BotMessage
from app.domain.state import DialogueState
from app.infrastructure.llm import llm
from app.prompts.history_builder import HistoryBuilder
from app.task.action.base import Action, ActionResult

#action_response类型的action
class ActionResponse(Action):
    name = "action_response"

    async def run(
            self,
            state:DialogueState,
            action_kwargs:dict[str,Any]
    ) -> ActionResult:
        #action_kwargs获取mode
        mode=action_kwargs.get('mode','static')
        #action_kwargs获取text
        text=action_kwargs['text']
        #文本渲染:把{order_num}替换具体
        ##订单号{{order_num}}状态是已经发货
        text_result=self.render_text(state, text)

        #根据不同Mode
        #static 不调用llm
        if mode=='static':
            return ActionResult(
                messages=[BotMessage(text=text_result)],
            )
        #rephrase 获取渲染文本，构建提示词, 调用llm 得到最终返回文本
        elif mode=='rephrase':
            #获取提示词
            prompt = action_kwargs['prompt']
            #调用llm
            result= await self._call_llm(state,prompt)
            return ActionResult(
                messages=[BotMessage(text=result)],
            )

    #调用llm方法
    async def _call_llm(self,state:DialogueState,
                  prompt:str,
                  render_text:str="")->str:
        #构建提示词
        prompt_template=PromptTemplate.from_template(prompt)
        #创建调用链
        chain = prompt_template | llm | StrOutputParser()
        #执行invoke
        result=await chain.ainvoke({
            "history":HistoryBuilder.build(
                state.current_session().turns[-5:]),
            "user_message":HistoryBuilder._render_user_message(
                            state.pending_turn.user_message),
            "current_response":render_text,
        })
        return result

    #渲染方法
    def render_text(self,state:DialogueState,text:str)->str:
        template=Template(text)
        result=template.render(
            slots=state.active_task.slots if state.active_task else {},
            context=state.active_system_task or state.active_task,
        )
        return result