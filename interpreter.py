from otherFunctions import convert, dump_ast

from lexer import *
from parser_1 import *

from time import sleep, time

from error import *

RET_VAL = Node(NodeType.NullNode, 0)

class Interpreter:
    def __init__(self, ast):
        self.current_line = 1
        self.nodes = ast
        self.iSymbol = {}
        self.globals = {
            'log': FunctionNode([Node(NodeType.StringNode, 'value')], [
                BaseGlobalLog(VarAccessNode('value'))
            ]),
            'sleep': FunctionNode([Node(NodeType.StringNode, 'number')], [
                BaseGlobalSleep(VarAccessNode('number'))
            ]),
            'time': FunctionNode([], [
                ReturnNode(BaseGlobalTime())
            ]),
            'input': FunctionNode([Node(NodeType.StringNode, 'message')], [
                ReturnNode(BaseGlobalInput(VarAccessNode('message')))
            ]),
            'tostring': FunctionNode([Node(NodeType.StringNode, 'value')], [
                ReturnNode(BaseGlobalConverter(VarAccessNode('value'), NodeType(NodeType.NumberNode)))
            ]),
            'tonumber': FunctionNode([Node(NodeType.StringNode, 'value')], [
                ReturnNode(BaseGlobalConverter(VarAccessNode('value'), NodeType(NodeType.StringNode)))
            ])
        }
        self.symbolTable = self.globals.copy()

        self.stack = {
            'func' : [],
            'loop': []
        }

        self.importRet = None

    def evaluate(self):
        self.visitBlock(self.nodes, True)
    
    def visitBlock(self, block, main: bool = False):
        for node in block:
            if len(self.stack['func']) != 0:
                return
            if len(self.stack['loop']) != 0:
                return
            if not main:
                self.visitStatement(node, block)
            else:
                self.visitStatement(node, lookForReturn = True)
            
    
    def visitStatement(self, statement: Node, block: list = [], lookForReturn: bool = False):
        # Internals
        if statement.type == NodeType.VarCreateNode:
            self.visitVarCreateNode(statement)
        elif statement.type == NodeType.VarOverrideNode:
            self.visitVarOverrideNode(statement)
        elif statement.type == NodeType.DataStructOverrideNode:
            self.visitDataStructOverrideNode(statement)
        elif statement.type == NodeType.IfStatementNode:
            self.visitIfStatementNode(statement)
        elif statement.type == NodeType.WhileLoopNode:
            self.visitWhileLoopNode(statement)
        elif statement.type == NodeType.ForLoopNode:
            self.visitForLoopNode(statement)
        elif statement.type == NodeType.ImportNode:
            self.visitImportNode(statement)

        # Branch Operators / NEWL
        elif statement.type == NodeType.NOP:
            pass
        elif statement.type == NodeType.NewLineNode:
            self.current_line += 1

            if len(block) != 0:
                for s in block:
                    if s.type == NodeType.NewLineNode:
                        s.type = Node(NodeType.NOP)
                        break
    
        elif statement.type == NodeType.ReturnNode:
            if lookForReturn:
                val = self.visitExpression(statement.returnValue)
                if val.type != NodeType.ObjectNode:
                    ExportError(val.type, self.current_line)
                self.importRet = self.visitExpression(val, True)
            else:
                self.stack['func'].append(self.visitExpression(statement.returnValue))
        elif statement.type == NodeType.BreakNode:
            self.stack['loop'].append(RET_VAL)
        
        # Globals
        elif statement.type == NodeType.BaseGlobalLog:
            val = self.visitExpression(statement.message).value
            print(self.visitLogNode(val))
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
        elif expression.type == NodeType.LengthOpNode:
            return self.visitLengthOpNode(expression)

        # Globals
        elif expression.type == NodeType.BaseGlobalConverter:
            return self.visitGlobalConverter(expression)
        elif expression.type == NodeType.BaseGlobalTime:
            return Node(NodeType.NumberNode, time())
        elif expression.type == NodeType.BaseGlobalInput:
            ask_val = self.visitExpression(expression.message).value
            print(self.visitLogNode(ask_val), end='')

            return Node(NodeType.StringNode, input(''))
        else:
            InvalidStatementTypeError(expression.type, '', self.current_line)
    
    def visitBinOpNode(self, node: BinOpNode):
        left = (self.visitExpression(node.left))
        op = node.op
        right = (self.visitExpression(node.right))
        resultNode = Node(NodeType.NumberNode, 0)

        if left.type == NodeType.StringNode or right.type == NodeType.StringNode:
            if op == TokenType.PLUS:
                return Node(NodeType.StringNode, str(left.value) + str(right.value))
            else:
                StringConcatenationError(self.current_line)
        else:
            left = convert(left)
            right = convert(right)
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
        if self.visitExpression(node.node).type == NodeType.BooleanNode:
            return Node(NodeType.BooleanNode, not self.visitExpression(node.node).value)
        
        if self.visitExpression(node.node).type == NodeType.CondNode:
            return Node(NodeType.BooleanNode, not self.visitExpression(node.node).value)

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
    
        if override and node.name in self.iSymbol:
            self.iSymbol[node.name] = valNode

        if node.name in self.symbolTable and override == False:
            VariableError(node.name, self.current_line)
        if not (node.name in self.symbolTable) and override == True and not regardlessOfExistence:
            VariableUnexistentError(node.name, self.current_line)

        self.symbolTable[node.name] = valNode
    
    def visitVarAccessNode(self, node: VarAccessNode):
        if node.name in self.symbolTable: pass
        elif node.name in self.iSymbol: pass
        else: VariableUnexistentError(node.name, self.current_line)
        
        symb = self.symbolTable if node.name in self.symbolTable else self.iSymbol

        valNode = self.visitExpression(symb[node.name])
        return valNode
    
    def visitIndexNode(self, node: IndexNode):
        if node.name in self.symbolTable: pass
        elif node.name in self.iSymbol: pass
        else: VariableUnexistentError(node.name, self.current_line)
        
        symb = self.symbolTable if node.name in self.symbolTable else self.iSymbol

        FF_STRING = False

        valNode = None
        for explNode in node.path:
            try:
                valNode = valNode.value[self.visitExpression(explNode)] if valNode != None else symb[node.name].value[self.visitExpression(explNode)]
            except Exception:
                ### String Concatination
                FF_STRING = True
                valNode = str(valNode.value)[int(self.visitExpression(explNode).value)] if valNode != None else str(symb[node.name].value)[int(self.visitExpression(explNode).value)]
        
        return self.visitExpression(valNode) if FF_STRING == False else Node(NodeType.StringNode, valNode)

    def visitDataStructOverrideNode(self, node: DataStructOverrideNode):
        if node.name in self.symbolTable: pass
        elif node.name in self.iSymbol: pass
        else: VariableUnexistentError(node.name, self.current_line)
        
        symb = self.symbolTable if node.name in self.symbolTable else self.iSymbol

        valNode = symb[node.name]
        if len(node.path) > 1:
            valNode = self.symbolTable[node.name].value[(self.visitExpression(node.path[0]))]
            if len(node.path) > 2:
                for explNode in node.path[1:-1]:
                    valNode = valNode.value[(self.visitExpression(explNode))]
    
        valNode.value[(self.visitExpression(node.path[-1]))] = self.visitExpression(node.value)
    
    def visitFunctionCallNode(self, node: FunctionCallNode):
        if node.name in self.symbolTable: pass
        elif node.name in self.iSymbol: pass
        else: VariableUnexistentError(node.name, self.current_line)
        
        lastSymb = self.symbolTable.copy()
        funNode = self.symbolTable[node.name] if node.path == None else self.visitExpression(node.path)
        targetArgs = funNode.args

        if len(targetArgs) != len(node.args):
            FunctionArgumentError(len(targetArgs), len(node.args))
        
        self.updateSymbolTable(targetArgs, node.args)
        

        if len(funNode.block) > 0:
            self.visitBlock(funNode.block, main=False)
        
        retVal = self.stack['func'][0] if len(self.stack['func']) > 0 else Node(NodeType.NullNode, 0)
        if len(self.stack['func']) > 0:
            self.stack['func'].pop(0)

        retVal = self.visitExpression(retVal, True)
        self.symbolTable = self.diffSymbolTables(lastSymb, self.symbolTable)

        return retVal
    
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

        lastSymb = self.symbolTable.copy()

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
                    return
            
            if not ranElif:
                if _else != None:
                    self.visitStatement(_else)
                    return
        
        self.symbolTable = self.diffSymbolTables(lastSymb, self.symbolTable)
    
    def visitWhileLoopNode(self, whln: WhileLoopNode):
        lastSymb = self.symbolTable.copy()
        while self.visitExpression(whln.condition).value:
            whlnSymb = self.symbolTable.copy()
            self.visitBlock(whln.body)
            self.symbolTable = self.diffSymbolTables(whlnSymb, self.symbolTable)

            if len(self.stack['loop']) != 0:
                self.stack['loop'].pop()
                break
        
        self.symbolTable = self.diffSymbolTables(lastSymb, self.symbolTable)
    
    def visitForLoopNode(self, frln: ForLoopNode):
        lastSymb = self.symbolTable.copy()
        self.visitStatement(frln.first)

        while self.visitExpression(frln.condition).value:
            frlnSymb = self.symbolTable.copy()
            self.visitBlock(frln.body)
            self.symbolTable = self.diffSymbolTables(frlnSymb, self.symbolTable)

            self.visitStatement(frln.last)
            if len(self.stack['loop']) != 0:
                self.stack['loop'].pop()
                break

        self.symbolTable = self.diffSymbolTables(lastSymb, self.symbolTable)
    
    def visitImportNode(self, node):
        if node.path.split('.')[1] != 'rux':
            InvalidFileNameError(node.path.split('.')[1])

        file = open(node.path, 'r')

        otherFile = Interpreter(Parser(Lexer(file.read()).lex()).parse())
        otherFile.evaluate()

        if otherFile.importRet != None:
            for i, v in otherFile.importRet.value.items():
                self.visitVarOverrideNode(VarOverrideNode(convert(i), v), True)
            
            otherFile.symbolTable.update(otherFile.iSymbol)
            self.iSymbol.update(otherFile.symbolTable)
    
    def visitLogNode(self, message):
        string = ''
        message = str(message)

        idx = 0
        while (idx < len(message)):
            char = message[idx]
            nextChar = message[idx + 1] if idx + 1 < len(message) else message[idx]

            if char == '\\':
                if nextChar == 'n':
                    idx += 2
                    string += '\n'
                    continue
                elif nextChar == '\\':
                    idx += 2
                    string += '\\'
                    continue
                idx += 2
                continue
            
            string += char
            idx += 1
        
        return string
    
    def visitGlobalConverter(self, converter: BaseGlobalConverter):
        newVal = self.visitExpression(converter.nodeValue)
        retVal = Node(NodeType.StringNode, 0)
        if converter.nodeType == NodeType.NumberNode:
            retVal.type = NodeType.StringNode
            retVal.value = newVal.value
        elif converter.nodeType == NodeType.StringNode:
            try:
                nV = float(newVal.value)
                retVal = Node(NodeType.NumberNode, nV)
            except Exception:
                ConverterError(retVal.type, self.current_line, 'Unable to convert to number.')
        else:
            ConverterError(converter.nodeType, self.current_line)
        
        return retVal

    def visitLengthOpNode(self, node: LengthOpNode):
        value = self.visitExpression(node.val)

        if value.type in [NodeType.ObjectNode, NodeType.ArrayNode, NodeType.StringNode]:
            return Node(NodeType.NumberNode, len(value.value))
        else:
            return Node(NodeType.NullNode, 0)
