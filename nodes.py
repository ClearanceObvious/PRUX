from enum import Enum
from dataclasses import dataclass
from ttoken import TokenType
import sys

class NodeType(Enum):
    NOP = -3
    NewLineNode = -2
    ImportNode = -1

    NumberNode = 0

    StringNode = 1
    FStringNode = 1
    
    BooleanNode = 2
    NullNode = 3

    BinOpNode = 4
    UnOpNode = 5

    EqNode = 6
    CondNode = 7

    VarCreateNode = 8
    VarAccessNode = 9
    VarOverrideNode = 10

    ArrayNode = 11
    ObjectNode = 12

    IndexNode = 13
    DataStructOverrideNode = 14

    FunctionNode = 15
    FunctionCallNode = 16
    ReturnNode = 17

    IfStatementNode = 18
    ForLoopNode = 19
    WhileLoopNode = 20
    BreakNode = 21

    BaseGlobalLog = 22
    BaseGlobalSleep = 23
    BaseGlobalTime = 24


@dataclass
class Node:
    type: NodeType
    value: any = 0

    def __hash__(self):
        return self.type.value

class BinOpNode(Node):
    def __init__(self, left: Node, op: TokenType, right: Node):
        super().__init__(NodeType.BinOpNode, 0)
        self.left = left
        self.op = op
        self.right = right

class UnOpNode(Node):
    def __init__(self, node: Node):
        super().__init__(NodeType.UnOpNode, 0)
        self.node = node

class CondNode(Node):
    def __init__(self, left: Node, op: Node, right: Node):
        super().__init__(NodeType.CondNode, 0)
        self.left = left
        self.right = right
        self.op = op

class VarCreateNode(Node):
    def __init__(self, name: str, value: Node):
        super().__init__(NodeType.VarCreateNode, 0)
        self.name = name
        self.value = value

class VarAccessNode(Node):
    def __init__(self, name: str):
        super().__init__(NodeType.VarAccessNode, 0)
        self.name = name

class VarOverrideNode(Node):
    def __init__(self, name: str, value: Node):
        super().__init__(NodeType.VarOverrideNode, 0)
        self.name = name
        self.value = value

class ArrayNode(Node):
    def __init__(self, value: dict):
        super().__init__(NodeType.ArrayNode, 0)
        self.value = value

class ObjectNode(Node):
    def __init__(self, value: dict):
        super().__init__(NodeType.ObjectNode, 0)
        self.value = value

class DataStructOverrideNode(Node):
    def __init__(self, name: str, path: list, val: Node):
        super().__init__(NodeType.DataStructOverrideNode, 0)
        self.name = name
        self.path = path
        self.value = val

class IndexNode(Node):
    def __init__(self, name: str, path: list):
        super().__init__(NodeType.IndexNode, 0)
        self.name = name
        self.path = path

class ReturnNode(Node):
    def __init__(self, returnValue: Node = Node(NodeType.NullNode, 0)):
        super().__init__(NodeType.ReturnNode, 0)
        self.returnValue = returnValue

class FunctionNode(Node):
    def __init__(self, args: list, block: list):
        super().__init__(NodeType.FunctionNode, 0)
        self.args = args
        self.block = block

class FunctionCallNode(Node):
    def __init__(self, args: list, name: str, path: IndexNode = None, hasPath : bool = False):
        super().__init__(NodeType.FunctionCallNode, 0)
        self.args = args
        self.name = name
        self.path = path

class IfStatementNode(Node):
    def __init__(self, condition: CondNode, body: list = [], elifs: list = [], _else: Node = None):
        super().__init__(NodeType.IfStatementNode, 0)
        self.condition = condition
        self.body = body
        self.elifs = elifs
        self._else = _else

class WhileLoopNode(Node):
    def __init__(self, condition: CondNode, body: list = []):
        super().__init__(NodeType.WhileLoopNode, 0)
        self.condition = condition
        self.body = body

class ForLoopNode(Node):
    def __init__(self, first: Node, condition: CondNode, last: Node, body: list = []):
        super().__init__(NodeType.ForLoopNode, 0)
        self.first = first
        self.condition = condition
        self.last = last
        self.body = body

class BreakNode(Node):
    def __init__(self):
        super().__init__(NodeType.BreakNode, 0)

class ImportNode(Node):
    def __init__(self, path: str):
        super().__init__(NodeType.ImportNode, 0)
        self.path = path

class BaseGlobalLog(Node):
    def __init__(self, message: Node):
        super().__init__(NodeType.BaseGlobalLog, 0)
        self.message = message

class BaseGlobalSleep(Node):
    def __init__(self, number: Node):
        super().__init__(NodeType.BaseGlobalSleep, 0)
        self.number = number

class BaseGlobalTime(Node):
    def __init__(self):
        super().__init__(NodeType.BaseGlobalTime, 0)
