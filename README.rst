==========================
(yet again) Falling Blocks
==========================

This is a falling block game (see Tetris or Columns) developed from scratch
in a weekend to learn about Pyglet.

The mechanics are pretty much like in Columns, although blocks can't be matched
in diagonal (making the game a little bit more difficult).

If a joystick / gamepad is present it will be used instead of the keyboard.


Controls
========

Keyboard:

 - Up: up arrow
 - Down: down arrow, speed the block
 - Left: left arrow
 - Right: right arrow
 - Action: space, swap blocks
 - Pause: p
 - Escape: esc

Joystick / Gamepad (when available):

 - Up: up
 - Down: down, speed the block
 - Left: left
 - Right: right
 - Action: button 1, swap blocks
 - Pause: button 3
 - Escape: button 4


Install
=======

 - Python 2.7
 - Pyglet 1.2 (alpha1)
 - AVbin (version 11 recommended, specially in Linux)

You don't need to install the game, just run the *yafb* script in the
"scripts" directory.

If you really want to install the game you'll need setuptools. Try running:

    python setup.py install

To install the alpha version of Pyglet 1.2 you can run:

    pip install http://pyglet.googlecode.com/files/pyglet-1.2alpha1.tar.gz

I recommend you to use virtualenv.


License
=======

This is free software under the terms of MIT license (check COPYING file
included in this package).

Music: "Fatigue" by Zerosum.


Author
======

- Juan J. Martínez <jjm@usebox.net>

