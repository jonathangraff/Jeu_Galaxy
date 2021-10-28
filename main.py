import random

from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transforms import transform, transform2D, transform_perspective
    from user_actions import on_keyboard_up, on_keyboard_down, \
        on_touch_down, on_touch_up, keyboard_closed
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    vertical_lines = []
    V_NB_LINES = 8
    V_LINES_SPACING = 0.4

    horizontal_lines = []
    H_NB_LINES = 15
    H_LINES_SPACING = 0.1

    SPEED_Y = 1
    current_offset_y = 0
    current_y_loop = 0
    start_index = -int(V_NB_LINES / 2) + 1
    end_index = start_index + V_NB_LINES - 1

    SPEED_X = 4
    current_offset_x = 0
    current_speed_x = 0

    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_has_started = False
    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")
    score_txt = NumericProperty(0)
    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.prefill_tiles_coordinates()
        self.generate_tiles_coordinates()
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1 / 60)
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load('audio/begin.wav')
        self.sound_galaxy = SoundLoader.load('audio/galaxy.wav')
        self.sound_gameover_impact = SoundLoader.load('audio/gameover_impact.wav')
        self.sound_gameover_voice = SoundLoader.load('audio/gameover_voice.wav')
        self.sound_music1 = SoundLoader.load('audio/music1.wav')
        self.sound_restart = SoundLoader.load('audio/restart.wav')
        self.sound_music1.volume=1
        self.sound_begin.volume = 0.25
        self.sound_galaxy.volume = 0.25
        self.sound_gameover_voice.volume = 0.25
        self.sound_restart.volume = 0.25
        self.sound_gameover_impact.volume = 0.6

    def reset_game(self):
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.current_offset_y = 0
        self.tiles_coordinates = []
        self.prefill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.score_txt = self.current_y_loop
        self.state_game_over = False

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        else:
            return False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        width = self.SHIP_WIDTH * self.width
        self.ship_coordinates[0] = (center_x - width / 2, base_y)
        self.ship_coordinates[1] = (center_x, base_y + self.SHIP_HEIGHT * self.height)
        self.ship_coordinates[2] = (center_x + width / 2, base_y)
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NB_TILES):
                self.tiles.append(Quad())

    def prefill_tiles_coordinates(self):
        for i in range(10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):

        last_y = 0
        last_x = 0
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1

        def go_right(last_x, last_y):
            last_x += 1
            self.tiles_coordinates.append((last_x, last_y))
            last_y += 1
            self.tiles_coordinates.append((last_x, last_y))
            return last_x, last_y

        def go_left(last_x, last_y):
            last_x -= 1
            self.tiles_coordinates.append((last_x, last_y))
            last_y += 1
            self.tiles_coordinates.append((last_x, last_y))
            return last_x, last_y

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                if last_x < self.end_index - 1:
                    last_x, last_y = go_right(last_x, last_y)
                else:
                    last_x, last_y = go_left(last_x, last_y)
            elif r == 2:
                if last_x > self.start_index:
                    last_x, last_y = go_left(last_x, last_y)
                else:
                    last_x, last_y = go_right(last_x, last_y)

            last_y += 1

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        return central_line_x + offset * spacing + self.current_offset_x

    def get_line_y_from_index(self, index):
        return index * self.H_LINES_SPACING * self.height - self.current_offset_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_tiles(self):
        for i in range(self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            ti_x = tile_coordinates[0]
            ti_y = tile_coordinates[1]
            xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
            xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):

        # central_line_x = self.width / 2
        # spacing = self.V_LINES_SPACING * self.width
        # offset = -int(self.V_NB_LINES / 2) + 0.5
        xmin = self.get_line_x_from_index(self.start_index)
        xmax = self.get_line_x_from_index(self.end_index)
        # spacing_y = self.H_LINES_SPACING * self.height
        for i in range(self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED_Y * self.height / 100
            self.current_offset_y += speed_y * time_factor
            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.generate_tiles_coordinates()
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor
            self.score_txt = self.current_y_loop
        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_voice_gameover, 3)

    def play_voice_gameover(self, dt):
        if self.state_game_over:
             self.sound_gameover_voice.play()

    def on_menu_button_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


GalaxyApp().run()
