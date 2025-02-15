from collections import OrderedDict 
from lark.lexer import Token

from parser import get_cname, get_statements
import state

def compile_debug(d):
    pass
    #print("debugging", repr(d.children))

def compile_define(d):
    name =  get_cname(d.children[0])
    state.definitions[name] = OrderedDict()
    #print("defining", name)

    for c in d.children[1:]:
        if (type(c.children[0]) == Token):
            continue

        if(len(c.children) == 1):
            state.definitions[name][get_cname(c.children[0])] = 0
        elif (len(c.children) == 2):
            #print(c.children[1])
            state.definitions[name][get_cname(c.children[0])] = c.children[1]
        else:
          assert("invalid define")

def compile_setting(s):
    name =  get_cname(s.children[0])
    print("adding setting", name)
    assert(len(s.children) == 2)
    state.settings[name] = get_statements(s.children[1])

def compile_lines(ls):
    for l in ls.children:
        if l.data == 'line':
            for x in l.children:
              compile_line(x)

def compile_line(l):
    if l.data == 'debug':
        compile_debug(l)
    elif l.data == 'define':
        compile_define(l)
    elif l.data == 'setting':
        compile_setting(l) 
    else:
        raise SyntaxError('Unknown line: %s' % l.data)
