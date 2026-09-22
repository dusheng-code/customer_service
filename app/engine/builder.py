from pathlib import Path

from app.clarify.responder import ClarifyResponder
from app.engine.dialogue_engine import DialogueEngine
from app.plan.turn_planner import TurnPlanner
from app.plan.validator import TurnPlanValidator
from app.chitchat.handler import ChitChatHandler
from app.knowledge.handler import KnowLedgeHandler
from app.knowledge.intents import KNOWLEDGE_INTENTS
from app.knowledge.provider import (
    ProductAPIProvider,
    OrderAPIProvider,
    FAQProvider,
    RAGProvider,
)
from app.knowledge.registry import KnowledgeProviderRegistry
from app.knowledge.responder import KnowledgeResponder
from app.task.action.builder import build_action_runner
from app.task.command.process import CommandProcessor
from app.task.flow.executor import FlowExecutor
from app.task.flow.loader import FlowLoader
from app.task.handler import TaskHandler


# def build_dialogue_engine():
#     return DialogueEngine(
#         turn_planner=TurnPlanner(),
#         turn_plan_validator=TurnPlanValidator(),
#         task_handler=TaskHandler()
#     )

# 真正加载YAML
PROJECT_DIR = Path(__file__).resolve().parents[2]
FLOW_CONFIG_DIR = PROJECT_DIR / "flow_config"
FLOW_CONFIG_FILES = ["system_flows.yml", "user_flows.yml"]


def build_dialogue_engine():
    flow_list = FlowLoader().load_many(
           [FLOW_CONFIG_DIR / file_name
         for file_name in FLOW_CONFIG_FILES])

    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_plan_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponder(),
        chitchat_handler=ChitChatHandler(),
        knowledge_handler=KnowLedgeHandler(
            knowledge_intents=KNOWLEDGE_INTENTS,
            provider_registry=KnowledgeProviderRegistry([
                ProductAPIProvider(),
                OrderAPIProvider(),
                FAQProvider(),
                RAGProvider(),
            ]),
            knowledge_responder=KnowledgeResponder(),
        ),
        task_handler=TaskHandler(flow_list=flow_list,
               processor=CommandProcessor(),
            action_runner=build_action_runner(),
             flow_executor=FlowExecutor()))