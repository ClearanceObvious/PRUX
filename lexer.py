from ttoken import Token, TokenType
from error import InvalidCharacterError
from otherFunctions import KEYWORDS, BOOL_VAL, NULL_VAL

LETTERS = 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.upper() + '_'
IDENTIFIER_LETTERS = LETTERS + '0123456789'
STRING = IDENTIFIER_LETTERS + '!@#$%^&*()+]}|\\ \';[{:><,/?~`'

class Lexer:
    def __init__(self, content) -> None:
        self.text = content
        self.currentNum = 0
        self.currentChar = self.text[self.currentNum]
        self.line = 1
    
    def advance(self):
        self.currentNum += 1
        self.currentChar = self.text[self.currentNum] if self.currentNum < len(self.text) else None
    
    def checkNext(self, char: str, get: bool = False):
        if self.currentNum + 1 < len(self.text) and self.text[self.currentNum + 1] == char:
            return True if not get else self.text[self.currentNum + 1]
        return False if not get else (self.text[self.currentNum + 1] if self.currentNum + 1 < len(self.text) else 'NULL')
    
    def lex(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in '\t\n \0':
                if self.currentChar in '\n':
                    self.line += 1
                    tokens.append(Token(TokenType.NEWL, 0))
                self.advance()
            elif self.currentChar == ',':
                tokens.append(Token(TokenType.COMMA, 0))
                self.advance()
            elif self.currentChar == '.':
                tokens.append(Token(TokenType.DOT, 0))
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TokenType.PLUS, 0))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TokenType.MINUS, 0))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TokenType.MULTIPLY, 0))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Token(TokenType.LPAREN, 0))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TokenType.RPAREN, 0))
                self.advance()
            elif self.currentChar == ';':
                tokens.append(Token(TokenType.SMCLN, 0))
                self.advance()
            elif self.currentChar == '[':
                tokens.append(Token(TokenType.LSQPAREN, 0))
                self.advance()
            elif self.currentChar == ']':
                tokens.append(Token(TokenType.RSQPAREN, 0))
                self.advance()
            elif self.currentChar == '{':
                tokens.append(Token(TokenType.LCPAREN, 0))
                self.advance()
            elif self.currentChar == '}':
                tokens.append(Token(TokenType.RCPAREN, 0))
                self.advance()
            elif self.currentChar == '=':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.EEQ, 0))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.EQ, 0))
                    self.advance()
            elif self.currentChar == '>':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.GTE, 0))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GT, 0))
                    self.advance()
            elif self.currentChar == '<':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.LTE, 0))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LT, 0))
                    self.advance()
            elif self.currentChar == '/':
                if self.checkNext('/'):
                    while self.currentChar != None and self.currentChar != '\n':
                        self.advance()
                else:
                    tokens.append(Token(TokenType.DIVIDE, 0))
                    self.advance()
                    
            elif self.currentChar == '&':
                if self.checkNext('&'):
                    tokens.append(Token(TokenType.AND, 0))
                    self.advance()
                    self.advance()
                else:
                    InvalidCharacterError('&', self.line)
            elif self.currentChar == '|':
                if self.checkNext('|'):
                    tokens.append(Token(TokenType.OR, 0))
                    self.advance()
                    self.advance()
                else:
                    InvalidCharacterError('|', self.line)
            elif self.currentChar == '!':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.NQ, 0))
                    self.advance()
                    self.advance()
                else:
                    InvalidCharacterError('=', self.line)
            elif self.currentChar == ':':
                if self.checkNext('='):
                    tokens.append(Token(TokenType.CEQ, 0))
                    self.advance()
                    self.advance()
                else:
                    InvalidCharacterError(':', self.line)
            elif self.currentChar == '"':
                self.advance()
                tokens.append(Token(TokenType.STRING, self.lex_string()))
                if self.currentChar != '"':
                    InvalidCharacterError(self.currentChar, self.line)
                self.advance()
            elif self.currentChar in '0123456789':
                tokens.append(Token(TokenType.NUMBER, self.lex_number()))
            elif self.currentChar in LETTERS:
                tokens.append(self.lex_id())
            else:
                InvalidCharacterError(self.currentChar, self.line)

        return tokens

    def lex_number(self):
        nstr = ''
        dotcount = 0

        while self.currentChar != None and self.currentChar in '0123456789.':
            if self.currentChar == '.':
                if dotcount == 1: InvalidCharacterError(self.currentChar, self.line)
                dotcount += 1
            
            nstr += self.currentChar
            self.advance()
        
        if nstr.endswith('.'): nstr = nstr[:-1]
        nstr = (float(nstr))

        return nstr

    def lex_string(self):
        string = ''
        
        while self.currentChar != None and self.currentChar in STRING:
            string += self.currentChar
            self.advance()
        
        return string

    def lex_id(self):
        identifier = ''
        while self.currentChar != None and self.currentChar in LETTERS:
            identifier += self.currentChar
            self.advance()
        
        if identifier == NULL_VAL:
            return Token(TokenType.NULL, 0)
        elif identifier in BOOL_VAL:
            if identifier == BOOL_VAL[0]:
                return Token(TokenType.BOOLEAN, True)
            else:
                return Token(TokenType.BOOLEAN, False)
        elif identifier in KEYWORDS:
            return Token(TokenType.KEYWORD, identifier)
        else:
            return Token(TokenType.IDENTIFIER, identifier)
