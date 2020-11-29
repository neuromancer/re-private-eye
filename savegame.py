import json
import state

def savegame():
    if not state.modified:
        return

    with open("re-private-eye-game.json", "w") as fp:
        game = dict()
        game['variables'] = state.definitions['variables']
        game['inventory'] = state.inventory
        game['dossiers'] = state.dossiers 
        json.dump(game,fp) 

def loadgame():
    with open("re-private-eye-game.json", "r") as fp:
        game = json.load(fp)
        state.definitions['variables'] = game['variables']
        state.inventory = game['inventory'] 
        state.dossiers = game['dossiers']
        state.started = True
        state.modified = True
        state.next_setting = "kMainDesktop"
