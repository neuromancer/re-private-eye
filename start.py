from os.path import isdir, isfile, join
from sys import exit, argv
from time import sleep

#from lark.lexer import Token
#from collections import OrderedDict 
from ffpyplayer.player import MediaPlayer
import pygame 

import state

from savegame import savegame, loadgame
from parser import game_parser
from compiler import compile_lines
from engine import run_statement

pgv = pygame.__version__

if len(pgv) < 2 or pgv[:2] != '2.':
    print("pygame %s was found, but 2.x is required. To upgrade, run: pip3 install pygame --user --upgrade" % pgv)
    exit(-1)

def set_cursor(x, y):
    #global state.exits
    #global state.masks

    # save/load masks
    if state.load_game is not None:
        (bmp, ox, oy) = state.load_game
        xm = x - ox
        ym = y - oy

        if xm < 0 or ym < 0:
            return False

        mask = pygame.mask.from_surface(bmp)
        msize = mask.get_size()
        if (xm >= msize[0] or ym >= msize[1]):
            pass
        elif mask.get_at((xm, ym)) == 1:
            #screen.blit(bmp, [ox, oy])
            #pygame.display.flip()
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
            return True

    # dossier masks
    if state.dossier_next_sheet is not None:
        (bmp, ox, oy) = state.dossier_next_sheet
        xm = x - ox
        ym = y - oy

        if xm < 0 or ym < 0:
            return False

        mask = pygame.mask.from_surface(bmp)
        msize = mask.get_size()
        if (xm >= msize[0] or ym >= msize[1]):
            pass
        elif mask.get_at((xm, ym)) == 1:
            #screen.blit(bmp, [ox, oy])
            #pygame.display.flip()
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
            return

    if state.dossier_previous_sheet is not None:
        (bmp, ox, oy) = state.dossier_previous_sheet
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
            return

    if state.dossier_next_suspect is not None:
        (bmp, ox, oy) = state.dossier_next_suspect
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
            return

    if state.dossier_previous_suspect is not None:
        (bmp, ox, oy) = state.dossier_previous_suspect
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
            return

    # general masks
    for (bmp, ox, oy, _) in state.masks:
        mask = pygame.mask.from_surface(bmp)
        msize = mask.get_size()
        xm = x - ox
        ym = y - oy

        if xm < 0 or ym < 0:
            continue

        if (xm >= msize[0] or ym >= msize[1]):
            continue

        if mask.get_at((xm, ym)) == 1:
            state.screen.blit(bmp, [ox, oy])
            #pygame.display.flip()
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
            return

    if state.started:
        x = x - state.gorigin[0]
        y = y - state.gorigin[1]

    for (xs, ys, xe, ye, _) in state.exits:
        if (x>=xs and x<=xe):
            if (y>=ys and y<=ye):
                pygame.mouse.set_cursor(*pygame.cursors.diamond)
                return

    # default cursor
    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)


def check_for_events():
    #global state.exits
    #global state.masks
    #global state.next_setting
    #global state.origin
    #global state.dossier_current_sheet
    #global state.dossier_current_suspect

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
                    state.screen.blit(bmp, [ox, oy])
                    pygame.display.flip()
                    #if(state.next_setting is not None):
                    #    assert(next_setting == new_setting)
                    state.next_setting = new_setting
                    state.masks = [] # TODO: check if this is necessary here
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
                        state.screen.blit(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet], [ox, oy])
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
                        state.screen.blit(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet], [ox, oy])
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
                        state.screen.blit(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet], [ox, oy])
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
                        state.screen.blit(state.dossiers[state.dossier_current_suspect][state.dossier_current_sheet], [ox, oy])
                        state.screen.blit(bmp, [ox, oy]) 
                        pygame.display.flip()
                    return False
  
            if state.started:
                x = x - state.gorigin[0]
                y = y - state.gorigin[1]

            for (xs, ys, xe, ye, new_setting) in state.exits:
                if (x>=xs and x<=xe):
                    if (y>=ys and y<=ye):
                        #if next_setting is not None:
                        #    assert(next_setting == new_setting)
                        state.next_setting = new_setting
                        state.exits = [] # TODO: check if this is necessary
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

    # Set up the drawing window
    state.screen = pygame.display.set_mode([640, 480])
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
    compile_lines(ls)

    print("Executing game..")
    state.next_setting = "kIntro" #Movie"
    while True:

        if check_for_events():
            pass
        elif (state.video_to_play != None):
            print("playing", state.video_to_play)
            filename, ns = state.video_to_play
            state.video_to_play = None
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
                    state.screen.blit(surf, [state.gorigin[0], state.gorigin[1]])

                # Flip the display
                pygame.display.flip()
            
            state.next_setting = ns


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
