from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Line, Mesh, Quad
from kivy.graphics.context_instructions import Color
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.properties import Clock

from itertools import chain


class MainWidget(Widget):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down, keyboard_closed
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 7
    V_LINES_SPACING = 0.1       # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 20
    H_LINES_SPACING = 1. / (H_NB_LINES - 1)
    horizontal_lines = []

    SPEED = 0.1
    current_offset_y = 0.
    current_y_progress = 0

    SPEED_X = 15
    current_speed_x = 0
    current_offset_x = 0.

    FPS = 60.

    tiles = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()

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

    def update_vertical_lines(self):
        # -1, 0, 1, 2
        # -2, -1, 0, 1, 2
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

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(4):
                self.tiles.append(Quad())

    def update_tiles(self):
        tile_coords = [(0,0), (1,5), (2,7), (-2,2)]
        for tile, (x, y) in zip(self.tiles, tile_coords):
            # x1, y1, x2, y2, x3, y3, x4, y4
            bl = (
                self.get_line_x_from_index(x),
                self.get_line_y_from_index(y, move=True),
            )
            tr = (
                self.get_line_x_from_index(x+1),
                self.get_line_y_from_index(y+1, move=True),
            )
            points = [
                bl,
                (bl[0], tr[1]),
                tr,
                (tr[0], bl[1]),
            ]
            tr_points = [list(self.transform(px, py)) for px, py in points]
            tile.points = list(chain(*tr_points))

    def update(self, dt):
        time_factor = dt * self.FPS
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()

        self.current_offset_y += self.SPEED * time_factor

        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_progress += 1
            print(self.current_y_progress)
        # self.current_offset_y %= spacing_y

        self.current_offset_x -= self.current_speed_x * time_factor

    def get_line_y_from_index(self, index, move=False):
        spacing_y = self.H_LINES_SPACING * self.height
        if move:
            index -= self.current_y_progress
        return index * spacing_y - self.current_offset_y


class GalaxyApp(App):
    pass


if __name__ == '__main__':
    GalaxyApp().run()
