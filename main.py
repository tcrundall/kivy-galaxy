from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Line, Mesh, Quad, Triangle
from kivy.graphics.context_instructions import Color
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.properties import Clock

from itertools import chain
import random


class MainWidget(Widget):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down, keyboard_closed
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 8
    V_LINES_SPACING = 0.2       # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 11 
    H_LINES_SPACING = 1. / (H_NB_LINES - 1)
    horizontal_lines = []

    SPEED = 0.008
    current_offset_y = 0.
    current_y_loop = 0

    SPEED_X = 0.03
    current_speed_x = 0
    current_offset_x = 0.

    FPS = 60.

    NB_TILES = 20
    tiles = []
    tiles_coordinates = []

    CORNER_PROB_THRESH = 0.6

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.init_tiles()
        self.init_ship()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(
                self.keyboard_closed,
                self
            )
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1. / self.FPS)

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def pre_fill_tiles_coordinates(self):
        nb_straight_tiles = 10
        for i in range(nb_straight_tiles):
            self.tiles_coordinates.append((0, i))

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in self.tiles_coordinates:
                self.tiles.append(Quad())

    def generate_path(self):
        # random number between -1 and 1
        corner_prob = random.random() * 2 - 1

        if abs(corner_prob) < self.CORNER_PROB_THRESH:
            return 0
        if corner_prob < 0:
            return -1
        else:
            return 1
    
    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        # clean the coordinates that are out of screen
        for tile_coords in self.tiles_coordinates[:]:
            if tile_coords[1] <= self.current_y_loop:
                self.tiles_coordinates.remove(tile_coords)
        
        if self.tiles_coordinates:
            last_x, last_y = self.tiles_coordinates[-1]

        print("foo1")

        while last_y < self.current_y_loop + self.NB_TILES:
            last_y += 1
            self.tiles_coordinates.append((last_x, last_y))
            path = self.generate_path()
            if path != 0:
                min_path = -(self.V_NB_LINES - 1) / 2
                max_path = (self.V_NB_LINES) / 2 - 1
                if last_x + path < min_path:
                    path = 1
                elif last_x + path > max_path:
                    path = -1
                last_x += path
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

        print("foo2")

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing_x = self.V_LINES_SPACING * self.width
        x_diff = (index - 0.5) * spacing_x
        return central_line_x + x_diff + self.current_offset_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        return index * spacing_y - self.current_offset_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for tile, (x, y) in zip(self.tiles, self.tiles_coordinates):
            # x1, y1, x2, y2, x3, y3, x4, y4
            xmin, ymin = self.get_tile_coordinates(x, y)
            xmax, ymax = self.get_tile_coordinates(x + 1, y + 1)
            points = [
                (xmin, ymin),
                (xmin, ymax),
                (xmax, ymax),
                (xmax, ymin),
            ]
            tr_points = [list(self.transform(px, py)) for px, py in points]
            tile.points = list(chain(*tr_points))

    def update_vertical_lines(self):
        start_ix = -int((self.V_NB_LINES - 1) / 2)
        for i in range(start_ix, start_ix + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_ix = -int((self.V_NB_LINES - 1) / 2)
        end_ix = start_ix + self.V_NB_LINES

        xmin = self.get_line_x_from_index(start_ix)
        xmax = self.get_line_x_from_index(end_ix - 1)

        with self.canvas:
            for i, horizontal_line in enumerate(self.horizontal_lines):
                line_y = self.get_line_y_from_index(i)
                x1, y1 = self.transform(xmin, line_y)
                x2, y2 = self.transform(xmax, line_y)
                horizontal_line.points = [x1, y1, x2, y2]

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        x1, y1 = self.transform(self.center_x - ship_half_width, base_y)
        x2, y2 = self.transform(self.center_x, base_y + ship_height)
        x3, y3 = self.transform(self.center_x + ship_half_width, base_y)

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def update(self, dt):
        time_factor = dt * self.FPS
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        speed_y = self.SPEED * self.height
        self.current_offset_y += speed_y * time_factor

        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.generate_tiles_coordinates()
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1

#             x, y = self.tiles_coordinates.pop(0)
#             step = random.randint(-1, 1)
#             new_x = self.tiles_coordinates[-1][0] + step
#             self.tiles_coordinates.append((new_x, y + self.NB_TILES))
            # print(self.current_y_loop)
        # self.current_offset_y %= spacing_y

        speed_x = self.current_speed_x * self.width
        self.current_offset_x -= speed_x * time_factor


class GalaxyApp(App):
    pass


if __name__ == '__main__':
    GalaxyApp().run()
