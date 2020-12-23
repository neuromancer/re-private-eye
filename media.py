from time import sleep
from os.path import join

from ffpyplayer.player import MediaPlayer
import pygame 

import state

def convert_path(p):
    p = p.lower()
    p = p.replace('"','')
    return p.replace("\\","/")

def scale_point(x, y):
    return (int(x * state.height  / 640.) , int(y * state.width / 480.))

def load_bmp(b):

    bmp = pygame.image.load(join(state.cdrom_path, convert_path(b)))
    bmp.set_colorkey((0, 255, 0))
    h,w = bmp.get_size() 
    bmp = pygame.transform.scale2x(bmp)
    
    if (h,w) == (640, 480):
        bmp = pygame.transform.scale(bmp, (state.height, state.width))
    else:
        bmp = pygame.transform.scale(bmp, scale_point(h, w) )
 
    return bmp 

def play_video(filename, check_for_events):
    filename = join(state.cdrom_path, convert_path(filename))
    print("playing", filename)
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
            surf = pygame.transform.scale(surf, (state.height-2*state.gorigin[0], state.width-2*state.gorigin[1]))
 
            sleep(val)
            state.screen.blit(surf, [state.gorigin[0], state.gorigin[1]])

        # Flip the display
        pygame.display.flip()

def is_sound_playing():
    return pygame.mixer.get_busy()

def play_sound(f, l):
    print("playing", f)
    if f == '""':
        pygame.mixer.stop()
    else:
        pygame.mixer.stop()
        sound = pygame.mixer.Sound(join(state.cdrom_path, convert_path(f)))
        sound.play(l)
