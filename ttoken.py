from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    PLUS = 1
    MINUS = 2
    MULTIPLY = 3
    DIVIDE = 4

    LPAREN = 5
    RPAREN = 6

    NUMBER = 7
    STRING = 8
    BOOLEAN = 9
    NULL = 10

    EQ = 11
    EEQ = 12

    LT = 13
    LTE = 14
    GT = 15
    GTE = 16

    NQ = 17

    AND = 18
    OR = 19

    KEYWORD = 20
    IDENTIFIER = 21

    NEWL = 22
    SMCLN = 23  #  ; "Semicolon"

    CEQ = 24    # := "ColonEquals"

    LSQPAREN = 25   # [
    RSQPAREN = 26   # ]
    LCPAREN = 27    # {
    RCPAREN = 28    # }

    COMMA = 29
    DOT = 30

    NEG = 31

    FSTRING = 32
    AID = 33

@dataclass
class Token:
    type: TokenType
    value: any = 0
