from kivy.app import App
from kivy.graphics.vertex_instructions import Ellipse, Line
from kivy.graphics.context_instructions import Color
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 4
    V_LINES_SPACING = 0.1       # percentage in screen width
    vertical_lines = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"INIT W: {self.width} H: {self.height}")
        self.init_vertical_lines()

    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # self.perspective_point_x = 0.5 * self.width
        # self.perspective_point_y = 0.75 * self.height
        self.update_vertical_lines()

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
            offset = -(self.V_NB_LINES - 1)/2

            for i, vertical_line in enumerate(self.vertical_lines):
                line_x = int(central_line_x + offset*spacing)
                x1, y1 = self.transform(line_x, 0)
                x2, y2 = self.transform(line_x, self.height)
                vertical_line.points = [x1, y1, x2, y2]
                offset += 1

    def transform(self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(sefl, x, y):
        return x, y

    def transform_perspective(self, x, y):
        y_scale = y / self.height
        x_scale = 1 - y_scale

        y_new = self.perspective_point_y * y_scale
        x_new = (x - self.perspective_point_x) * x_scale \
            + self.perspective_point_x

        return (x_new, y_new)


class GalaxyApp(App):
    pass


GalaxyApp().run()
