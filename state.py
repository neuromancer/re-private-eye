from collections import OrderedDict 
from lark.lexer import Token

cdrom_path = None 
definitions = OrderedDict()
dossiers = []
dossier_next_sheet = None
dossier_previous_sheet = None

dossier_next_suspect = None
dossier_previous_suspect = None

dossier_current_sheet = None
dossier_current_suspect = None

exits = []
inventory = []
masks = []
next_setting = None
current_setting = None
gorigin = [63, 48]
started = False
settings = OrderedDict()
video_to_play = None
sound_to_play = None
screen = None
current_view_frame = None
game_frame = "inface/general/inface2.bmp"
