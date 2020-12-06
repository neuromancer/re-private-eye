from collections import OrderedDict 
from lark.lexer import Token

# Dossiers

dossiers = []
dossier_next_sheet = None
dossier_previous_sheet = None

dossier_next_suspect = None
dossier_previous_suspect = None

dossier_current_sheet = None
dossier_current_suspect = None

# Savegames

load_game = None
save_game = None

# Masks

exits = []
inventory = []
masks = []

# Settings

modified = False
definitions = OrderedDict()
next_setting = None
current_setting = None
gorigin = None
started = False
settings = OrderedDict()
save_path = None
save_name = "re-private-eye-game.json" 

# Media

height = 1024
width = 768
cdrom_path = None 
video_to_play = None
sound_to_play = None
screen = None
font = None
current_view_frame = None
game_frame = "inface/general/inface2.bmp"
