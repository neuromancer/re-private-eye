from sys import exit, argv
from time import sleep

from lark import Lark
from lark.lexer import Token
from collections import OrderedDict 

from ffpyplayer.player import MediaPlayer

import pygame

game_parser = Lark(r"""
    start: line+
    line: debug
        | define
        | setting

    name : CNAME
    value:  CNAME
          | NUMBER
          | ESCAPED_STRING 
    nl: "\n"
    pvalue: NUMBER "%"

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
 
    goto: "goto" expr

    if: "if" "(" expr ")" ["{" statements "}" | statement] 
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

def compile_debug(d):
    print("debugging", repr(d.children))

def get_cname(c):
    return str(c.children[0])

def compile_define(d):
    global definitions
    name =  get_cname(d.children[0])
    definitions[name] = OrderedDict()
    print("defining", name)

    for c in d.children[1:]:
        if (type(c.children[0]) == Token):
            continue

        if(len(c.children) == 1):
            definitions[name][get_cname(c.children[0])] = 0
        elif (len(c.children) == 2):
            #print(c.children[1])
            definitions[name][get_cname(c.children[0])] = c.children[1]
        else:
          assert("invalid define")

def get_statements(s):
    assert(s.data == "statements")
    if len(s.children) == 0:
        return []
    #print(s.children[0])
    return s.children

def compile_setting(s):
    global settings
    #if "'setting', [Tree('name', [Token('CNAME', 'kIntroTitle" in str(s):
    #    print(s.pretty())
    #    print("s0", s.children[0])
    #    print("s1", get_statements(s.children[1]))
    #    print(len(   get_statements(s.children[1]) ) )
    #    assert(False)
    name =  get_cname(s.children[0])
    print("adding setting", name)
    assert(len(s.children) == 2)

    #for c in s.children[1:]:
    settings[name] = get_statements(s.children[1])

def compile_line(l):
    if l.data == 'debug':
        compile_debug(l)

    elif l.data == 'define':
        compile_define(l)

    elif l.data == 'setting':
        compile_setting(l)
 
    else:
        raise SyntaxError('Unknown line: %s' % l.data)

def resolve_rect(a, b, c, d):
    a = int(resolve_expr(a))
    b = int(resolve_expr(b))
    c = int(resolve_expr(c))
    d = int(resolve_expr(d))
    return (a, b, c, d)
 
def resolve_fcall(fc):
    #print(fc.children)
    global settings
    name = get_cname(fc.children[0]) 
    if (name == "RECT" or name == "CRect"):
        assert(len(fc.children) == 5)  # 4 parameters
        return resolve_rect(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), get_param(fc.children[4]))
 

def resolve_expr(e):
    #print(e)
    name = e.data
    if (name == "not"):
        assert(len(e.children) == 1)
        v = resolve_expr(e.children[0])
        if (v == "FALSE"):
            return "TRUE"
        else:
            return "FALSE"

    elif (name == "add"):
        assert(len(e.children) == 2)
        print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        print(v1, v2)

        v1 = resolve_variable(v1)
        v2 = resolve_variable(v2)
 
        v1 = int(v1)
        v2 = int(v2)

        return v1+v2

    elif (name == "let"):
        assert(len(e.children) == 2)
        print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        print(v1, v2)

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
        print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        print(v1, v2)

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
        print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        print(v1, v2)

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
        print(e.children)
        v1 = resolve_expr(e.children[0])
        v2 = resolve_expr(e.children[1])
        print(v1, v2)

        v1 = resolve_variable(v1)
        v2 = resolve_variable(v2)
 
        v1 = int(v1)
        v2 = int(v2)

        if v1>v2:
            return "TRUE"
        else:
            return "FALSE" 
 
    elif (name == "expr"):
        print(e)
        assert(len(e.children) == 1) 
        return resolve_expr(e.children[0])
    elif (name == "value"):
        assert(len(e.children) == 1)
        return get_value(e)
    elif (name == "fcall"):
        return resolve_fcall(e)
    else:
        raise SyntaxError('I don\'t know how to resolve: %s' % e)
 
    #    print("chgmode", fc.children[1:])
    #elif (name == "SetFlag"):
    #    print("setflags", fc.children[1:])


def get_param(p):
    #print(p)
    assert(p.data == "param") 
    return p.children[0]

def get_value(p):
    #print(p)
    assert(p.data == "value") 
    return p.children[0]

def get_expr(p):
    #print(p)
    assert(p.data == "expr") 
    return p.children[0]

def run_goto(e):
    global next_setting
    v = resolve_expr(e)
    print("goto", v)
    next_setting = v 

def run_timer(e1, e2):
    global next_setting
    v1 = resolve_expr(e1)
    v2 = resolve_expr(e2)
    print("timer", v1, v2)
    sleep(int(v1))
    next_setting = v2 

def run_sound(e, loops):
    global cdrom_path
    v = resolve_expr(e)
    print("sound", v)
    if v == '""':
        pygame.mixer.stop()
    else:
        sound = pygame.mixer.Sound(cdrom_path + convert_path(v))
        sound.play(loops)


def run_mask(m, e, v, drawn):
    m = resolve_expr(m)
    e = resolve_expr(e)
    v = resolve_expr(v)

    global cdrom_path
    global masks
    print("mask", m, e, v)
    bmp = pygame.image.load(cdrom_path + convert_path(m))
    bmp.set_colorkey((0, 255, 0))
    masks.append((bmp, e))
    if drawn:
        screen.blit(bmp, [0, 0])
        pygame.display.flip()

def run_bitmap(e, x, y):
    if (type(x) != int):
        x = resolve_expr(x)
        x = int(x)

    if (type(y) != int):
        y = resolve_expr(y)
        y = int(y)

    global cdrom_path
    v = resolve_expr(e)
    print("bitmap", v, x, y)
    bmp = pygame.image.load(cdrom_path + convert_path(v))
    bmp.set_colorkey((0, 255, 0))
    screen.blit(bmp, [x, y])
    pygame.display.flip()

def resolve_variable(f):
    if f.isnumeric():
        return f

    if (f in ["TRUE","FALSE"]):
        return f

    if (f in definitions["variables"]):
        return(definitions["variables"][f])
    else:
        print("flag %s not found in variable list" % f)
        assert(False)

def run_setflag(f, v):
    f = resolve_expr(f)
    v = resolve_expr(v)
    #print(definitions["rects"])
    #print(e)
    if (f in definitions["variables"]):
        definitions["variables"][f] = v 
    else:
        print("flag %s not found in variable list" % f)
        assert(False)

    print("setflag", f, v)

def run_exit(e, r):
    r = resolve_expr(r)
    e = resolve_expr(e)
    #print(definitions["rects"])
    #print(e)
    if (r in definitions["rects"]):
        r = definitions["rects"][r]
        r = resolve_expr(r)

    (a, b, c, d) = r
    exits.append((a, b, c, d, e))
    print("exit", e, r)

def convert_path(p):
    p = p.lower()
    p = p.replace('"','')
    return p.replace("\\","/")

def run_transition(v, e):
    global screen
    global video_to_play
    v = resolve_expr(v)
    e = resolve_expr(e)

    print("play", v)
    video_to_play = (cdrom_path + convert_path(v), e)
    #assert(False)
    #play_video(cdrom_path + convert_path(v), screen)

def run_fcall(fc):
    #print(fc.children)
    global settings
    name = get_cname(fc.children[0]) 
    if (name == "goto"):
        assert(len(fc.children) == 2) # 1 parameter
        run_goto(get_param(fc.children[1]))
    elif (name == "ChgMode"): 
        assert(len(fc.children) == 3 or len(fc.children) == 4) # 2 or 3 parameter
        run_goto(get_param(fc.children[2])) # this looks like a goto
 
    elif (name == "Timer"):
        assert(len(fc.children) == 4) # 3 parameters
        run_timer(get_param(fc.children[1]), get_param(fc.children[2]))
    elif (name == "Bitmap"):
        assert(len(fc.children) == 2 or len(fc.children) == 4)  # 1 or 3 parameters
        x = 0
        y = 0

        if len(fc.children) == 4:
            x = get_param(fc.children[2])
            y = get_param(fc.children[3])

        run_bitmap(get_param(fc.children[1]), x, y)

    elif (name == "VSPicture"):
        assert(len(fc.children) == 2)  # 1 or 3 parameters
        run_bitmap(get_param(fc.children[1]), 0, 0)

    elif (name == "Mask"):
        assert(len(fc.children) == 4)  # 1 or 3 parameters
        run_mask(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), False)

    elif (name == "MaskDrawn"):
        assert(len(fc.children) == 4)  # 1 or 3 parameters
        run_mask(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), True)
 
    elif (name == "Sound"):
        assert(len(fc.children) == 2 or len(fc.children) == 4 or len(fc.children) == 5)  # 1, 3 or 4 parameters
        run_sound(get_param(fc.children[1]), 1)

    elif (name == "LoopedSound"):
        assert(len(fc.children) == 2)  # 1 or 3 parameters
        run_sound(get_param(fc.children[1]), -1)
 
    elif (name == "Transition"):
        assert(len(fc.children) == 3)  # 2 parameters
        run_transition(get_param(fc.children[1]), get_param(fc.children[2]))
    elif (name == "Exit"):
        assert(len(fc.children) == 4)  # 3 parameters
        run_exit(get_param(fc.children[1]), get_param(fc.children[3]))

    elif (name == "SetFlag"):
        assert(len(fc.children) == 3)  # 2 parameters
        run_setflag(get_param(fc.children[1]), get_param(fc.children[2])) 
    elif (name == "SetModifiedFlag"):
        assert(len(fc.children) == 2)  # 1 parameter
        print("SetModifiedFlag (no op for now)") 
        #run_setflag(get_param(fc.children[1]), get_param(fc.children[2]))

    elif (name == "Movie"):
        assert(len(fc.children) == 3)  # 2 parameter
        print("Movie (goto?)") 
        run_goto(get_param(fc.children[2]))
 
    elif (name == "Quit"): 
        assert(len(fc.children) == 1) # No parameters
        pygame.quit()
        exit(0)
    elif (name == "RestartGame"): 
        assert(len(fc.children) == 1) # No parameters
        print("RestarGame (no op for now)") 

    elif (name == "PoliceBust"): 
        print("PoliceBust (no op for now)") 
 
    elif (name == "DossierAdd"): 
        assert(len(fc.children) == 3) # 2 parameters
        print("DossierAdd (no op for now)") 
  
    else:
        raise SyntaxError('I don\'t know how to exec: %s' % fc)

def run_ifelse(ie):
    assert(ie.data == "ifelse")
    v = resolve_expr(ie.children[0])
    v = resolve_variable(v)
    if (v is None):
        print("Uninitialized variable %s" % v)
        assert(False)
    print("ifelse", repr(v))
    if (v == "FALSE" or v == 0):
        if (ie.children[2].data) == "statements":
            for s in ie.children[2].children:
                run_statement(s)
        elif (ie.children[2].data) == "statement":
            run_statement(ie.children[2])
 
    else:
        print("TRUE!")
        if (ie.children[1].data) == "statements":
            for s in ie.children[1].children:
                run_statement(s)
        elif (ie.children[1].data) == "statement":
            run_statement(ie.children[1])


def run_if(i):
    assert(i.data == "if")
    v = resolve_expr(i.children[0])
    v = resolve_variable(v)
    if (v is None):
        print("Uninitialized variable %s" % v)
        assert(False)

    print("if", v) 

    if (v != "FALSE" and v != 0):
        if (i.children[1].data) == "statements":
            run_statement(i.children[1].children[0])
        elif (i.children[1].data) == "statement":
            run_statement(i.children[1])
 

def run_statement(s):
    s = s.children[0] 
    global settings

    if s.data == 'fcall':
        run_fcall(s)
    elif s.data == 'ifelse':
        run_ifelse(s)
    elif s.data == 'if':
        run_if(s)
    elif (s.data == "goto"):
        run_goto(s.children[0])
 
    #elif s.data == '':
    #    print(s.children)
 
    else:
        raise SyntaxError('I don\'t know how to run: %s' % s)

def check_for_events():
    global exits
    global masks
    global next_setting

    #x,y = pygame.mouse.get_pos()

    #for mask in masks:
    #    if mask.get_at(x, y) == 1:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x,y = event.pos

            for (bmp, new_setting) in masks:
                mask = pygame.mask.from_surface(bmp)
                print("mask", mask.get_at((x, y)))
                if mask.get_at((x, y)) == 1:
                    screen.blit(bmp, [0, 0])
                    pygame.display.flip()
                    next_setting = new_setting
                    masks = []
                    return True

            for (xs, ys, xe, ye, new_setting) in exits:
                if (x>=xs and x<=xe):
                    if (y>=ys and y<=ye):
                        next_setting = new_setting
                        exits = []
                        return True
    return False

cdrom_path = None 
definitions = OrderedDict()
masks = []
next_setting = None
settings = OrderedDict()
exits = []
video_to_play = None
screen = None

if __name__ == '__main__':

    if (len(argv) == 2):
        cdrom_path = argv[1]
    else:
        print("A path to the CDROM files is required")
        exit(-1)

    pygame.init()

    # Set up the drawing window
    screen = pygame.display.set_mode([640, 480])
    pygame.display.set_caption("Private Eye (1996) re-implementation")

    with open('assets/GAME.DAT') as f:
        data = f.read()

    print("Parsing game assets..")
    ls = game_parser.parse(data)
    print("Compiling assets..")
    for l in ls.children:
        if l.data == 'line':
            for x in l.children:
              compile_line(x)

    print("Executing game..")
    next_setting = "kIntro" #Movie"
    while True:

        check_for_events()

        if (video_to_play != None):
            print("playing", video_to_play)
            filename, next_setting = video_to_play
            player = MediaPlayer(filename)
            video_to_play = None
            val = None
            while val != 'eof':
                if check_for_events():
                    player.close_player()
                    break

                frame, val = player.get_frame()
                if val != 'eof' and frame is not None:
                    img, t = frame
                    data = bytes(img.to_bytearray()[0])
                    w, h = img.get_size()
                    surf = pygame.image.fromstring(data, (w, h), "RGB")
                    sleep(val)
                    screen.blit(surf, [0, 0])

                # Flip the display
                pygame.display.flip()

        if next_setting != None:
            print("setting", next_setting)
            s = next_setting
            exits = []
            masks = []
            next_setting = None

            if (s in settings):
                if settings[s] == []:
                    print("WARNING", s, "is empty")
                    break

                for st in settings[s]:
                    print("EXECUTING",st.pretty())
                    run_statement(st)

    pygame.quit()
