# re-private-eye

<a href="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen.png"><img src="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen.png" width="350"/></a>

This open-source project aims to be a modern engine re-implementation for ["Private Eye"](https://www.mobygames.com/game/private-eye) from 1996 by Brooklyn Multimedia. The first iteration is written in Python and uses pygame and SDL2. It should run in Windows, Linux, and macOS.

This project is open for collaboration. If you are interested, please open [an issue](https://github.com/neuromancer/re-private-eye/issues) about it.

## Current status

No actual gameplay yet, but intro and main menu are working, as well as some scenes. A large amount of the gameplay elements are missing, including pointers showing where you can click, so it is difficult to play right now.

### Project dependencies
- Python 3
- [pygame 2](https://www.pygame.org)
- [FFPyPlayer 4.3.2](https://matham.github.io/ffpyplayer/)

To install the dependencies, just use `pip3 install pygame ffpyplayer --user`.

### Running the game
1. Mount/load the CDROM. 
2. Install the game (you will need something like `wine`). 
3. From the game directory, run `python3 start.py path/to/cdrom`
