# re-private-eye

<a href="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-1.png"><img src="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-1.png" width="170"/></a> <a href="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-2.png"><img src="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-2.png" width="170"/></a> <a href="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-3.png"><img src="https://raw.githubusercontent.com/neuromancer/re-private-eye/main/screen-3.png" width="170"/></a>

This open-source project aims to be a modern engine re-implementation for ["Private Eye"](https://www.mobygames.com/game/private-eye) from 1996 by Brooklyn Multimedia. The first iteration is written in Python and uses pygame and SDL2. It should run in Windows, Linux, and MacOS.

This project is open for collaboration. If you are interested, please open [an issue](https://github.com/neuromancer/re-private-eye/issues) about it.

## Current status

Barely playable: the intro, main menus as well as some of the first scenes (they can be played). However, some important gameplay elements are missing, including:

* Save and load games.
* Diary.
* Radios.

Additionally, the mouse pointers used are not the original ones, so playing the game is a litte more difficult than expected.

### Project dependencies
- Python 3
- [lark](https://github.com/lark-parser/lark)
- [pygame 2](https://www.pygame.org)
- [FFPyPlayer 4.3.2](https://matham.github.io/ffpyplayer/)

To install the dependencies, just use `pip3 install lark pygame ffpyplayer --user --upgrade`.

## Playing with the engine

### Using the full game:

1. Mount/load the CDROM. 
2. Install the game (you can use `wine` or just extract `support/assets.z` using [unshieldv3](https://github.com/wfr/unshieldv3)).
3. From the game directory where it was installed, run `python3 start.py path/to/cdrom`

### Using the demo:

If you don't own the full game, you can still play with this engine using [the free demo](https://archive.org/details/PrivateEye_1020) following these steps:

```
mkdir demo
cd demo
wget "https://archive.org/download/PrivateEye_1020/PVT_DEMO.zip"
unzip -LL PVT_DEMO.zip
git clone https://github.com/wfr/unshieldv3
cd unshieldv3
qmake .
make
cd ..
mkdir assets
./unshieldv3/unshieldv3 extract support/assets.z assets/
python ../start.py .
```
