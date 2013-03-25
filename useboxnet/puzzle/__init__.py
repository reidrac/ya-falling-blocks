import os
import gc
import logging
from argparse import ArgumentParser

import pyglet

# pyglet setup
pyglet.options['debug_gl'] = False
DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
pyglet.resource.path.append(DATA_PATH)

from pyglet.window import Window

from useboxnet.puzzle.const import PROJECT_DESC, PROJECT_URL, VERSION, WIDTH, HEIGHT, AUDIO_DRIVERS
from useboxnet.puzzle.control import Keyboard, Joystick
from useboxnet.puzzle.scenes import Menu, Game

# set some sane audio defaults (Linux)
pyglet.options['audio'] = AUDIO_DRIVERS

class Main(Window):

    def __init__(self):
        """Process cli arguments and setup the game"""
        parser = ArgumentParser(description=PROJECT_DESC,
                                epilog='Project home: ' + PROJECT_URL,
                                )

        parser.add_argument("--version", action="version", version="%(prog)s "  + VERSION)
        parser.add_argument("-f", "--fullscreen", dest="fullscreen", action="store_true",
                            help="run the application in full screen mode"
                            )
        parser.add_argument("-a", "--audio", dest="audio_driver", type=str, default="default",
                            help="audio driver to use in: %s" % ', '.join(AUDIO_DRIVERS))
        parser.add_argument("-k", "--keyboard", dest="keyboard", action="store_true", help="use the keyboard even if a joystick is present")
        parser.add_argument("-d", "--debug", dest="debug", action="store_true")

        self.args = parser.parse_args()

        if self.args.debug:
            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Debug enabled")
            logging.debug("Options: %s" % self.args)

        if self.args.audio_driver in AUDIO_DRIVERS:
            pyglet.options['audio'] = (self.args.audio_driver,)

        conf = pyglet.gl.Config()
        conf.double_fuffer = True

        super(Main, self).__init__(visible=False,
                                   width=WIDTH,
                                   height=HEIGHT,
                                   config=conf,
                                   fullscreen=self.args.fullscreen,
                                   caption=PROJECT_DESC,
                                   )

        try:
            # only tested in Linux, may fail in other platforms
            self.set_icon(pyglet.resource.image("piece0.png"))
        except:
            pass

        if self.args.debug:
            self.fps = pyglet.clock.ClockDisplay()

        self.set_visible()

        joysticks = Joystick.get_joysticks()
        if joysticks and not self.args.keyboard:
            logging.debug("Joystick found, using: %s" % joysticks[0].device.name)
            self.control = Joystick(joysticks[0])
        else:
            logging.debug("Using keyboard")
            self.control = Keyboard(self)
        self.scene = Menu(self.control, self.change_scene)

        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

        # for images with transparent parts
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

    def change_scene(self, scene):
        """Used from scenes"""
        if scene == "game":
            self.scene.close()
            self.scene = Game(self.control, self.change_scene)
        elif scene == "menu":
            self.scene.close()
            self.scene = Menu(self.control, self.change_scene)
        else: # exit game
            self.close()

    def update(self, dt):
        """Update scene state"""
        self.scene.update(dt)

    def on_key_press(self, symbol, mods):
        """Remove the default handler, disables escape -> close"""
        pass

    def on_close(self):
        """The app is being terminated"""
        self.scene.close()
        # avoid a crash on windows - issue #636
        gc.collect()
        super(Main, self).on_close()

    def on_draw(self):
        """Draw the scene"""
        self.clear()

        self.scene.draw()

        if self.args.debug:
            self.fps.draw()

        self.flip()

