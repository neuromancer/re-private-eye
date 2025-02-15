import pygame
from time import sleep
from os.path import join

import state
from parser import get_cname, get_statements, get_param
from compiler import compile_lines
from interpreter import resolve_expr, resolve_variable, resolve_all
from media import load_bmp, play_sound, scale_point

def run_goto(e):
    v = resolve_expr(e)
    print("goto", v, "previous value:", state.next_setting)
    state.next_setting = v 

def run_chgmode(v, e, x):
    v = resolve_expr(v)
    e = resolve_expr(e)
    if x is not None:
        x = resolve_expr(x)
 
    print("chgmode", v, e, x)
    state.next_setting = e
    state.mode = v
    if state.mode == 0:
        state.gorigin = [0, 0]
    elif state.mode == 1:
        state.gorigin = scale_point(63, 48)
    else:
        print("mode", state.mode)
        assert(False)

def run_timer(e1, e2):
    v1 = resolve_expr(e1)
    v2 = resolve_expr(e2)
    print("timer", v1, v2)
    sleep(int(v1))
    state.next_setting = v2 

def run_sound(e, loops):
    v = resolve_expr(e)
    print("sound", v)
    play_sound(v, loops)

def run_mask(m, e, c, x, y, drawn):

    m = resolve_expr(m)
    e = resolve_expr(e)
    c = resolve_expr(c)
    x = resolve_expr(x)
    y = resolve_expr(y)

    print("mask", m, e, c, x, y)
    bmp = load_bmp(m)

    if state.mode == 1:
        x,y = state.gorigin
    else:
        x,y = scale_point(x,y)

    print("mask (updated)", x, y) 
    state.masks.append((bmp, x, y, e, "NULL", c))
    if drawn:
        state.screen.blit(bmp, [x, y])
        pygame.display.flip()

def run_soundarea(m, s):

    m = resolve_expr(m)
    s = resolve_expr(s)

    print("soundarea", m, s)
    bmp = load_bmp(m)

    state.sareas.append((bmp, s))
    state.screen.blit(bmp, [0, 0])
    pygame.display.flip()

def add_sound(s, t, v, x):

    if v is not None:
        v = resolve_expr(v)

    if x is not None:
        x = resolve_expr(x)
       

    if t not in state.sounds:
        state.sounds[t] = dict()

    s = resolve_expr(s).replace('"','')
    if s == '':
        assert(x is None and v is None)
        return
    s = s + ".wav" 
    print("add_sound", s, t)
    #if s not in state.sounds[t]:
    if s not in state.played_sounds:
        state.sounds[t][s] = (v, x)

def run_loadgame(b):

    b = resolve_expr(b)
    bmp = load_bmp(b)
    state.load_game = (bmp, 0, 0)

    state.screen.blit(bmp, [0, 0])
    pygame.display.flip()

def run_savegame(b):

    b = resolve_expr(b)
    bmp = load_bmp(b)
    state.save_game = (bmp, 0, 0)

    state.screen.blit(bmp, [0, 0])
    pygame.display.flip()

def run_dossierchgsheet(b, n, x, y):

    b = resolve_expr(b)
    n = resolve_expr(n)
    x = resolve_expr(x)
    y = resolve_expr(y)
    x, y = scale_point(x,y) 
 
    bmp = load_bmp(b)

    if n == 1:
        state.dossier_next_sheet = (bmp, x, y)
    else:
        state.dossier_previous_sheet = (bmp, x, y)

    state.screen.blit(bmp, [x, y])
    pygame.display.flip()

def run_dossiernextsuspect(b, x, y):

    b = resolve_expr(b)
    x = resolve_expr(x)
    y = resolve_expr(y)
    x, y = scale_point(x,y) 
 
    bmp = load_bmp(b)
    state.dossier_next_suspect = (bmp, x, y)

    state.screen.blit(bmp, [x, y])
    pygame.display.flip()

def run_dossierprevsuspect(b, x, y):

    b = resolve_expr(b)
    x = resolve_expr(x)
    y = resolve_expr(y)
    x, y = scale_point(x,y) 
 
    bmp = load_bmp(b) 
    state.dossier_previous_suspect = (bmp, x, y)

    state.screen.blit(bmp, [x, y])
    pygame.display.flip()



def run_dossierbitmap(x, y):
    x = resolve_expr(x)
    y = resolve_expr(y)
    x, y = scale_point(x,y) 
 
    assert(state.dossier_current_sheet is not None)
    assert(state.dossier_current_suspect is not None)
    bmp = load_bmp(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet])

    state.screen.blit(bmp, [x, y])
    pygame.display.flip()

def run_dossieradd(b1, b2):

    b1 = resolve_expr(b1)
    b2 = resolve_expr(b2)
 
    #b1 = convert_path(b1)  

    if b2 != '""':
        pass #b2 = convert_path(b2) 
    else:
        b2 = None

    state.dossiers.append(( b1 , b2 ))
    if state.dossier_current_sheet is None:
        state.dossier_current_sheet = 0
        state.dossier_current_suspect = 0

def run_bitmap(e, x, y):
    if (type(x) != int):
        x = resolve_expr(x)
        x = int(x)

    if (type(y) != int):
        y = resolve_expr(y)
        y = int(y)

    v = resolve_expr(e)
    print("bitmap", v, x, y, state.screen)
    bmp = load_bmp(v)

    if state.mode == 1:
        x,y = state.gorigin
    else:
        x,y = scale_point(x,y) 
    
    state.screen.blit(bmp, [x, y])
    pygame.display.flip()

def run_setflag(f, v):
    f = resolve_expr(f)
    v = resolve_expr(v)
    if (f in state.definitions["variables"]):
        state.definitions["variables"][f] = v 
    else:
        print("flag %s not found in variable list" % f)
        assert(False)

    print("setflag", f, v)

def run_restart_game():
    for f in state.definitions["variables"]:
        if f != 'kAlternateGame':
            state.definitions["variables"][f] = 0

    #state.mode = 1
    #state.gorigin = scale_point(63, 48)

def run_setmodified(x):

    x = resolve_expr(x)
    x = resolve_variable(x)

    assert(type(x) == str or type(x) == int)
    assert(x != "0" and x != "" and x != '""' and x != "NULL")

    if (x == "FALSE"):
        state.modified = False
    elif (x == "TRUE"):
        state.modified = True
    else:
        assert(False)

def run_viewscreen(x, y):
    x = resolve_expr(x)
    y = resolve_expr(y)

def run_exit(e, x, r):
    r = resolve_expr(r)
    x = resolve_expr(x) 
    e = resolve_expr(e)

    if (r in state.definitions["rects"]):
        r = state.definitions["rects"][r]
        r = resolve_expr(r)

    (a, b, c, d) = r

    a, b = scale_point(a, b) 
    c, d = scale_point(c, d)

    a = a + state.gorigin[0]
    b = b + state.gorigin[1]
    c = c + state.gorigin[0]
    d = d + state.gorigin[1]

    state.exits.append((a, b, c, d, e, x))
    print("exit", e, r)

def run_transition(v, e):

    v = resolve_expr(v)
    e = resolve_expr(e)

    if state.mode == 1:
        state.current_view_frame = load_bmp(state.game_frame)
        state.screen.blit(state.current_view_frame, [0, 0])

    print("play transition", v)
    if (v != '""'):
        state.video_to_play = (v, e)
    else:
        assert(state.next_setting is None)
        state.next_setting = e 

def run_movie(v, e):

    v = resolve_expr(v)
    e = resolve_expr(e)

    if state.mode == 1:
        state.current_view_frame = load_bmp(state.game_frame)
        state.screen.blit(state.current_view_frame, [0, 0])

    print("play movie", v)

    if (v != '""' and v not in state.played_movies):
        state.video_to_play = (v, e)
        state.played_movies.append(v)
    elif (v == '""'):
        state.repeated_movie_exit = e
        assert(state.next_setting is None)
        state.next_setting = e 
    else:
        print("movie", v, "already played")
        state.next_setting = state.repeated_movie_exit 
 


def run_fcall(fc):
    #print(fc.children)

    name = get_cname(fc.children[0]) 
    if (name == "goto"):
        assert(len(fc.children) == 2) # 1 parameter
        run_goto(get_param(fc.children[1]))
        
    elif (name == "ChgMode"): 
        assert(len(fc.children) == 3 or len(fc.children) == 4) # 2 or 3 parameter
        v = get_param(fc.children[1])
        e = get_param(fc.children[2])
        x = None

        if len(fc.children) == 4:
            x = get_param(fc.children[3])

        run_chgmode(v, e, x) # this looks like a goto
 
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
        add_sound(get_param(fc.children[1]), "kPoliceRadio", None, None)

    elif (name == "AMRadioClip"):
        add_sound(get_param(fc.children[1]), "kAMRadio", None, None)

    elif (name == "PhoneClip"):

        v = None
        x = None 
        if len(fc.children) == 7:
            v = get_param(fc.children[5])
            x = get_param(fc.children[6])
 
        add_sound(get_param(fc.children[1]), "kPhone", v, x)

    elif (name == "SoundArea"):
        assert(len(fc.children) == 4)  # 3 parameters
        run_soundarea(get_param(fc.children[1]), get_param(fc.children[2]))

    elif (name == "ViewScreen"):
        assert(len(fc.children) == 3)  # 2 parameters
        print("ViewScreen")
        run_viewscreen(get_param(fc.children[1]), get_param(fc.children[2]))
 
    elif (name == "Transition"):
        assert(len(fc.children) == 3)  # 2 parameters
        run_transition(get_param(fc.children[1]), get_param(fc.children[2]))

    elif (name == "Exit"):
        assert(len(fc.children) == 4)  # 3 parameters
        run_exit(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]))

    elif (name == "SetFlag"):
        assert(len(fc.children) == 3)  # 2 parameters
        run_setflag(get_param(fc.children[1]), get_param(fc.children[2])) 

    elif (name == "SetModifiedFlag"):
        assert(len(fc.children) == 2)  # 1 parameter
        print("SetModifiedFlag") 
        run_setmodified(get_param(fc.children[1]))

    elif (name == "Movie"):
        assert(len(fc.children) == 3)  # 2 parameter
        print("Movie")
        run_movie(get_param(fc.children[1]), get_param(fc.children[2]))
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
        print("DossierAdd") 
        run_dossieradd(get_param(fc.children[1]), get_param(fc.children[2]))

    elif (name == "DossierChgSheet"):
        assert(len(fc.children) == 5)  # 4 parameters
        print("DossierChgSheet")
        run_dossierchgsheet(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), get_param(fc.children[4])) 

    elif (name == "DossierBitmap"):
        assert(len(fc.children) == 3)  # 2 parameters
        print("DossierChgSheet")
        run_dossierbitmap(get_param(fc.children[1]), get_param(fc.children[2])) 

    elif (name == "DossierPrevSuspect"):
        assert(len(fc.children) == 4)  # 3 parameters
        print("DossierPrevSuspect")
        run_dossierprevsuspect(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3])) 

    elif (name == "DossierNextSuspect"):
        assert(len(fc.children) == 4)  # 3 parameters
        print("DossierNextSuspect")
        run_dossiernextsuspect(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3])) 

    elif (name == "DiaryLocList"):
        print("DiaryLocList (skip)")
 
    elif (name == "DiaryGoLoc"):
        print("DiaryGoLoc (skip)")
 
    elif (name == "DiaryInvList"):
        print("DiaryInvList (skip)")
    
    elif (name == "AskSave"): 
        assert(len(fc.children) == 3) # 2 parameters
        print("AskSave")
        # No time to ask, let's go for the first option
        run_goto(get_param(fc.children[1]))

    elif (name == "LoadGame"): 
        assert(len(fc.children) == 4) # 3 parameters
        print("LoadGame")
        run_loadgame(get_param(fc.children[1]))
 
    elif (name == "SaveGame"): 
        assert(len(fc.children) == 3) # 2 parameters
        print("SaveGame") 
        run_savegame(get_param(fc.children[1]))
 
    elif (name == "Inventory"): 
        assert(len(fc.children) == 10) # 9 parameters
        print("Inventory")
        run_inventory(get_param(fc.children[1]), get_param(fc.children[2]), get_param(fc.children[3]), get_param(fc.children[4]), get_param(fc.children[5]), get_param(fc.children[6]), get_param(fc.children[7]), get_param(fc.children[8]), get_param(fc.children[9]) ) 

    else:
        raise SyntaxError('I don\'t know how to exec: %s' % fc)

def run_inventory(b1, v1, v2, e, b2, b3, b, c, snd):

    [b1, v1, v2, e, b2, b3, snd] = resolve_all([b1, v1, v2, e, b2, b3, snd])
    print("inventory", b1, v1, v2, e, b2, b3, snd) 

    if b3 == '"REMOVE"':
        found = False
        for i,(_ , _, _, _, bi) in enumerate(state.inventory):
            if bi == b2:
                found = True
                state.inventory.pop(i)
                break

        assert(found)

    if v1 != '""':
        run_setflag(v1, "TRUE")

    if b1 != '""': 
        bmp = load_bmp(b1)
        x,y = state.gorigin 
        state.screen.blit(bmp, [x, y])
        pygame.display.flip()
        state.masks.append((bmp, x, y, e, v2, "kInventory"))
 
    state.inventory.append((b1, v1, v2, e, b2, b3))
    if snd != '""':
        play_sound(snd, 0)

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

