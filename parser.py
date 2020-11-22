from lark import Lark
from lark.lexer import Token

game_parser = Lark(r"""
    start: line+
    line: debug
        | define
        | setting

    name : CNAME
    value:  CNAME
          | NUMBER
          | ESCAPED_STRING 

    ?expr: value
        | "!" expr       -> not
        | expr "==" expr -> eq
        | expr "!=" expr -> neq
        | expr "<" expr  -> lt
        | expr "<=" expr -> let
        | expr ">" expr  -> gt
        | expr ">=" expr -> get
        | expr "+" expr  -> add
        | "-" expr       -> minus
        | value "+"      -> plus
        | "Random" "(" NUMBER "%" ")" -> random

    debug : "debug" "{" [ name ("," name)*] "}"
    define : "define" name "{" [def ("," def)*] "}"
    def: name ("," fcall)? 
       | WS

    setting: "setting" name "{" statements "}"
    statements: statement*
    statement: fcall ";"
             | goto ";"
             | ifelse
             | if
 
    goto: "goto" expr

    if: "if" "(" expr ")" ("{" statements "}" | statement) 
    ifelse: "if" "(" expr ")" ("{" statements "}" | statement) "else" ("{" statements "}" | statement )
 
    fcall: name "(" [param ("," param)*] ")"
    param: expr 
         | fcall

    %import common.CNAME
    %import common.NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore /\/\/[^\n]*/ 
    %ignore WS
    """, start='start')

def get_cname(c):
    assert(c.data in ["name", "value"])
    return str(c.children[0])

def get_statements(s):
    assert(s.data == "statements")
    if len(s.children) == 0:
        return []
    return s.children

def get_param(p):
    assert(p.data == "param") 
    return p.children[0]

def get_value(p):
    assert(p.data == "value") 
    v = p.children[0]
    v = str(v)
    
    if (v.isnumeric()):
        return int(v)

    #print("v:", str(v), repr(v))
    return v
    

def get_expr(p):
    assert(p.data == "expr") 
    return p.children[0]

