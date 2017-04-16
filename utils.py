import math

MAX_ALPHA = 1000
INF = 1000*1000
MIN_EPS = 0.0000001
# Alpha should not be greater than 1000

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

    def __init__(self, eps=0.1, alpha=1):
        self.eps = eps
        self.alpha_cells = int((1.0*2*math.sqrt(2))/eps) + 1
        self.cell_width = alpha / self.alpha_cells

    def get_min_max_dis(self, x_addr_1, y_addr_1, x_addr_2, y_addr_2):
        p_addr_1 = PointAddress(x_addr_1, y_addr_1, self.cell_width)
        p_addr_2 = PointAddress(x_addr_2, y_addr_2, self.cell_width)
        from_points = p_addr_1.get_corners()
        to_points = p_addr_2.get_corners()
        min_dis = INF
        max_dis = 0
        for p1 in from_points:
            for p2 in to_points:
                dis = p1.distance(p2)
                min_dis = min(min_dis, dis)
                max_dis = max(max_dis, dis)
        return min_dis, max_dis

    def get_point_address(self, point):
        x_addr = math.floor(point.x / self.cell_width)
        y_addr = math.floor(point.y / self.cell_width)
        return PointAddress(x_addr, y_addr, self.cell_width)
