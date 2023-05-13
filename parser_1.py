from ttoken import TokenType
from nodes import *
from error import InvalidSyntaxError

from otherFunctions import KEYWORDS, dump_ast

class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = (tokens)
        self.currentNum = 0
        self.currentToken = self.tokens[0]
        self.current_line = 1
        self.ast = []
    
    def advance(self):
        self.currentNum += 1
        if self.currentNum < len(self.tokens):
            while self.currentNum < len(self.tokens) and self.tokens[self.currentNum].type == TokenType.NEWL:
                self.currentNum += 1
                self.current_line += 1
                self.ast.append(Node(NodeType.NewLineNode, 0))

            self.currentToken = self.tokens[self.currentNum] if self.currentNum < len(self.tokens) else None
        else:
            self.currentToken = None
    
    def getNodeFromToken(self, ttype):
        if ttype == TokenType.NUMBER:
            return NodeType.NumberNode
        elif ttype == TokenType.STRING:
            return NodeType.StringNode
        elif ttype == TokenType.BOOLEAN:
            return NodeType.BooleanNode
        elif ttype == TokenType.NULL:
            return NodeType.NullNode
        else:
            raise Exception('PARSER METHOD "getNodeFromToken": Unable to cast TokenType to NodeType "{ttype}"')
    def check(self, tokenType: TokenType or list):
        while self.currentToken != None and self.currentToken.type == TokenType.NEWL:
            self.advance()

        if type(tokenType) == 'list':
            if self.currentToken == None or not (self.currentToken.type in tokenType):
                InvalidSyntaxError(self.currentToken.type if self.currentToken else TokenType.NULL, self.current_line, f'Expected {tokenType[0].name}.')
        else:
            if self.currentToken == None or self.currentToken.type != tokenType:
                InvalidSyntaxError(self.currentToken.type if self.currentToken else TokenType.NULL, self.current_line, f'Expected {tokenType.name}.')
        

        val = self.currentToken.value
        self.advance()

        return val

    def bcheck(self, tokenType: TokenType):
        if self.currentToken != None and self.currentToken.type == TokenType.NEWL:
            self.advance()

        if self.currentToken == None or self.currentToken.type != tokenType:
            return False
        
        return True
    
    def checkNext(self, tokenType: TokenType):
        idx = 1
        while self.currentNum + idx < len(self.tokens) and self.tokens[self.currentNum + idx] == TokenType.NEWL:
            idx += 1
        
        if self.tokens[self.currentNum + idx] != None and self.tokens[self.currentNum + idx].type == tokenType:
            return True
        
        return False

    def parse_fstring(self):
        print("NOT IMPLEMENTED YET")
        pass

    def factor(self):
        if self.currentToken != None:
            if self.currentToken.type in [TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL]:
                __type = self.currentToken.type
                __val = self.currentToken.value
                self.advance()
                return Node(self.getNodeFromToken(__type), __val)
            elif self.currentToken.type == TokenType.FSTRING:
                return self.parse_fstring()
            elif self.currentToken.type == TokenType.HLEN:
                self.advance()
                return LengthOpNode(self.factor())
            elif self.currentToken.type == TokenType.NEG:
                self.advance()
                cond = self.factor()
                if (cond in [NodeType.StringNode, NodeType.NumberNode]):
                    InvalidSyntaxError(cond, self.current_line, 'Expected Condition or Boolean.')
                
                return UnOpNode(cond)
            elif self.currentToken.type == TokenType.LSQPAREN:
                ### Arrays & Objects
                valueList = {}
                idx = 0
                self.advance()

                if self.currentToken.type == TokenType.RSQPAREN:
                    self.advance()
                    return ArrayNode(valueList)

                ### Objects
                if self.checkNext(TokenType.EQ) or self.checkNext(TokenType.CEQ):
                    dictVal = {}
                    curId = Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER))
                    if self.bcheck(TokenType.CEQ):
                        self.check(TokenType.CEQ)
                        dictVal[curId] = self.fundefinition()
                    else:
                        self.check(TokenType.EQ)
                        dictVal[curId] = self.expression()
                    if self.bcheck(TokenType.SMCLN):
                        while self.bcheck(TokenType.SMCLN):
                            self.advance()
                            curId = Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER))
                            if self.bcheck(TokenType.CEQ):
                                self.check(TokenType.CEQ)
                                dictVal[curId] = self.fundefinition()
                            else:
                                self.check(TokenType.EQ)
                                dictVal[curId] = self.expression()
                    
                    self.check(TokenType.RSQPAREN)
                    return ObjectNode(dictVal)

                valueList[Node(NodeType.NumberNode, idx)] = self.expression()
                idx += 1
                while self.currentToken != None and not self.bcheck(TokenType.RSQPAREN):
                    self.check(TokenType.COMMA)
                    valueList[Node(NodeType.NumberNode, idx)] = self.expression()
                    idx += 1
                
                
                self.check(TokenType.RSQPAREN)
                return ArrayNode(valueList)
            elif self.currentToken.type == TokenType.IDENTIFIER:
                __val = self.currentToken.value
                self.advance()

                ### Indexing & Function Calls
                if self.bcheck(TokenType.DOT) or self.bcheck(TokenType.LSQPAREN):
                    last = self.currentToken.type
                    self.advance()
                    path = []

                    if last == TokenType.DOT:
                        path.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))
                    else:
                        path.append(self.expression())
                    
                    if last == TokenType.LSQPAREN:
                        self.check(TokenType.RSQPAREN)
                    
                    while self.bcheck(TokenType.DOT) or self.bcheck(TokenType.LSQPAREN):
                        last = self.currentToken.type
                        self.advance()
                        if last == TokenType.DOT:
                            path.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))
                        else:
                            path.append(self.expression())
                            self.check(TokenType.RSQPAREN)
                        
                    if self.bcheck(TokenType.LPAREN):
                        return self.funcall(__val, IndexNode(__val, path))
                    
                    return IndexNode(__val, path)
                elif self.bcheck(TokenType.LPAREN):
                    return self.funcall(__val)
                return VarAccessNode(__val)
            elif self.currentToken.type == TokenType.LPAREN:
                self.advance()
                returnNode = self.expression()
                self.check(TokenType.RPAREN)
                return returnNode
            elif self.currentToken.type == TokenType.MINUS:
                self.advance()
                returnNode = UnOpNode(self.factor())
                return returnNode
            elif self.currentToken.type == TokenType.NEWL:
                self.advance()
                self.current_line += 1
                return self.factor()
            else:
                InvalidSyntaxError(self.currentToken.type, self.current_line, 'Expected Literal.')
        else:
            InvalidSyntaxError(self.currentToken.type, self.current_line, 'Expected Literal, got null.')

    def term(self):
        left = self.factor()

        while self.currentToken != None and self.currentToken.type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            op = self.currentToken.type
            self.advance()
            left = BinOpNode(left, op, self.factor())
        
        return left
    
    def expr1(self):
        left = self.term()

        while self.currentToken != None and self.currentToken.type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.currentToken.type
            self.advance()
            left = BinOpNode(left, op, self.term())

        return left

    def expr(self):
        left = self.expr1()

        while self.currentToken != None and self.currentToken.type in [TokenType.EEQ, TokenType.NQ, TokenType.LT, TokenType.GT, TokenType.GTE, TokenType.LTE]:
            op = self.currentToken.type
            self.advance()
            left = CondNode(left, op, self.expr1())

        return left

    def expression(self):
        left = self.expr()

        while self.currentToken != None and self.currentToken.type in [TokenType.AND, TokenType.OR]:
            op = self.currentToken.type
            self.advance()
            left = CondNode(left, op, self.expr())

        return left

    def statement(self):
        if self.currentToken == None or not (self.currentToken.type in [TokenType.KEYWORD, TokenType.IDENTIFIER]):
            InvalidSyntaxError(self.currentToken.type if self.currentToken != None else 'null', self.current_line, 'Expected keyword or identifier.')
        
        if self.currentToken.type == TokenType.IDENTIFIER:
            identifier = self.currentToken.value
            self.advance()
            
            if self.bcheck(TokenType.LPAREN):
                call = self.funcall(identifier)
                self.check(TokenType.SMCLN)
                return call

            ### Objects
            if self.bcheck(TokenType.DOT) or self.bcheck(TokenType.LSQPAREN):
                last = self.currentToken.type
                self.advance()
                path = []
                if last == TokenType.DOT:
                    path.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))
                else:
                    path.append(self.expression())
                    self.check(TokenType.RSQPAREN)

                while self.bcheck(TokenType.DOT) or self.bcheck(TokenType.LSQPAREN):
                    last = self.currentToken.type
                    self.advance()
                    if last == TokenType.DOT:
                        path.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))
                    else:
                        path.append(self.expression())
                        self.check(TokenType.RSQPAREN)
                
                if self.bcheck(TokenType.LPAREN):
                    fc = self.funcall(identifier, IndexNode(identifier, path))
                    self.check(TokenType.SMCLN)
                    return fc
                
                self.check(TokenType.EQ)
                value = self.expression()
                self.check(TokenType.SMCLN)
                return DataStructOverrideNode(identifier, path, value)

            ### Function Override
            if self.bcheck(TokenType.CEQ):
                self.advance()
                return VarOverrideNode(identifier, self.fundefinition())
            
            ### Compound Operators
            if self.currentToken.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE]:
                operator = self.currentToken.type
                self.advance()
                self.check(TokenType.EQ)
                val = self.expression()
                self.check(TokenType.SMCLN)
                return VarOverrideNode(identifier, BinOpNode(VarAccessNode(identifier), operator, val))

            self.check(TokenType.EQ)
            value = self.expression()
            self.check(TokenType.SMCLN)
            return VarOverrideNode(identifier, value)
        elif self.currentToken.value == KEYWORDS[0]:  ### Let
            self.advance()
            identifier = self.check(TokenType.IDENTIFIER)
            
            ### Functions
            if self.bcheck(TokenType.CEQ):
                self.advance()
                return VarCreateNode(identifier, self.fundefinition())

            self.check(TokenType.EQ)
            value = self.expression()
            self.check(TokenType.SMCLN)
            return VarCreateNode(identifier, value)
        elif self.currentToken.value == KEYWORDS[1]:    ### Return
            self.advance()
            if self.bcheck(TokenType.SMCLN):
                self.advance()
                return ReturnNode()
            else:
                ret = ReturnNode(self.expression())
                self.check(TokenType.SMCLN)
                return ret
        elif self.currentToken.value == KEYWORDS[2]:    ### If Statement
            self.advance()
            return self.ifstatement()
        elif self.currentToken.value == KEYWORDS[4]:    ### While Loops
            self.advance()
            return self.whileloop()
        elif self.currentToken.value == KEYWORDS[5]:    ### For Loops
            self.advance()
            return self.forloop()
        elif self.currentToken.value == KEYWORDS[6]:    ### Break Statements
            self.advance()
            self.check(TokenType.SMCLN)
            return BreakNode()
        elif self.currentToken.value == KEYWORDS[7]:    ### Import
            self.advance()
            return ImportNode(self.check(TokenType.STRING))
    
    
    def forloop(self):
        ### Conditions
        operator = None
        self.check(TokenType.LPAREN)

        # Cond1
        val = self.check(TokenType.KEYWORD)
        if val != KEYWORDS[0]:
            InvalidSyntaxError(TokenType.KEYWORD, self.current_line, f'Got "{val}", expected "let".')
        
        id = self.check(TokenType.IDENTIFIER)
        self.check(TokenType.EQ)
        val = self.expression()
        cond1 = VarCreateNode(id, val)
        # Cond1

        self.check(TokenType.SMCLN)

        # Cond2
        condition = self.expression()
        # Cond2

        self.check(TokenType.SMCLN)

        # Cond3
        id = self.check(TokenType.IDENTIFIER)
        if self.currentToken.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE]:
            operator = self.currentToken.type
            self.advance()
        
        self.check(TokenType.EQ)
        val = self.expression()
        cond3 = VarOverrideNode(id, val if operator == None else BinOpNode(VarAccessNode(id), operator, val))
        # Cond3

        self.check(TokenType.RPAREN)

        ### Block
        self.check(TokenType.LCPAREN)
        body = self.block(True)
        self.check(TokenType.RCPAREN)

        return ForLoopNode(cond1, condition, cond3, body)

    def whileloop(self):
        ### Condition
        self.check(TokenType.LPAREN)
        condition = self.expression()
        self.check(TokenType.RPAREN)

        ### Body
        self.check(TokenType.LCPAREN)
        body = self.block(True)
        self.check(TokenType.RCPAREN)

        return WhileLoopNode(condition, body)

    def ifstatement(self, ignoreElseOrElifs: bool = False):
        elifs = []
        _else = None

        ### Condition Check
        self.check(TokenType.LPAREN)
        condition = self.expression()
        self.check(TokenType.RPAREN)

        ### Body
        self.check(TokenType.LCPAREN)
        block = self.block(True)
        self.check(TokenType.RCPAREN)

        ### Elifs
        if not ignoreElseOrElifs:
            while self.bcheck(TokenType.KEYWORD):
                if self.currentToken.value == KEYWORDS[3]:  ### Else statement
                    self.advance()
                    if self.bcheck(TokenType.KEYWORD):
                        if self.currentToken.value == KEYWORDS[2]:  ### Elseif
                            self.advance()
                            elifs.append(self.ifstatement(True))
                    else:
                        self.check(TokenType.LCPAREN)
                        elseBlock = self.block(True)
                        self.check(TokenType.RCPAREN)
                        _else = IfStatementNode(CondNode(Node(NodeType.NumberNode, 0), TokenType.EEQ, Node(NodeType.NumberNode, 0)), elseBlock)
                else:
                    break
                            

        return IfStatementNode(condition, block, elifs, _else)

    def fundefinition(self):
        ### Arguments Part
        self.check(TokenType.LPAREN)
        args = []
        if not (self.bcheck(TokenType.RPAREN)):
            args.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))
            while self.bcheck(TokenType.COMMA):
                self.advance()
                args.append(Node(NodeType.StringNode, self.check(TokenType.IDENTIFIER)))

        self.check(TokenType.RPAREN)

        ### Body Part
        self.check(TokenType.LCPAREN)
        block = self.block(True)
        self.check(TokenType.RCPAREN)

        return FunctionNode(args, block)

    def funcall(self, identifier, path: list = None):
        self.check(TokenType.LPAREN)
        args = []
        if not (self.bcheck(TokenType.RPAREN)):
            args.append(self.expression())
            while self.bcheck(TokenType.COMMA):
                self.advance()
                args.append(self.expression())
            
        self.check(TokenType.RPAREN)
        
        return FunctionCallNode(args, identifier, path)


    def block(self, retBlock: bool = False):
        block = []
        while self.currentToken != None and self.currentToken.type != TokenType.RCPAREN:
            while self.currentToken != None and self.currentToken.type == TokenType.NEWL:
                if retBlock: block.append(Node(NodeType.NewLineNode, 0))
                if not retBlock: self.ast.append(Node(NodeType.NewLineNode, 0))
                self.current_line += 1
                self.advance()
            if self.currentToken != None and self.currentToken.type != TokenType.RCPAREN:
                statement = self.statement()
                if retBlock: block.append(statement)
                if not retBlock: self.ast.append(statement)
        
        if retBlock: return block

    def parse(self):
        self.block()
        
        ### Error Checking
        if self.currentToken != None:
            InvalidSyntaxError(self.currentToken.type, self.current_line, 'Expected EOF.')

        return self.ast
