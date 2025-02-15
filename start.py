from os.path import isdir, isfile
from sys import exit, argv
from time import sleep
from pathlib import Path
from random import choice
from argparse import ArgumentParser

import pygame 

import state

from media import play_video, play_sound, is_sound_playing, load_bmp, scale_point
from savegame import savegame, loadgame
from parser import game_parser
from compiler import compile_lines
from engine import run_statement, run_setflag
from cursor import load_cursors

pgv = pygame.__version__

if len(pgv) < 2 or pgv[:2] != '2.':
    print("pygame %s was found, but 2.x is required. To upgrade, run: pip3 install pygame --user --upgrade" % pgv)
    exit(-1)

def render_cursor_hand(mask, x, y, c):
    #print(c)
    if mask is None:
        return False

    if c == "NULL" or c == 0:
        return False

    (bmp, ox, oy) = mask
    xm = x - ox
    ym = y - oy

    if xm < 0 or ym < 0:
        return False

    mask = pygame.mask.from_surface(bmp)
    msize = mask.get_size()
    if (xm >= msize[0] or ym >= msize[1]):
        pass
    elif mask.get_at((xm, ym)) == 1:
        pygame.mouse.set_cursor(*state.cursors[c])

        return True

    return False

def render_dossier():

    (bmp, x, y) = state.dossier_previous_sheet
    state.screen.blit(bmp, [x, y])

    (bmp, x, y) = state.dossier_next_sheet
    state.screen.blit(bmp, [x, y])

    csus = state.dossier_current_suspect
    cshe = state.dossier_current_sheet 
    bmp = load_bmp(state.dossiers[csus][cshe])
    state.screen.blit(bmp, [x, y])

    (bmp, x, y) = state.dossier_previous_suspect
    state.screen.blit(bmp, [x, y])

    (bmp, x, y) = state.dossier_next_suspect
    state.screen.blit(bmp, [x, y])

    pygame.display.flip()
 
def set_cursor(x, y):

    # save/load masks
    if render_cursor_hand(state.load_game, x, y, "kExit"):
        return

    if render_cursor_hand(state.save_game, x, y, "kExit"):
        return

    # dossier related masks
    if render_cursor_hand(state.dossier_next_sheet, x, y, "kExit"):
        return

    if render_cursor_hand(state.dossier_previous_sheet, x, y, "kExit"):
        return
    
    if render_cursor_hand(state.dossier_next_suspect, x, y, "kExit"):
        return

    if render_cursor_hand(state.dossier_previous_suspect, x, y, "kExit"):
        return

    # sound areas
    for (bmp, _) in state.sareas:
        if render_cursor_hand((bmp, 0, 0), x, y, "kExit"):
            return

    # general masks
    for (bmp, ox, oy, _, _, c) in state.masks:
        if render_cursor_hand((bmp, ox, oy), x, y, c):
            return

    # exits
    current_exit_size = None
    selected_exit = None
    selected_cursor = None
    for (xs, ys, xe, ye, e, c) in state.exits:
        if (x>=xs and x<=xe):
            if (y>=ys and y<=ye):
                exit_size = (xs-xe)*(ys-ye)
                #print("matched", new_setting, exit_size)
                assert(exit_size > 0)
                if current_exit_size is None or exit_size < current_exit_size:
                    selected_exit = e
                    selected_cursor = c
                    current_exit_size = exit_size

    if selected_exit is not None and selected_exit != "NULL" and selected_exit != 0:
        if c != "NULL" and c != 0:
            pygame.mouse.set_cursor(*state.cursors[selected_cursor])
        return

    # default cursor
    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)


def check_for_events():
    # incoming phone call
    if state.mode == 0 and "kPhone" in state.sounds and len(state.sounds["kPhone"]) > 0:
        filename = state.phone_path + state.phone_sound
        if (not is_sound_playing()):
            play_sound(filename, 0) 
 

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

            # General masks
            for (bmp, ox, oy, new_setting, v, _) in state.masks:
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
                    oscreen = state.screen.copy()
                    state.screen.blit(bmp, [ox, oy])
                    pygame.display.flip()
                    sleep(0.2)
                    state.screen.blit(oscreen, [0, 0])
                    pygame.display.flip()
                    if new_setting != "NULL" and new_setting != 0:
                        assert(new_setting in state.settings)
                        state.next_setting = new_setting
                    if v != "NULL" and v != 0:
                        assert(v in state.definitions['variables'])
                        run_setflag(v, "TRUE")

                    return True

            # Sound Areas
            for (bmp, s) in state.sareas:
                xm = x 
                ym = y

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                print("sound area", mask.get_at((xm, ym)))
                if mask.get_at((xm, ym)) == 1:
                    if s == "kPoliceRadio":
                        ss = list(state.sounds["kPoliceRadio"].items())
                        if len(ss) > 0:
                            (s, _) = choice(list(state.sounds["kPoliceRadio"].items()))
                            filename = state.police_radio_path + s
                            play_sound(filename, 0)

                            state.played_sounds.append(s)
                            del state.sounds["kPoliceRadio"][s]
 
                    elif s == "kAMRadio":
                        ss = list(state.sounds["kAMRadio"].items())
                        if len(ss) > 0:
                            (s, _) = choice(list(state.sounds["kAMRadio"].items()))
                            filename = state.am_radio_path + s
                            play_sound(filename, 0)
                            del state.sounds["kAMRadio"][s] 

                    elif s == "kPhone":
                        ss = list(state.sounds["kPhone"].items())
                        if len(ss) > 0:
                            (s, (v, x)) = choice(list(state.sounds["kPhone"].items()))
                            filename = state.phone_path + s
                            play_sound(filename, 0)
                            if v != "NULL" and v != 0:
                                assert(v in state.definitions['variables'])
                                run_setflag(v, x)

                            state.played_sounds.append(s)
                            del state.sounds["kPhone"][s]
 
                    else:
                        print("Invalid sound added")
                        assert(False)

                    return True




            # Load/Save game
            if state.save_game is not None:
                (bmp, ox, oy) = state.save_game
                xm = x - ox
                ym = y - oy

                if xm < 0 or ym < 0:
                    return False

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                if mask.get_at((xm, ym)) == 1:
                    savegame()
                    return True

            if state.load_game is not None:
                (bmp, ox, oy) = state.load_game
                xm = x - ox
                ym = y - oy

                if xm < 0 or ym < 0:
                    return False

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                if mask.get_at((xm, ym)) == 1:
                    loadgame()
                    return True

            # Dossiers handling
            if state.dossier_next_sheet is not None:
                (bmp, ox, oy) = state.dossier_next_sheet
                xm = x - ox
                ym = y - oy

                if xm < 0 or ym < 0:
                    return False

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                print("dossier_next_sheet mask", mask.get_at((xm, ym)))
                nd = state.dossier_current_sheet + 1
                cs = state.dossier_current_suspect 
                if mask.get_at((xm, ym)) == 1:
                    if nd < len(state.dossiers[cs]) and state.dossiers[cs][nd] is not None:
                        state.dossier_current_sheet = nd
                        render_dossier()
                    return False

            if state.dossier_previous_sheet is not None:
                (bmp, ox, oy) = state.dossier_previous_sheet
                xm = x - ox
                ym = y - oy

                if xm < 0 or ym < 0:
                    return False

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                print("dossier_previous_sheet mask", mask.get_at((xm, ym)))
                pd = state.dossier_current_sheet - 1
                cs = state.dossier_current_suspect
                if mask.get_at((xm, ym)) == 1:
                    if pd >= 0 and state.dossiers[cs][pd] is not None:
                        state.dossier_current_sheet = pd
                        render_dossier()
                    return False


            if state.dossier_next_suspect is not None:
                (bmp, ox, oy) = state.dossier_next_suspect
                xm = x - ox
                ym = y - oy

                if xm < 0 or ym < 0:
                    return False

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                print("dossier_next_suspect mask", mask.get_at((xm, ym)))
                ns = state.dossier_current_suspect + 1
                if mask.get_at((xm, ym)) == 1:
                    if ns < len(state.dossiers):
                        state.dossier_current_suspect = ns
                        state.dossier_current_sheet = 0
                        render_dossier() 
                    return False

            if state.dossier_previous_suspect is not None:
                (bmp, ox, oy) = state.dossier_previous_suspect
                xm = x - ox
                ym = y - oy

                if xm < 0 or ym < 0:
                    return False

                mask = pygame.mask.from_surface(bmp)
                msize = mask.get_size()
                if (xm >= msize[0] or ym >= msize[1]):
                    continue

                print("dossier_next_suspect mask", mask.get_at((xm, ym)))
                pd = state.dossier_current_suspect - 1
                if mask.get_at((xm, ym)) == 1:
                    if pd >= 0:
                        state.dossier_current_suspect = pd
                        state.dossier_current_sheet = 0
                        render_dossier()
                    return False
  
            current_exit_size = None
            for (xs, ys, xe, ye, new_setting, _) in state.exits:
                if (x>=xs and x<=xe):
                    if (y>=ys and y<=ye):
                        exit_size = (xs-xe)*(ys-ye)
                        #print("matched", new_setting, exit_size)
                        assert(exit_size > 0)
                        if current_exit_size is None or exit_size < current_exit_size:
                            if new_setting == "NULL" or new_setting == 0:
                                state.next_setting = None
                            else:
                                state.next_setting = new_setting
                            current_exit_size = exit_size

            if current_exit_size is not None:
                return True
    return False

if __name__ == '__main__':

    # Arguments
    parser = ArgumentParser(description='re-private-eye')
    parser.add_argument("CDROM", help="Path to CDROM", type=str) 
    parser.add_argument("-height", help="Screen height", type=int, default=1024)
    parser.add_argument("-width", help="Screen height", type=int, default=768)

    options = parser.parse_args()
    state.height, state.width = options.height, options.width
    state.cdrom_path = options.CDROM

    if not isdir(state.cdrom_path):
        print(state.cdrom_path, "does not exists")
        exit(-1)

    pygame.init()
    pygame.font.init() # you have to call this at the start, 
    state.font = pygame.font.SysFont(pygame.font.get_default_font(), 70)

    # Set up the drawing window
    state.screen = pygame.display.set_mode((state.height, state.width))#, pygame.FULLSCREEN)
    state.gorigin = [0, 0]
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

    state.save_path = Path(__file__).parent.absolute() 

    state.cursors = load_cursors()

    print("Parsing game assets..")
    ls = game_parser.parse(data)
    print("Compiling assets..")
    compile_lines(ls)

    print("Executing game..")
    state.next_setting = "kIntro"
    while True:

        if check_for_events():
            pass
        elif (state.video_to_play != None):
            filename, next_setting = state.video_to_play
            play_video(filename, check_for_events)
            state.next_setting = next_setting

        if state.next_setting != None:
            state.current_setting = state.next_setting
            print("CURRENT SETTING:", state.current_setting, state.mode)
            state.exits = []
            state.masks = []
            state.sareas = []
            state.dossier_next_sheet = None
            state.dossier_previous_sheet = None
            state.dossier_next_suspect = None
            state.dossier_previous_suspect = None
            state.save_game = None
            state.load_game = None
 
            state.video_to_play = None
            state.next_setting = None

            if (state.current_setting in state.settings):
                if state.settings[state.current_setting] == []:
                    print("WARNING", state.current_setting, "is empty")
                    break

                for st in state.settings[state.current_setting]:
                    #print("EXECUTING",st.pretty())
                    run_statement(st)
            else:
                raise SyntaxError('I can\'t find setting: %s' % state.current_setting)
        
        #brighten = 32
        #screen.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_ADD)
        pygame.display.flip()
 

    pygame.quit()
