from lark import Lark

game_parser = Lark(r"""
    start: line+
    line: debug
        | define
        | setting
        | line

    name : CNAME
    value:  CNAME
          | NUMBER
          | ESCAPED_STRING 
    nl: "\n"
    pvalue: NUMBER "%"

    expr: value
        | "!" expr
        | expr "==" expr 
        | expr "!=" expr
        | expr "<" expr
        | expr "<=" expr
        | expr ">" expr
        | expr ">=" expr 
        | expr "+" expr 
        | "-" expr   
        | value "+"  
        | "Random" "(" pvalue ")"

    debug : "debug" "{" [ name ("," name)*] "}"
    define : "define" name "{" [def ("," def)*] "}"
    def: name ("," fcall)? 
       | WS

    setting: "setting" name "{" statements "}"
    statements: [statement (statement)*]  
    statement: fcall ";"
             | goto ";"
             | ifelse
             | if
 
    goto: "goto" name

    if: "if" "(" expr ")" ["{" statements "}" | statement] 
    ifelse: "if" "(" expr ")" ["{" statements "}" | statement] "else" ["{" statements "}" | statement ]
 
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

def run_line(l):
    if l.data == 'debug':
        print("debugging", (*l.children))
 
    elif l.data == 'define':
        print("defining", (*l.children))

    elif l.data == 'setting':
        print("setting", (*l.children))
 
    else:
        raise SyntaxError('Unknown line: %s' % l.data)

if __name__ == '__main__':

    with open('assets/GAME.DAT') as f:
        data = f.read()

    #parser = Lark(game_grammar)  # Scannerless Earley is the default
    ls = game_parser.parse(data)
    for l in ls.children:
        if l.data == 'line':
            for x in l.children:
              run_line(x)
