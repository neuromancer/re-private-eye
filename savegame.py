from time import sleep
from os.path import isfile

import json
import state
import pygame

from media import scale_point

def savegame():
    if not state.modified:
        return

    assert(state.mode == 0)
    oscreen = state.screen.copy()
    bmp = state.font.render('Saving..', False, (0, 200, 255))
    state.screen.blit(bmp, [(state.height-bmp.get_size()[0])/2., (state.width-bmp.get_size()[1])/2.])
    pygame.display.flip()
 
    path = str(state.save_path) + "/" +state.save_name 
    with open(path, "w") as fp:
        game = dict()
        game['variables'] = state.definitions['variables']
        game['inventory'] = state.inventory
        game['sounds'] = state.sounds
        game['played_sounds'] = state.played_sounds
        game['played_movies'] = state.played_movies 
        game['repeated_movie_exit'] = state.repeated_movie_exit
        game['dossiers'] = state.dossiers
        game['dossier_current_sheet'] = state.dossier_current_sheet
        game['dossier_current_suspect'] = state.dossier_current_suspect

        json.dump(game,fp) 

    sleep(1)
    state.screen.blit(oscreen, [0, 0])
    pygame.display.flip()

def loadgame():

    path = str(state.save_path) + "/" + state.save_name
    found = isfile(path)

    oscreen = state.screen.copy()
    if found:
        bmp = state.font.render('Loading..', False, (0, 200, 255))
        pygame.mixer.stop()
    else:
        bmp = state.font.render('Failed to load ' + state.save_name, False, (0, 200, 255))
 
    state.screen.blit(bmp, [(state.height-bmp.get_size()[0])/2., (state.width-bmp.get_size()[1])/2.])
    pygame.display.flip()
    sleep(1)
    state.screen.blit(oscreen, [0, 0])
    pygame.display.flip()

    if not found:
        return

    with open(path, "r") as fp:
        game = json.load(fp)
        state.definitions['variables'] = game['variables']
        state.sounds = game['sounds']  
        state.played_sounds = game['played_sounds']
        state.played_movies = game['played_movies']
        state.repeated_movie_exit = game['repeated_movie_exit']
        state.inventory = game['inventory'] 
        state.dossiers = game['dossiers']
        state.dossier_current_sheet = game['dossier_current_sheet']
        state.dossier_current_suspect = game['dossier_current_suspect']

        state.modified = True
        state.next_setting = "kMainDesktop"
