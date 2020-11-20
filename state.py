from collections import OrderedDict 
from lark.lexer import Token

cdrom_path = None 
definitions = OrderedDict()
exits = []
inventory = []
masks = []
next_setting = None
origin = [0, 0]
settings = OrderedDict()
video_to_play = None
sound_to_play = None
screen = None
current_view_frame = None
game_frame = "inface/general/inface2.bmp"
