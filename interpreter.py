from nodes import *
from ttoken import *
from otherFunctions import dump_ast, convert

from time import sleep, time

from error import InvalidStatementTypeError, DivisionByZeroError, InvalidConditionOperatorError, StringConcatenationError, VariableError, VariableUnexistentError, FunctionArgumentError

RET_VAL = Node(NodeType.NullNode, 0)

class Interpreter:
    def __init__(self, ast):
        self.current_line = 1
        self.nodes = ast
        self.symbolTable = {
            'log': FunctionNode([Node(NodeType.StringNode, 'value')], [
                BaseGlobalLog(VarAccessNode('value'))
            ]),
            'sleep': FunctionNode([Node(NodeType.StringNode, 'number')], [
                BaseGlobalSleep(VarAccessNode('number'))
            ]),
            'time': FunctionNode([], [
                ReturnNode(BaseGlobalTime())
            ])
        }

        self.stack = {
            'func' : []
        }

    def evaluate(self):
        self.visitBlock(self.nodes)
    
    def visitBlock(self, block):
        for node in block:
            if len(self.stack['func']) != 0:
                return
            self.visitStatement(node)
    
    def visitStatement(self, statement: Node):
        if statement.type == NodeType.VarCreateNode:
            self.visitVarCreateNode(statement)
        elif statement.type == NodeType.VarOverrideNode:
            self.visitVarOverrideNode(statement)
        elif statement.type == NodeType.DataStructOverrideNode:
            self.visitDataStructOverrideNode(statement)
        elif statement.type == NodeType.IfStatementNode:
            self.visitIfStatementNode(statement)

        elif statement.type == NodeType.NewLineNode:
            self.current_line += 1
        elif statement.type == NodeType.ReturnNode:
            self.stack['func'].append(self.visitExpression(statement.returnValue))
        
        elif statement.type == NodeType.BaseGlobalLog:
            print(self.visitExpression(statement.message).value)
        elif statement.type == NodeType.BaseGlobalSleep:
            sleep(self.visitExpression(statement.number).value)

        elif statement.type == NodeType.FunctionCallNode:
            self.visitExpression(statement)
    
    def deep(self, node: ArrayNode or ObjectNode):
        newN = {}
        for key, val in node.value.items():
            newN[self.visitExpression(key)] = self.visitExpression(val, True)
        
        return ArrayNode(newN) if node.type == NodeType.ArrayNode else ObjectNode(newN)

    def visitExpression(self, expression: Node, deep: bool = False):
        if expression.type in [NodeType.NumberNode, NodeType.StringNode, NodeType.BooleanNode, NodeType.NullNode, NodeType.ArrayNode, NodeType.ObjectNode, NodeType.FunctionNode]:
            if expression.type in [NodeType.ArrayNode, NodeType.ObjectNode]:
                return self.deep(expression)
            return expression
        elif expression.type == NodeType.BinOpNode:
            return self.visitBinOpNode(expression)
        elif expression.type == NodeType.UnOpNode:
            return self.visitUnOpNode(expression)
        elif expression.type == NodeType.CondNode:
            return self.visitCondNode(expression)
        elif expression.type == NodeType.VarAccessNode:
            return self.visitVarAccessNode(expression)
        elif expression.type == NodeType.IndexNode:
            return self.visitIndexNode(expression)
        elif expression.type == NodeType.FunctionCallNode:
            return self.visitFunctionCallNode(expression)

        elif expression.type == NodeType.BaseGlobalTime:
            return Node(NodeType.NumberNode, time())

        else:
            InvalidStatementTypeError(expression.type, '', self.current_line)
    
    def visitBinOpNode(self, node: BinOpNode):
        left = convert(self.visitExpression(node.left))
        op = node.op
        right = convert(self.visitExpression(node.right))
        resultNode = Node(NodeType.NumberNode, 0)

        if node.left.type == NodeType.StringNode or node.right.type == NodeType.StringNode:
            if op == TokenType.PLUS:
                resultNode.value = str(left) + str(right)
                resultNode.type = NodeType.StringNode
            else:
                StringConcatenationError(self.current_line)
        else:
            if op == TokenType.PLUS:
                resultNode.value = left + right
            elif op == TokenType.MINUS:
                resultNode.value = left - right
            elif op == TokenType.MULTIPLY:
                resultNode.value = left * right
            elif op == TokenType.DIVIDE:
                if right == 0:
                    DivisionByZeroError(self.current_line)
                resultNode.value = left / right
        
        return resultNode

    def visitUnOpNode(self, node: UnOpNode):
        val = float(self.visitExpression(node.node).value)
        return Node(NodeType.NumberNode, -val)

    def visitCondNode(self, node: CondNode):
        left = (self.visitExpression(node.left))
        right = (self.visitExpression(node.right))
        op = node.op
        resultNode = Node(NodeType.BooleanNode, 0)

        if not (op in [TokenType.AND, TokenType.OR]):
            left = convert(left)
            right = convert(right)
            if op == TokenType.EEQ:
                if left == right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.NQ:
                if left != right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.LT:
                if left < right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.LTE:
                if left <= right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.GT:
                if left > right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            elif op == TokenType.GTE:
                if left >= right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            else:
                InvalidConditionOperatorError(op, self.current_line)
        else:
            if left.type != NodeType.BooleanNode or right.type != NodeType.BooleanNode:
                InvalidConditionOperatorError(op, self.current_line)
            
            left = left.value
            right = right.value

            if op == TokenType.AND:
                if left and right:
                    resultNode.value = True
                else:
                    resultNode.value = False
            else:
                if left or right:
                    resultNode.value = True
                else:
                    resultNode.value = False

        
        return resultNode
    
    def visitVarOverrideNode(self, node: Node, regardlessOfExistence: bool = False):
        self.visitVarCreateNode(node, True, regardlessOfExistence)

    def visitVarCreateNode(self, node: VarCreateNode, override: bool=False, regardlessOfExistence: bool = False):
        valNode = self.visitExpression(node.value)
        if node.name in self.symbolTable and override == False:
            VariableError(node.name, self.current_line)
        if not (node.name in self.symbolTable) and override == True and not regardlessOfExistence:
            VariableUnexistentError(node.name, self.current_line)

        self.symbolTable[node.name] = valNode
    
    def visitVarAccessNode(self, node: VarAccessNode):
        if not (node.name in self.symbolTable):
            VariableUnexistentError(node.name, self.current_line)

        valNode = self.visitExpression(self.symbolTable[node.name])
        return valNode
    
    def visitIndexNode(self, node: IndexNode):
        if not (node.name in self.symbolTable):
            VariableUnexistentError(node.name, self.current_line)
        
        valNode = None
        for explNode in node.path:
            valNode = valNode.value[(self.visitExpression(explNode))] if valNode != None else self.symbolTable[node.name].value[(self.visitExpression(explNode))]
                
        return self.visitExpression(valNode)

    def visitDataStructOverrideNode(self, node: DataStructOverrideNode):
        if not (node.name in self.symbolTable):
            VariableUnexistentError(node.name, self.current_line)

        valNode = self.symbolTable[node.name]
        if len(node.path) > 1:
            valNode = self.symbolTable[node.name].value[(self.visitExpression(node.path[0]))]
            if len(node.path) > 2:
                for explNode in node.path[1:-1]:
                    valNode = valNode.value[(self.visitExpression(explNode))]
    
        valNode.value[(self.visitExpression(node.path[-1]))] = self.visitExpression(node.value)
    
    def visitFunctionCallNode(self, node: FunctionCallNode):
        if not (node.name in self.symbolTable):
            VariableUnexistentError(node.name, self.current_line)
        
        lastSymb = self.symbolTable.copy()
        funNode = self.symbolTable[node.name] if node.path == None else self.visitExpression(node.path)
        targetArgs = funNode.args

        if len(targetArgs) != len(node.args):
            FunctionArgumentError(len(targetArgs), len(node.args))
        
        self.updateSymbolTable(targetArgs, node.args)
        
        if len(funNode.block) > 0:
            self.visitBlock(funNode.block)
        
        retVal = self.stack['func'][0] if len(self.stack['func']) > 0 else Node(NodeType.NullNode, 0)
        if len(self.stack['func']) > 0:
            self.stack['func'].pop(0)

        retVal = self.visitExpression(retVal, True)
        self.symbolTable = self.diffSymbolTables(lastSymb, self.symbolTable)

        return retVal

        ###TODO: Make it so x.a() works
    
    def updateSymbolTable(self, args, val):
        idx = 0
        for arg in args:
            self.visitVarOverrideNode(VarOverrideNode(arg.value, self.visitExpression(val[idx])), True)
            idx += 1
    
    def diffSymbolTables(self, symb1: dict, symb2: dict):
        newSymb = symb1.copy()

        for key, val in symb2.items():
            if key in symb1:
                newSymb[key] = self.visitExpression(val)
        
        return newSymb

    def visitIfStatementNode(self, ifst: IfStatementNode):
        condition = self.visitExpression(ifst.condition)

        elifs = []
        _else = None

        ranElif = False

        if len(ifst.elifs) != 0:
            for elf in ifst.elifs:
                elifs.append(elf)
        
        if ifst._else != None:
            _else = ifst._else
        

        if condition.value:
            self.visitBlock(ifst.body)
        else:
            if len(elifs) > 0:
                for elf in elifs:
                    if self.visitExpression(elf.condition).value:
                        self.visitStatement(elf)
                        ranElif = True
            else:
                if _else != None:
                    self.visitStatement(_else)
            
            if not ranElif:
                if _else != None:
                    self.visitStatement(_else)
