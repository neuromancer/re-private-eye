from time import sleep
from ffpyplayer.player import MediaPlayer
import pygame 

import state

def load_bmp(b):
    bmp = pygame.image.load(join(state.cdrom_path, b1))
    bmp.set_colorkey((0, 255, 0))
    return bmp 

def play_video(filename, check_for_events):
    print("playing", filename)
    #filename, ns = state.video_to_play
    #state.video_to_play = None
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
 
