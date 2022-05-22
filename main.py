from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.vertex_instructions import Ellipse, Line
from kivy.graphics.context_instructions import Color
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.properties import Clock


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 10
    V_LINES_SPACING = 0.25       # percentage in screen width

    H_NB_LINES = 20
    H_LINES_SPACING = 1. / H_NB_LINES

    vertical_lines = []
    horizontal_lines = []

    SPEED = 2
    current_offset_y = 0.

    SPEED_X = 15
    vel_x = 0
    current_offset_x = 0.

    FPS = 60.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"INIT W: {self.width} H: {self.height}")
        self.init_vertical_lines()
        self.init_horizontal_lines()
        Clock.schedule_interval(self.update, 1./self.FPS)

    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # self.perspective_point_x = 0.5 * self.width
        # self.perspective_point_y = 0.75 * self.height
        # self.update_vertical_lines()
        # self.update_horizontal_lines()
        pass

    def on_perspective_point_x(self, widget, value):
        print(f"PX: {value}")

    def on_perspective_point_y(self, widget, value):
        print(f"PY: {value}")

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        with self.canvas:
            spacing = self.V_LINES_SPACING * self.width
            central_line_x = self.width / 2
            offset = -int((self.V_NB_LINES)/2) + 0.5

            for i, vertical_line in enumerate(self.vertical_lines):
                line_x = int(central_line_x + offset*spacing
                    + self.current_offset_x)
                x1, y1 = self.transform(line_x, 0)
                x2, y2 = self.transform(line_x, self.height)
                vertical_line.points = [x1, y1, x2, y2]
                offset += 1

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        spacing_x = self.V_LINES_SPACING * self.width
        central_line_x = self.width / 2
        offset = -int((self.V_NB_LINES)/2) + 0.5

        xmin = central_line_x + offset * spacing_x + self.current_offset_x
        xmax = central_line_x - offset * spacing_x + self.current_offset_x

        with self.canvas:
            spacing_y = self.H_LINES_SPACING * self.height

            for i, horizontal_line in enumerate(self.horizontal_lines):
                line_y = i * spacing_y + self.current_offset_y
                x1, y1 = self.transform(xmin, line_y)
                x2, y2 = self.transform(xmax, line_y)
                horizontal_line.points = [x1, y1, x2, y2]

    def transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(sefl, x, y):
        return int(x), int(y)

    def transform_perspective(self, x, y):
        y_scale = 1 - pow(1 - (y / self.height), 4)
        x_scale = 1 - y_scale

        y_new = self.perspective_point_y * y_scale
        x_new = (x - self.perspective_point_x) * x_scale \
            + self.perspective_point_x

        return int(x_new), int(y_new)
    
    def on_touch_down(self, touch):
        if touch.x < self.width / 2:
            self.vel_x = - self.SPEED_X
        else:
            self.vel_x = self.SPEED_X

    def on_touch_up(self, touch):
        self.vel_x = 0.
    
    def update(self, dt):
        print(f"dt: {dt:.3f} - {1./60:.3f}")
        time_factor = dt * self.FPS
        print(f"time factor: {time_factor}")
        self.current_offset_y -= self.SPEED * time_factor
        spacing_y = self.H_LINES_SPACING * self.height
        self.current_offset_y %= spacing_y

        self.current_offset_x -= self.vel_x * time_factor

        self.update_vertical_lines()
        self.update_horizontal_lines()


class GalaxyApp(App):
    pass


GalaxyApp().run()
