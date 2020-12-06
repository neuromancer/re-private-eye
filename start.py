from os.path import isdir, isfile
from sys import exit, argv
from time import sleep
from pathlib import Path

import pygame 

import state

from media import play_video, load_bmp, scale_point
from savegame import savegame, loadgame
from parser import game_parser
from compiler import compile_lines
from engine import run_statement

pgv = pygame.__version__

if len(pgv) < 2 or pgv[:2] != '2.':
    print("pygame %s was found, but 2.x is required. To upgrade, run: pip3 install pygame --user --upgrade" % pgv)
    exit(-1)

def render_cursor_hand(mask, x, y):
    if mask is None:
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
        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        return True

    return False


def set_cursor(x, y):

    # save/load masks
    if render_cursor_hand(state.load_game, x, y):
        return

    if render_cursor_hand(state.save_game, x, y):
        return

    # dossier related masks
    if render_cursor_hand(state.dossier_next_sheet, x, y):
        return

    if render_cursor_hand(state.dossier_previous_sheet, x, y):
        return
    
    if render_cursor_hand(state.dossier_next_suspect, x, y):
        return

    if render_cursor_hand(state.dossier_previous_suspect, x, y):
        return

    # general masks
    for (bmp, ox, oy, _) in state.masks:
        if render_cursor_hand((bmp, ox, oy), x, y):
            return

    if state.started:
        x = x - state.gorigin[0]
        y = y - state.gorigin[1]

    # exits
    for (xs, ys, xe, ye, _) in state.exits:
        if (x>=xs and x<=xe):
            if (y>=ys and y<=ye):
                pygame.mouse.set_cursor(*pygame.cursors.diamond)
                return

    # default cursor
    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)


def check_for_events():
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
            for (bmp, ox, oy, new_setting) in state.masks:
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
                    #if(state.next_setting is not None):
                    #    assert(next_setting == new_setting)
                    state.next_setting = new_setting
                    #state.masks = [] # TODO: check if this is necessary here
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
                if mask.get_at((xm, ym)) == 1:
                    if nd < len(state.dossiers[state.dossier_current_suspect]) and state.dossiers[state.dossier_current_suspect][nd] is not None:
                        state.dossier_current_sheet = nd
                        bmp = load_bmp(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet])
                        state.screen.blit(bmp, [ox, oy])
                        pygame.display.flip()
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
                nd = state.dossier_current_sheet - 1
                if mask.get_at((xm, ym)) == 1:
                    if nd >= 0 and state.dossiers[state.dossier_current_suspect][nd] is not None:
                        state.dossier_current_sheet = nd
                        bmp = load_bmp(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet]) 
                        state.screen.blit(bmp, [ox, oy])
                        pygame.display.flip()
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
                nd = state.dossier_current_suspect + 1
                if mask.get_at((xm, ym)) == 1:
                    if nd < len(state.dossiers):
                        state.dossier_current_suspect = nd
                        state.dossier_current_sheet = 0
                        bmp = load_bmp(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet]) 
                        state.screen.blit(bmp, [ox, oy])
                        pygame.display.flip()
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
                nd = state.dossier_current_suspect - 1
                if mask.get_at((xm, ym)) == 1:
                    if nd >= 0:
                        state.dossier_current_suspect = nd
                        state.dossier_current_sheet = 0
                        bmp = load_bmp(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet]) 
                        state.screen.blit(bmp, [ox, oy])
                        pygame.display.flip()
                    return False
  
            if state.started:
                x = x - state.gorigin[0]
                y = y - state.gorigin[1]

            current_exit_size = None
            for (xs, ys, xe, ye, new_setting) in state.exits:
                if (x>=xs and x<=xe):
                    if (y>=ys and y<=ye):
                        exit_size = (xs-xe)*(ys-ye)
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

    if (len(argv) == 2):
        state.cdrom_path = argv[1]
    else:
        print("A path to the CDROM files is required")
        exit(-1)

    if not isdir(state.cdrom_path):
        print(state.cdrom_path, "does not exists")
        exit(-1)

    pygame.init()
    pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
    state.font = pygame.font.SysFont(pygame.font.get_default_font(), 70)

    # Set up the drawing window
    state.screen = pygame.display.set_mode((state.height, state.width))#, pygame.FULLSCREEN)
    state.gorigin = scale_point(0, 0)
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

    print("Parsing game assets..")
    ls = game_parser.parse(data)
    print("Compiling assets..")
    compile_lines(ls)

    print("Executing game..")
    state.next_setting = "kIntro" #Movie"
    while True:

        if check_for_events():
            pass
        elif (state.video_to_play != None):
            filename, next_setting = state.video_to_play
            play_video(filename, check_for_events)
            state.next_setting = next_setting

        if state.next_setting != None:
            state.current_setting = state.next_setting
            print("CURRENT SETTING:", state.current_setting)
            state.exits = []
            state.masks = []
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
                    print("EXECUTING",st.pretty())
                    run_statement(st)
            else:
                raise SyntaxError('I can\'t find setting: %s' % state.current_setting)
        
        #brighten = 32
        #screen.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_ADD)
        pygame.display.flip()
 

    pygame.quit()
