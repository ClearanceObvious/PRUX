import sys
from error import InvalidFileNameError
from lexer import Lexer
from parser_1 import Parser
from interpreter import Interpreter
from otherFunctions import dump_ast

sysargs = sys.argv[1:]
filename = sysargs[0]

if filename.split('.')[1] != 'rux':
    InvalidFileNameError(filename.split('.')[1])

file = open(filename, 'r')
contents = file.read()

## LEXING
lexer = Lexer(contents)
tokens = lexer.lex()

## PARSING
parser = Parser(tokens)
ast = parser.parse()

## INTERPRETING
interpreter = Interpreter(ast)
interpreter.evaluate()

file.close()
