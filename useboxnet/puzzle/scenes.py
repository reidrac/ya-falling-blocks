"""
Scenes
"""

from math import ceil
from random import randint

import pyglet

from useboxnet.puzzle.const import HEIGHT

class Menu(object):
    """Menu scene"""

    # background image
    bg = pyglet.resource.image("panel.png")
    # effect to play on menu items selection
    select_snd = pyglet.resource.media("select.wav", streaming=False)

    OPTIONS = ["Play", "Music: On", "Exit"]

    # colors
    UNSELECTED = (100, 100, 100, 255)
    SELECTED = (255, 255, 255, 255)

    # hiscore
    hilevel = 1
    hiscore = 0

    def __init__(self, control, change_scene):
        self.control = control
        self.change_scene = change_scene

        self.input_delay = 10

        # for the hiscore
        self.score_label = pyglet.text.Label("HI: %.6d" % self.hiscore,
                                             font_size=18,
                                             x=Game.OFFSET_X+32+Game.BOARD_W*Game.SIZE,
                                             y=(Game.BOARD_H-4)*Game.SIZE,
                                             )
        self.level_label = pyglet.text.Label("Level: %d" % self.hilevel,
                                             font_size=18,
                                             x=Game.OFFSET_X+32+Game.BOARD_W*Game.SIZE,
                                             y=(Game.BOARD_H-4)*Game.SIZE-28,
                                             )

        # set the music status
        music = "On" if Game.play_music else "Off"
        self.OPTIONS[1] = "Music: %s" % music

        self.labels = []
        for i in range(len(self.OPTIONS)):
            self.labels.append(pyglet.text.Label(self.OPTIONS[i],
                                                 font_size=16,
                                                 bold=True,
                                                 x=420,
                                                 y=300-i*32,
                                                 color=self.UNSELECTED,
                                                 ))
        self.selected = None
        self.select(0) # Play

    def close(self):
        """Nothin to clean"""
        pass

    def select(self, index):
        """Select a menu option"""
        if self.selected is not None:
            self.labels[self.selected].color = self.UNSELECTED
        self.selected = index
        self.labels[index].color = self.SELECTED

    def update(self, dt):
        """Update the menu status"""

        self.input_delay -= 1
        if self.input_delay < 0:

            if self.control.action:

                if self.selected == 0: # Play
                    self.select_snd.play()
                    self.change_scene("game")

                elif self.selected == 1: # Music
                    self.select_snd.play()
                    Game.play_music = not Game.play_music
                    music = "On" if Game.play_music else "Off"
                    self.labels[1].text = "Music: %s" % music
                    self.input_delay = 10

                elif self.selected == 2: # Exit
                    self.change_scene("quit")

            elif self.control.up and self.selected > 0:
                self.select(self.selected-1)
                self.input_delay = 10

            elif self.control.down and self.selected < len(self.OPTIONS)-1:
                self.select(self.selected+1)
                self.input_delay = 10


    def draw(self):
        """Draw the scene"""

        # panel
        self.bg.blit(0, 0)

        # hiscore
        self.score_label.draw()
        self.level_label.draw()

        # the menu
        for label in self.labels:
            label.draw()

class BasePiece(pyglet.sprite.Sprite):
    image = None
    def __init__(self, x, y, type=None, batch=None):
        self.type = type
        super(BasePiece, self).__init__(self.image, x=x, y=y, batch=batch)

class Empty(BasePiece):
    image = pyglet.resource.image("empty.png")

class Scored(BasePiece):
    image = pyglet.resource.image("scored.png")

class Piece(pyglet.sprite.Sprite):
    images = [pyglet.resource.image("piece%d.png" % i) for i in range(5)]
    def __init__(self, x, y, type, batch):
        self.type = type
        super(Piece, self).__init__(self.images[type], x=x, y=y, batch=batch)

class Game(object):

    SIZE = 32 # piece size

    # board dimensions
    BOARD_W = 9
    BOARD_H = 18

    # for chained scores (starts in 1)
    PITCH = (1.0, 0.8, 1.0, 1.4, 1.8, 2.0, 2.4,)

    # sound effects
    hit = pyglet.resource.media("hit.wav", streaming=False)
    levelup = pyglet.resource.media("levelup.wav", streaming=False)
    scored = pyglet.resource.media("scored.wav", streaming=False)

    # background
    bg = pyglet.resource.image("panel.png")

    play_music = True

    # board offset on the screen
    OFFSET_X = 60

    def __init__(self, control, change_scene):
        self.control = control
        self.change_scene = change_scene

        # status for the updates
        self.status = "ready?"
        self.delay = 200

        # default delay
        self.top_delay = 30
        # input delay
        self.movement_delay = 0

        # used by the falling block row on level up
        self.fast_gravity = False

        # used by the game over clean effect
        self.gameover_clean = 0

        # init the board as empty
        self.board_batch = pyglet.graphics.Batch()
        self.board = [None for i in range(self.BOARD_W*self.BOARD_H)]
        for y in range(self.BOARD_H):
            for x in range(self.BOARD_W):
                self.set_board(x, y, Empty)
        self.combos = None

        # images for current and next
        self.pieces = [pyglet.resource.image("piece%d.png" % i) for i in range(5)]

        # intial piece position
        self.x = self.BOARD_W/2
        self.y = 0

        # get pieces
        self.current = self.new_piece()
        self.next = self.new_piece()

        self.combo_level = 1
        self.score = 0
        self.score_label = pyglet.text.Label("",
                                             font_size=18,
                                             x=self.OFFSET_X+32+self.BOARD_W*self.SIZE,
                                             y=(self.BOARD_H-4)*self.SIZE,
                                             )
        self.level_count = 0
        self.level_top = 10
        self.level = 1
        self.level_label = pyglet.text.Label("",
                                             font_size=18,
                                             x=self.OFFSET_X+32+self.BOARD_W*self.SIZE,
                                             y=(self.BOARD_H-4)*self.SIZE-28,
                                             )

        # used for misc messages
        self.message_label = pyglet.text.Label("Ready?",
                                               font_size=24,
                                               bold=True,
                                               x=self.OFFSET_X+(self.BOARD_W*self.SIZE)/2,
                                               y=360,
                                               anchor_x='center',
                                               )

        # load the music
        self.music = pyglet.resource.media("fatigue.ogg")
        self.player = None

    def close(self):
        """Clean up"""
        if self.play_music and self.player.playing:
            self.player.pause()
            self.player = None

    def new_piece(self):
        """Generate a new piece (types)"""
        return [ randint(0, 4),
                 randint(0, 4),
                 randint(0, 4),
                 ]

    def board_to_screen(self, x, y):
        """Translate board coordinates into screen coordinates"""
        return x*self.SIZE + self.OFFSET_X, HEIGHT - (y+1)*self.SIZE

    def get_board(self, x, y):
        """Get item at board position x, y"""
        return self.board[x + int(y)*self.BOARD_W]

    def set_board(self, x, y, cls, type=None):
        """Set item at board position x,y.

        Optionally provide a "type" for Piece.
        """
        sx, sy = self.board_to_screen(x, y)
        index = x + int(y)*self.BOARD_W
        if self.board[index] is not None:
            self.board[index].delete()
        self.board[index] = cls(sx, sy, type=type, batch=self.board_batch)

    def is_free(self, x, y):
        """Check if piece at board x, y is Empty"""
        return self.board[x + int(y)*self.BOARD_W].type is None

    def update(self, dt):
        """Update game status"""

        # delay for non-move statuses
        if self.status != "move":
            self.delay -= 1
            if self.delay >= 0:
                return

        if self.status == "combo":
            # look for combos
            self.combos = set()
            points = 0
            for y in range(self.BOARD_H):
                for x in range(self.BOARD_W):
                    if self.is_free(x, y):
                        continue

                    current = self.get_board(x, y).type

                    # horizontal
                    strike = 0
                    for nx in range(x, self.BOARD_W):
                        if current == self.get_board(nx, y).type:
                            strike += 1
                        else:
                            break
                    if strike > 2:
                        points += strike
                        for nx in range(x, x+strike):
                            self.combos.add((nx, y))

                    # vertical
                    strike = 0
                    for ny in range(y, self.BOARD_H):
                        if current == self.get_board(x, ny).type:
                            strike += 1
                        else:
                            break
                    if strike > 2:
                        points += strike
                        for ny in range(y, y+strike):
                            self.combos.add((x, ny))

            # chage the graphic of the scored pieces
            for x, y in self.combos:
                self.set_board(x, y, Scored)

            # play a sound when scoring, alter the pitch based on chained scores
            if points:
                self.scored.play().pitch = self.PITCH[self.combo_level] if self.combo_level < len(self.PITCH) else 1.0

            if self.combos:
                # we may have more
                self.score += points*self.combo_level*10
                self.combo_level += 1
                self.delay = self.top_delay/2
                self.status = "score"
            else:
                # no more chained scores, no need to apply gravity
                self.score += points*self.combo_level*12
                self.combo_level = 1
                self.status = "next"

            return

        elif self.status == "score":

            # clear combos + score
            for x, y in self.combos:
                self.set_board(x, y, Empty)

            if self.combos:
                self.status = "gravity"
            else:
                self.status = "next"

            return

        elif self.status == "gravity":

            # apply gravity
            updated = False
            for y in range(self.BOARD_H-1):
                for x in range(self.BOARD_W):
                    # from bottom to top
                    by = self.BOARD_H-2-y
                    if not self.is_free(x, by) and self.is_free(x, by+1):
                        self.set_board(x, by+1, Piece, self.get_board(x, by).type)
                        self.set_board(x, by, Empty)
                        updated = True
            if updated:
                self.delay = self.top_delay/3
                if self.fast_gravity:
                    self.delay = 1
                return

            self.fast_gravity = False
            self.status = "combo"
            self.delay = self.top_delay
            return

        elif self.status == "next":

            # next piece
            self.current = self.next
            self.next = self.new_piece()

            self.level_count += 1
            if self.level_count > self.level_top:
                self.level_count = 0
                self.level_top *= 2
                self.level += 1

                self.levelup.play()

                # speed or falling blocks
                if self.level % 2:
                    self.top_delay *= 0.6
                else:
                    for x in range(self.BOARD_W):
                        self.set_board(x, 0, Piece, randint(0, 4))
                    self.fast_gravity = True
                    self.status = "gravity"
                    return

            self.y = 0
            self.x = self.BOARD_W/2

            if not all([self.is_free(self.x, self.y),
                        self.is_free(self.x, self.y+1),
                        ]):
                self.message_label.font_size = 24
                self.message_label.text = "GAME OVER"
                self.status = "gameover"
            else:
                self.status = "move"

            return

        elif self.status == "gameover":

            # the game is over, play the clean effect
            if self.play_music and self.player.playing:
                self.player.pause()

            if self.gameover_clean is not None:
                for x in range(self.BOARD_W):
                    self.set_board(x, self.BOARD_H-1-self.gameover_clean, Empty)

                self.hit.play()

                self.gameover_clean += 1
                if self.gameover_clean == self.BOARD_H:
                    self.gameover_clean = None
            else:
                # after a pause, go back to the menu
                self.delay = 200
                self.status = "quit"
                return

            self.delay = 8
            return

        elif self.status == "paused":

            # the game was paused
            if self.control.pause:
                self.status = "move"
                if self.play_music:
                    self.player.play()
                # so it is not paused again immediately
                self.movement_delay = 20
            self.delay = 5
            return

        elif self.status == "escaped":

            # escape was pressed, whould we leave?
            if self.control.escape:
                self.status = "move"
                if self.play_music:
                    self.player.play()
                self.movement_delay = 20
            elif self.control.action:
                self.change_scene("menu")
                return
            self.delay = 5
            return

        elif self.status == "quit":

            # after the game is over
            if self.score > Menu.hiscore:
                Menu.hiscore = self.score
                Menu.hilevel = self.level

            self.change_scene("menu")
            return

        elif self.status == "ready?":

            # the dramatic pause before starting the game
            self.status = "move"
            if self.play_music:
                self.player = self.music.play()
                self.player.volume = 0.25
                self.player.eos_action = self.player.EOS_LOOP
            return

        # from now on status is "move"

        if self.movement_delay < 0:

            # adjustment to avoid moving left/right in the middle of a step
            xy = self.y
            if xy + 0.5 < self.BOARD_H:
                xy = ceil(self.y)

            if self.control.left and self.x-1 >= 0 and self.is_free(self.x-1, xy+2):
                self.movement_delay = 5
                self.x -= 1
            if self.control.right and self.x+1 < self.BOARD_W and self.is_free(self.x+1, xy+2):
                self.movement_delay = 5
                self.x += 1
            if self.control.action:
                self.movement_delay = 5
                self.current = self.current[1:] + self.current[0:1]
            if self.control.down and self.y+3 < self.BOARD_H and self.is_free(self.x, self.y+3):
                self.movement_delay = 5
                self.y += 0.5

            if self.control.pause:
                self.message_label.font_size = 24
                self.message_label.text = "(paused)"
                if self.play_music:
                    self.player.pause()
                self.status = "paused"
                self.delay = 10

            if self.control.escape:
                self.message_label.font_size = 14
                self.message_label.text = "(press ACTION to leave)"
                if self.play_music:
                    self.player.pause()
                self.status = "escaped"
                self.delay = 10

        else:
            self.movement_delay -= 1

        self.delay -= 1

        if self.delay < 0:
            self.delay = self.top_delay

            if self.y+3 < self.BOARD_H and self.is_free(self.x, self.y+3):
                self.y += 0.5
            else:
                for i in range(3):
                    self.set_board(self.x, self.y+i, Piece, self.current[i])

                # check if the user has scored
                self.hit.play()
                self.status = "combo"

    def draw(self):
        """Draw the scene"""

        # panel
        self.bg.blit(0, 0)

        # board
        self.board_batch.draw()

        for i in range(3):
            # current piece
            if self.status == "move":
                x, y = self.board_to_screen(self.x, self.y)
                self.pieces[self.current[i]].blit(x, y-i*self.SIZE)

            # next piece
            self.pieces[self.next[i]].blit(self.OFFSET_X+self.BOARD_W*self.SIZE + 32, HEIGHT-32-i*self.SIZE)

        # current score
        self.score_label.text = "Score %.6d" % self.score
        self.score_label.draw()

        # current level
        self.level_label.text = "Level %d" % self.level
        self.level_label.draw()

        # used after game over effect
        if self.status == "gameover" and self.gameover_clean is None:
            self.message_label.draw()

        # misc messages
        if self.status in ("ready?", "paused", "escaped", "quit"):
            self.message_label.draw()

