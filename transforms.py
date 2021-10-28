def transform(self, x, y):
    # return self.transform2D(x,y)
    return self.transform_perspective(x, y)


def transform2D(self, x, y):
    return int(x), int(y)


def transform_perspective(self, x, y):
    lin_y = y / self.height * self.perspective_point_y
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y
    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    factor_y = diff_y / self.perspective_point_y
    factor_y = factor_y ** 4
    offset_x = diff_x * factor_y
    tr_x = self.perspective_point_x + offset_x
    tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
    return tr_x, tr_y