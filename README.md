# re-private-eye

<a href="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-1.png"><img src="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-1.png" width="170"/></a> <a href="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-2.png"><img src="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-2.png" width="170"/></a>

This open-source project aims to be a modern engine re-implementation for ["Private Eye"](https://www.mobygames.com/game/private-eye) from 1996 by Brooklyn Multimedia. The first iteration is written in Python and uses pygame and SDL2. It should run in Windows, Linux, and MacOS.

This project is open for collaboration. If you are interested, please open [an issue](https://github.com/neuromancer/re-private-eye/issues) about it.

## Current status

Barely playable: the intro, main menus  as well as some of the first scenes (they can be played). However, some important gameplay elements are missing, including:

* Save and load games.
* Dossiers.
* Diary.
* Radios.

The pointers pointers used are not the original ones, so playing the game is a litte more difficult than expected.

### Project dependencies
- Python 3
- [pygame 2](https://www.pygame.org)
- [FFPyPlayer 4.3.2](https://matham.github.io/ffpyplayer/)

To install the dependencies, just use `pip3 install pygame ffpyplayer --user`.

### Running the game
1. Mount/load the CDROM. 
2. Install the game (you will need something like `wine`). 
3. From the game directory, run `python3 start.py path/to/cdrom`
