import math

class Point:
    """ Create a new Point, at coordinates x, y """

    def __init__(self, x=0, y=0):
        """ Create a new point at x, y """
        self.x = x
        self.y = y

    def distance(self, point):
        return math.sqrt((self.x-point.x)**2 + (self.y-point.y)**2)

    def move(self, vec):
        return Point( self.x + vec.x, self.y + vec.y)

class PointAddress:

    """ i, j represents the bottom left corner of the cell """
    def __init__(self, x_addr=0, y_addr=0, cell_width=1):
        self.x_addr = x_addr
        self.y_addr = y_addr
        self.cell_width = cell_width

    def get_center_point(self):
        return Point((self.x_addr + 1.0/2)*self.cell_width,\
            (self.y_addr + 1.0/2)*self.cell_width)

    def get_corners(self):
        ret_list = []
        center_point = self.get_center_point()
        for d_x in [-self.cell_width/2, self.cell_width/2]:
            for d_y in [-self.cell_width/2, self.cell_width/2]:
                ret_list.append( center_point.move(Point(d_x, d_y)))
        return ret_list


class PointUtil:

    def __init__(self, eps, alpha):
        self.eps = eps
        self.alpha_cells = int((1.0*2*math.sqrt(2))/eps) + 1
        self.cell_width = self.alpha / self.alpha_cells

    @staticmethod
    def get_min_max_dis(point_addr_1, point_addr_2):
        from_points = get_corners(*point_addr_1)
        to_points = get_corners(*point_addr_2)
        min_dis = INF
        max_dis = 0
        for p1 in from_points:
            for p2 in to_points:
                dis = p1.distance(p2)
                min_dis = min(min_dis, dis)
                max_dis = max(max_dis, dis)
        return min_dis, max_dis
