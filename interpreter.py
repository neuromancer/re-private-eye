from random import random

from parser import *
from state import *

def resolve_rect(a, b, c, d):
    a = int(resolve_expr(a))
    b = int(resolve_expr(b))
    c = int(resolve_expr(c))
    d = int(resolve_expr(d))
    return (a, b, c, d)
 
def resolve_fcall(fc):
    #print(fc.children)
    #global settings
    name = get_cname(fc.children[0]) 
    if (name == "RECT" or name == "CRect"):
        assert(len(fc.children) == 5)  # 4 parameters
        return resolve_rect(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), get_param(fc.children[4]))
    else:
        raise SyntaxError("I don\'t know how to resolve fcall: %s" % fc)

def resolve_all(xs):
    r = []
    for x in xs:
        r.append(resolve_expr(x))

    return r

def resolve_expr(e):
    if (type(e) == str or type(e) == int):
        # expression already resolved
        return e

    if (str(e).isnumeric()):
        return int(str(e))

    #print(repr(e))
    name = e.data
    if (name == "not"):
        assert(len(e.children) == 1)
        v = resolve_expr(e.children[0])
        v = resolve_variable(v)
        assert(type(v) == str or type(v) == int)
        assert(v != "0" and v != "" and v != '""' and v != "NULL")

        if (v == "FALSE" or v == 0):
            return "TRUE"
        else:
            return "FALSE"

    elif (name == "add"):
        assert(len(e.children) == 2)
        #print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        #print(v1, v2)

        v1 = resolve_variable(v1)
        v2 = resolve_variable(v2)
 
        v1 = int(v1)
        v2 = int(v2)

        return v1+v2

    elif (name == "let"):
        assert(len(e.children) == 2)
        #print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        #print(v1, v2)

        v1 = resolve_variable(v1)
        v2 = resolve_variable(v2)
 
        v1 = int(v1)
        v2 = int(v2)

        if v1<=v2:
            return "TRUE"
        else:
            return "FALSE" 

    elif (name == "lt"):
        assert(len(e.children) == 2)
        #print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        #print(v1, v2)

        v1 = resolve_variable(v1)
        v2 = resolve_variable(v2)
 
        v1 = int(v1)
        v2 = int(v2)

        if v1<=v2:
            return "TRUE"
        else:
            return "FALSE" 

    elif (name == "get"):
        assert(len(e.children) == 2)
        #print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        #print(v1, v2)

        v1 = resolve_variable(v1)
        v2 = resolve_variable(v2)
 
        v1 = int(v1)
        v2 = int(v2)

        if v1>=v2:
            return "TRUE"
        else:
            return "FALSE" 

    elif (name == "gt"):
        assert(len(e.children) == 2)
        #print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        #print(v1, v2)

        v1 = resolve_variable(v1)
        v2 = resolve_variable(v2)
 
        v1 = int(v1)
        v2 = int(v2)

        if v1>v2:
            return "TRUE"
        else:
            return "FALSE"

    elif (name == "random"):
        assert(len(e.children) == 1)
        p = resolve_expr(e.children[0])
        p = resolve_variable(p)

        #p = int(str(e.children[0])) / 100.

        if random()<=p:
            return "TRUE"
        else:
            return "FALSE" 
 
 
    elif (name == "expr"):
        #print(e)
        assert(len(e.children) == 1) 
        return resolve_expr(e.children[0])
    elif (name == "value"):
        assert(len(e.children) == 1)
        return get_value(e)
    elif (name == "fcall"):
        return resolve_fcall(e)
    else:
        raise SyntaxError('I don\'t know how to resolve: %s' % e)

def resolve_variable(f):
    if type(f) == int:
        return f

    assert(not f.isnumeric())

    if (f in ["TRUE","FALSE"]):
        return f

    if (f in definitions["variables"]):
        return(definitions["variables"][f])
    else:
        print("flag %s not found in variable list" % f)
        assert(False)

