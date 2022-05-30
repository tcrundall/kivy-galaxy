
def transform(self, x, y):
    # return self.transform_2D(x, y)
    return self.transform_perspective(x, y)


def transform_2D(self, x, y):
    return int(x), int(y)


def transform_perspective(self, x, y):
    if y > self.height:
        return int(self.perspective_point_x), int(self.perspective_point_y)

    y_scale = 1 - pow(1 - (y / self.height), 4)
    x_scale = 1 - y_scale

    y_new = self.perspective_point_y * y_scale

    x_new = (x - self.perspective_point_x) * x_scale \
        + self.perspective_point_x

    return int(x_new), int(y_new)