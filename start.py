from os.path import isdir, isfile, join
from sys import exit, argv
from time import sleep
from random import random

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

def run_goto(e):
    global next_setting
    v = resolve_expr(e)
    print("goto", v, "previous value:", next_setting)
    #assert(next_setting is None)
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
        sound = pygame.mixer.Sound(join(cdrom_path, convert_path(v)))
        sound.play(loops)

def run_mask(m, e, v, x, y, drawn):
    m = resolve_expr(m)
    e = resolve_expr(e)
    v = resolve_expr(v)
    x = resolve_expr(x)
    y = resolve_expr(y)

    global cdrom_path
    global masks
    global screen

    print("mask", m, e, v, x, y)

    bmp = pygame.image.load(join(cdrom_path, convert_path(m)))
    bmp.set_colorkey((0, 255, 0))

    if bmp.get_size() == (640, 480):
        assert(x == 0 and y == 0)
    else:
        if x == 0 and y == 0:
            x,y = gorigin

    masks.append((bmp, x, y, e))
    if drawn:
        screen.blit(bmp, [x, y])
        pygame.display.flip()

def run_bitmap(e, x, y):
    if (type(x) != int):
        x = resolve_expr(x)
        x = int(x)

    if (type(y) != int):
        y = resolve_expr(y)
        y = int(y)

    global cdrom_path
    global screen

    v = resolve_expr(e)
    print("bitmap", v, x, y, screen)
    bmp = pygame.image.load(join(cdrom_path, convert_path(v)))
    bmp.set_colorkey((0, 255, 0))

    if bmp.get_size() == (640, 480):
        assert(x == 0 and y == 0)
        screen.blit(bmp, [0, 0])
    else:
        if x == 0 and y == 0:
            x,y = gorigin
        
        screen.blit(bmp, [x, y])

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
    if (f in definitions["variables"]):
        definitions["variables"][f] = v 
    else:
        print("flag %s not found in variable list" % f)
        assert(False)

    print("setflag", f, v)

def run_restart_game():
    global started
    started = True

def run_viewscreen(x, y):
    x = resolve_expr(x)
    y = resolve_expr(y)

def run_exit(e, r):
    global origin
    r = resolve_expr(r)
    e = resolve_expr(e)
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
    global next_setting

    v = resolve_expr(v)
    e = resolve_expr(e)

    if started:
        current_view_frame = pygame.image.load(join(cdrom_path, game_frame))
        screen.blit(current_view_frame, [0, 0])

    print("play", v)
    if (v != '""'):
        video_to_play = (join(cdrom_path, convert_path(v)), e)
    else:
        assert(next_setting is None)
        next_setting = e 

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
        assert(len(fc.children) == 4 or len(fc.children) == 3) # 2 or 3 parameters
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
        assert(len(fc.children) == 4 or len(fc.children) == 6)  # 3 or 5 parameters
        x = 0
        y = 0

        if len(fc.children) == 6:
            x = get_param(fc.children[4])
            y = get_param(fc.children[5])

        run_mask(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), x, y, False)

    elif (name == "MaskDrawn"):
        assert(len(fc.children) == 4)  # 3 parameters
        run_mask(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), 0, 0, True)
 
    elif (name == "Sound"):
        assert(len(fc.children) == 2 or len(fc.children) == 4 or len(fc.children) == 5)  # 1, 3 or 4 parameters
        run_sound(get_param(fc.children[1]), 0)

    elif (name == "SoundEffect"):
        assert(len(fc.children) == 2)  # 1 parameter
        run_sound(get_param(fc.children[1]), 0)

    elif (name == "PaperShuffleSound"):
        assert(len(fc.children) == 1)  # no parameters
        print("PaperShuffleSound (no op for now)")  
        #run_sound(get_param(fc.children[1]), 0)

    elif (name == "SyncSound"):
        assert(len(fc.children) == 3)  # 2 parameter
        run_goto(get_param(fc.children[2]))

    elif (name == "NoStopSounds"):
        assert(len(fc.children) == 1)  # no parameters
        print("NoStopSounds (no op for now)")  
        #run_sound(get_param(fc.children[1]), 0)

    elif (name == "LoopedSound"):
        assert(len(fc.children) == 2)  # 1 or 3 parameters
        run_sound(get_param(fc.children[1]), -1)

    # clips

    elif (name == "PoliceClip"):
        pass

    elif (name == "AMRadioClip"):
        pass

    elif (name == "PhoneClip"):
        pass

    elif (name == "SoundArea"):
        assert(len(fc.children) == 4)  # 3 parameters
        run_mask(get_param(fc.children[1]), 0, get_param(fc.children[3]), 0, 0, True)

    elif (name == "ViewScreen"):
        assert(len(fc.children) == 3)  # 2 parameters
        print("ViewScreen")
        run_viewscreen(get_param(fc.children[1]), get_param(fc.children[2]))
 
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
        print("RestartGame (unclear)") 

    elif (name == "PoliceBust"): 
        print("PoliceBust (no op for now)")
        #assert(False)
 
    elif (name == "DossierAdd"): 
        assert(len(fc.children) == 3) # 2 parameters
        print("DossierAdd (no op for now)") 

    elif (name == "LoadGame"): 
        assert(len(fc.children) == 4) # 3 parameters
        print("LoadGame (no op for now)") 

    elif (name == "SaveGame"): 
        assert(len(fc.children) == 3) # 2 parameters
        print("SaveGame (no op for now)") 

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

    assert(type(v) == str or type(v) == int)
    assert(v != "0" and v != "" and v != '""' and v != "NULL")

    if (v == "FALSE" or v == 0):
        if (ie.children[2].data) == "statements":
            run_statements(ie.children[2])
        elif (ie.children[2].data) == "statement":
            run_statement(ie.children[2])
 
    else:
        print("TRUE!")
        if (ie.children[1].data) == "statements":
            run_statements(ie.children[1])
        elif (ie.children[1].data) == "statement":
            run_statement(ie.children[1])


def run_if(i):
    assert(i.data == "if")
    assert(len(i.children) == 2)

    v = resolve_expr(i.children[0])
    v = resolve_variable(v)
    if (v is None):
        print("Uninitialized variable %s" % v)
        assert(False)

    assert(type(v) == str or type(v) == int)
    assert(v != "0" and v != "" and v != '""' and v != "NULL")

    if (v != "FALSE" and v != 0):
        print("TRUE!")
        if (i.children[1].data) == "statements":
            run_statements(i.children[1])
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
    else:
        raise SyntaxError('I don\'t know how to run: %s' % s)

def set_cursor(x, y):
    global exits
    global masks

    for (bmp, ox, oy, _) in masks:
        mask = pygame.mask.from_surface(bmp)
        msize = mask.get_size()
        xm = x - ox
        ym = y - oy

        if xm < 0 or ym < 0:
            continue

        if (xm >= msize[0] or ym >= msize[1]):
            continue

        if mask.get_at((xm, ym)) == 1:
            screen.blit(bmp, [ox, oy])
            #pygame.display.flip()
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
            return

    if started:
        x = x - gorigin[0]
        y = y - gorigin[1]

    for (xs, ys, xe, ye, _) in exits:
        if (x>=xs and x<=xe):
            if (y>=ys and y<=ye):
                pygame.mouse.set_cursor(*pygame.cursors.diamond)
                return

    # default cursor
    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)


def check_for_events():
    global exits
    global masks
    global next_setting
    global origin

    (x,y) = pygame.mouse.get_pos()
    set_cursor(x,y)

    for event in pygame.event.get():


        # Did the user click the window close button?
        if event.type == pygame.QUIT:
            exit(0)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            x,y = event.pos

            for (bmp, ox, oy, new_setting) in masks:
                xm = x - ox
                ym = y - oy

                if xm < 0 or ym < 0:
                    return False

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                print("mask", mask.get_at((xm, ym)))
                if mask.get_at((xm, ym)) == 1:
                    screen.blit(bmp, [ox, oy])
                    pygame.display.flip()
                    if(next_setting is not None):
                        assert(next_setting == new_setting)
                    next_setting = new_setting
                    masks = []
                    return True
        
            if started:
                x = x - gorigin[0]
                y = y - gorigin[1]

            for (xs, ys, xe, ye, new_setting) in exits:
                if (x>=xs and x<=xe):
                    if (y>=ys and y<=ye):
                        #if next_setting is not None:
                        #    assert(next_setting == new_setting)
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

    if not isdir(cdrom_path):
        print(cdrom_path, "does not exists")
        exit(-1)

    pygame.init()

    # Set up the drawing window
    screen = pygame.display.set_mode([640, 480])
    pygame.display.set_caption("Private Eye (1996) re-implementation")

    data = None
    if isfile('assets/GAME.DAT'):
        with open('assets/GAME.DAT') as f:
            data = f.read()
    
    if isfile('assets/GAME.TXT'):
        with open('assets/GAME.TXT') as f:
            data = f.read()

    if data is None:
        print("Cannot find full game (assets/GAME.DATA) or demo (assets/GAME.TXT)")
        exit(-1)

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

        if check_for_events():
            pass
        elif (video_to_play != None):
            print("playing", video_to_play)
            filename, ns = video_to_play
            video_to_play = None
            player = MediaPlayer(filename)
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
                    screen.blit(surf, [gorigin[0], gorigin[1]])

                # Flip the display
                pygame.display.flip()
            
            next_setting = ns


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
            else:
                raise SyntaxError('I can\'t find setting: %s' % s)
        
        #brighten = 32
        #screen.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_ADD)
        pygame.display.flip()
 

    pygame.quit()
