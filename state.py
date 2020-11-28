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
gorigin = [63, 48]
started = False
settings = OrderedDict()

# Media

cdrom_path = None 
video_to_play = None
sound_to_play = None
screen = None
current_view_frame = None
game_frame = "inface/general/inface2.bmp"
