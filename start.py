from sys import exit, argv
from time import sleep

#from lark import Lark
from lark.lexer import Token
from collections import OrderedDict 

from ffpyplayer.player import MediaPlayer

from parser import *
from compiler import *
from state import *
import pygame

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

def resolve_all(xs):
    r = []
    for x in xs:
        r.append(resolve_expr(x))

    return r

def resolve_expr(e):
    if (type(e) == str or type(e) == int):
        # expression already resolved
        return e

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
    v = p.children[0]
    v = str(v)
    
    if (v.isnumeric()):
        return int(v)

    #print("v:", str(v), repr(v))
    return v
    

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
        pygame.mixer.stop()
        print("starting sound")
        sound = pygame.mixer.Sound(cdrom_path + convert_path(v))
        sound.play(loops)
        print("continue executing")


def run_mask(m, e, v, drawn):
    m = resolve_expr(m)
    e = resolve_expr(e)
    v = resolve_expr(v)

    global cdrom_path
    global origin
    global masks
    print("mask", m, e, v)
    bmp = pygame.image.load(cdrom_path + convert_path(m))
    bmp.set_colorkey((0, 255, 0))
    masks.append((bmp, e))
    if drawn:
        screen.blit(bmp, [origin[0], origin[1]])
        pygame.display.flip()

def run_bitmap(e, x, y):
    if (type(x) != int):
        x = resolve_expr(x)
        x = int(x)

    if (type(y) != int):
        y = resolve_expr(y)
        y = int(y)

    global cdrom_path
    global origin
    v = resolve_expr(e)
    print("bitmap", v, x, y)
    bmp = pygame.image.load(cdrom_path + convert_path(v))
    bmp.set_colorkey((0, 255, 0))
    screen.blit(bmp, [origin[0] + x, origin[1] + y])
    pygame.display.flip()

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

def run_restart_game():
    global current_view_frame
    global origin
    current_view_frame = pygame.image.load(cdrom_path + game_frame)
    origin = [63, 48]

def run_exit(e, r):
    global origin
    r = resolve_expr(r)
    e = resolve_expr(e)
    #print(definitions["rects"])
    #print(e)
    if (r in definitions["rects"]):
        r = definitions["rects"][r]
        r = resolve_expr(r)

    (a, b, c, d) = r
    exits.append((origin[0] + a, origin[1] + b, origin[0] + c, origin[1] + d, e))
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
    if (v != '""'):
        video_to_play = (cdrom_path + convert_path(v), e)
    else:
        pass
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
        assert(len(fc.children) == 2)  # 1 parameter
        run_bitmap(get_param(fc.children[1]), 0, 0)

    elif (name == "Mask"):
        assert(len(fc.children) == 4)  # 3 parameters
        run_mask(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), False)

    elif (name == "MaskDrawn"):
        assert(len(fc.children) == 4)  # 3 parameters
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
        print("Movie (transition?)")
        #assert(False)
        run_transition(get_param(fc.children[1]), get_param(fc.children[2]))
        #run_goto(get_param(fc.children[2]))
 
    elif (name == "Quit"): 
        assert(len(fc.children) == 1) # No parameters
        pygame.quit()
        exit(0)
    elif (name == "RestartGame"): 
        assert(len(fc.children) == 1) # No parameters
        run_restart_game()
        print("RestarGame (no op for now)") 

    elif (name == "PoliceBust"): 
        print("PoliceBust (no op for now)") 
 
    elif (name == "DossierAdd"): 
        assert(len(fc.children) == 3) # 2 parameters
        print("DossierAdd (no op for now)") 

    elif (name == "Inventory"): 
        assert(len(fc.children) == 10) # 9 parameters
        print("Inventory")
        run_inventory(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), get_param(fc.children[4]), get_param(fc.children[5]))
 

    else:
        raise SyntaxError('I don\'t know how to exec: %s' % fc)

def run_inventory(b1, v1, v2, e, b2): #a, b, c, d):
    [b1, v1, v2, e, b2] = resolve_all([b1, v1, v2, e, b2])
    print("inventory", b1, v1, v2, e, b2) 
    if v1 != '""':
        run_setflag(v1, "TRUE")

    if v2 != '""':
        run_setflag(v2, "TRUE")

def run_ifelse(ie):
    assert(ie.data == "ifelse")
    assert(len(ie.children) == 3)

    v = resolve_expr(ie.children[0])
    v = resolve_variable(v)
    if (v is None):
        print("Uninitialized variable %s" % v)
        assert(False)

    #v = resolve_expr(v)
    #print("ifelse", repr(v))
    assert(type(v) == str or type(v) == int)

    if (v == "FALSE" or v == "0"):
        if (ie.children[2].data) == "statements":
            run_statements(ie.children[2])
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
    assert(len(i.children) == 2)

    #print(i)
    v = resolve_expr(i.children[0])
    v = resolve_variable(v)
    if (v is None):
        print("Uninitialized variable %s" % v)
        assert(False)

    #v = resolve_expr(v)
    #print("if", repr(v))
    assert(type(v) == str or type(v) == int)

    if (v != "FALSE" and v != "0"):
        print("TRUE!")
        if (i.children[1].data) == "statements":
            run_statements(i.children[1])
            #for s in i.children[1].children:
            #    run_statement(s)
        elif (i.children[1].data) == "statement":
            run_statement(i.children[1])
 
def run_statements(ss):
    assert(ss.data == "statements") 
    for s in ss.children:
        print("EXECUTING",s.pretty())
        run_statement(s)

def run_statement(s):
    s = s.children[0] 
    global settings

    if s.data == 'fcall':
        run_fcall(s)
    elif s.data == 'ifelse':
        #print("if", s.pretty()) 
        run_ifelse(s)
    elif s.data == 'if':
        #print("if", s.pretty())
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
    global origin

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
                #if(bmp.get_size() != (640, 480)):
                #    print(bmp, bmp.get_size())
                #    assert(False)
                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (x >= msize[0] or y >= msize[1]):
                    continue

                print("mask", mask.get_at((x, y)))
                if mask.get_at((x, y)) == 1:
                    screen.blit(bmp, [origin[0], origin[1]])
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

        if current_view_frame is not None:
            screen.blit(current_view_frame, [0, 0])

        if check_for_events():
            pass
        elif (video_to_play != None):
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
                    screen.blit(surf, [origin[0], origin[1]])

                # Flip the display
                pygame.display.flip()

        if next_setting != None:
            print("setting", next_setting)
            s = next_setting
            exits = []
            masks = []
            video_to_play = None
            next_setting = None

            if (s in settings):
                if settings[s] == []:
                    print("WARNING", s, "is empty")
                    break

                for st in settings[s]:
                    print("EXECUTING",st.pretty())
                    run_statement(st)

    pygame.quit()
