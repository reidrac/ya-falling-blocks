"""
Control classes
"""

from pyglet.window import key
from pyglet import input

class Keyboard(object):
    """
    Keyboard controller
    """

    def __init__(self, window):
        self.keys = key.KeyStateHandler()
        window.push_handlers(self.keys)

    @property
    def up(self):
        return self.keys[key.UP]

    @property
    def down(self):
        return self.keys[key.DOWN]

    @property
    def left(self):
        return self.keys[key.LEFT]

    @property
    def right(self):
        return self.keys[key.RIGHT]

    @property
    def action(self):
        return self.keys[key.SPACE] or self.keys[key.ENTER]

    @property
    def escape(self):
        return self.keys[key.ESCAPE]

    @property
    def pause(self):
        return self.keys[key.P]

class Joystick(object):
    """
    Joystick controller
    """

    @staticmethod
    def get_joysticks():
        return  input.get_joysticks()

    def __init__(self, joystick):
        self.buttons = {}
        self.joystick = joystick
        self.joystick.open()

    @property
    def up(self):
        return self.joystick.y == -1

    @property
    def down(self):
        return self.joystick.y == 1

    @property
    def left(self):
        return self.joystick.x == -1

    @property
    def right(self):
        return self.joystick.x == 1

    @property
    def action(self):
        return self.joystick.buttons[0]

    @property
    def escape(self):
        return self.joystick.buttons[3]

    @property
    def pause(self):
        return self.joystick.buttons[2]

