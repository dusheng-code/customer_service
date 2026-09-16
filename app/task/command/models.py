from dataclasses import dataclass
from typing import Any


# {"command": "start_flow", "flow": "refund_request"}
@dataclass
class Command:
    command: str

    @classmethod
    def from_dict(cls, data: dict) -> "Command":
        clz = COMMAND_NAME_TO_CLASS.get(data["command"])
        if clz is not None:
            return clz(**data)
        return Command(command="unknown")

# 开始任务
# {"command": "start_flow", "flow": "refund_request"}
@dataclass
class StartFlowCommand(Command):
    flow: str

# 设置槽数据
# {"command": "set_slots", "slots": {"order_number": "10001"}}
@dataclass
class SetSlotsCommand(Command):
    slots: dict[str, Any]

# 取消
# {"command": "cancel_flow"}
@dataclass
class CancelFlowCommand(Command):
    pass

# 恢复
# {"command": "resume_task", "flow": "refund_request"}
@dataclass
class ResumeFlowCommand(Command):
    flow: str

COMMAND_NAME_TO_CLASS = {
    "start_flow": StartFlowCommand,
    "set_slots": SetSlotsCommand,
    "cancel_flow": CancelFlowCommand,
    "resume_flow": ResumeFlowCommand,
}
