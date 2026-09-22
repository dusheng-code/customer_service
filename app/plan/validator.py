from typing import List

from app.domain.state import DialogueState
from app.plan.turn_plan import TurnPlan, TurnPlanValidationResult, ClarifyReason
from app.knowledge.intents import KNOWLEDGE_INTENTS
from app.task.command.models import StartFlowCommand, SetSlotsCommand, CancelFlowCommand, ResumeFlowCommand
from app.task.flow.models import FlowsList

# 执行计划校验
class TurnPlanValidator:
    def validate(self,
                 state:DialogueState,
                 turn_plan:TurnPlan,
                 flows:FlowsList)->TurnPlanValidationResult:
        # 1 获取前一步意图识别内容轨道
        # active_tracks类型列表，因为识别轨道可能有多个
        active_tracks = self._active_tracks(turn_plan)

        # 2 如果意图识别内容没有轨道， 返回false和失败信息
        if not active_tracks:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_TRACK
            )

        #3 如果有轨道，判断是否多个轨道
        # 3.1 如果多个轨道，返回校验失败和失败信息
        if len(active_tracks) > 1:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MULTIPLE_TRACKS
            )
        #3.2 只有一个轨道，根据轨道类型，对不同轨道进一步校验
        active_track = active_tracks[0]
        #4 task任务轨道检验，成功返回true,失败：返回false和失败信息
        if active_track == 'task':
            return self._validate_task_track(turn_plan,flows)

        #5 knowledge 轨道校验：意图非法或缺少必要聚焦对象时，提前返回澄清
        if active_track == "knowledge":
            return self._validate_knowledge_track(state,turn_plan)
        #6 chitchat 轨道校验
        if active_track == "chitchat":
            return self._validate_chitchat_track(turn_plan)
        # 兜底：未知单轨道不静默放行，返回澄清
        return TurnPlanValidationResult(
            valid=False,
            reason=ClarifyReason.MISSING_TRACK
        )

    #从TurnPlan获取轨道
    def _active_tracks(self,turn_plan:TurnPlan)->List[str]:
        active_tracks:List[str] = []
        if turn_plan.task is not None:
            active_tracks.append("task")
        if turn_plan.knowledge is not None:
            active_tracks.append("knowledge")
        if turn_plan.chitchat is not None:
            active_tracks.append("chitchat")
        return active_tracks

    #对任务流程意图识别内容，进一步校验
    def _validate_task_track(self,turn_plan:TurnPlan,
                             flows:FlowsList)->TurnPlanValidationResult:
        #todo 校验规则是自定义的，根据实际需求自己定
        #校验1：turn_plan是否存在 commands
        task_turn = turn_plan.task
        if not task_turn.commands:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_TASK_COMMANDS
            )
        #校验2：command 值必须在四个中的某一个
        allowed = (StartFlowCommand,SetSlotsCommand,
                   CancelFlowCommand,ResumeFlowCommand)
        #all()
        if not all(isinstance(cmd,allowed)
                            for cmd in task_turn.commands):
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.INVALID_TASK_COMMANDS
            )
        #校验3：是否存在多个 开启流程命令 start_flow
        #start_flow_cmd列表
        start_flow_cmd = [cmd for cmd in task_turn.commands
                          if isinstance(cmd,StartFlowCommand)]
        if len(start_flow_cmd)>1:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MULTIPLE_TASK_FLOWS
            )

        # 校验4：判断开启流程具体流程id 在所有流程是否存在
        if start_flow_cmd:
            flow_id = start_flow_cmd[0].flow
            flow = flows.get_flow_by_id(flow_id)
            if flow is None:
                return TurnPlanValidationResult(
                    valid=False,
                    reason= ClarifyReason.UNKNOWN_TASK_FLOW
                )
        return TurnPlanValidationResult(valid=True)

    #对知识咨询轨道做校验：无意图或缺少必要聚焦对象时，返回澄清
    def _validate_knowledge_track(self,state:DialogueState,
                                  turn_plan:TurnPlan)->TurnPlanValidationResult:
        knowledge_turn = turn_plan.knowledge
        intents = knowledge_turn.intents if knowledge_turn is not None else []
        #校验1：没有任何知识意图
        if not intents:
            return TurnPlanValidationResult(
                valid=False,
                reason=ClarifyReason.MISSING_KNOWLEDGE_INTENT
            )
        focused = state.focused_object
        for intent_id in intents:
            intent = KNOWLEDGE_INTENTS.get(intent_id)
            if intent is None:
                continue
            required_object = intent.requires_object
            #校验2：该意图需要聚焦对象，但当前没有或类型不匹配
            if required_object and (focused is None or focused.type != required_object):
                return TurnPlanValidationResult(
                    valid=False,
                    reason=ClarifyReason.MISSING_FOCUSED_OBJECT
                )
        return TurnPlanValidationResult(valid=True)

    #对闲聊轨道做校验：闲聊无额外前置要求，直接通过（预留后续规则扩展点）
    def _validate_chitchat_track(self,turn_plan:TurnPlan)->TurnPlanValidationResult:
        return TurnPlanValidationResult(valid=True)