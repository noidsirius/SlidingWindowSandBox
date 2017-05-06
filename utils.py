import math
import random

MAX_ALPHA = 1000
INF = 1000*1000
MIN_EPS = 0.0000001
WINDOW_SIZE = 20
MAX_RADIUS = 10
# Alpha should not be greater than 1000

def average(list_of_numbers):
    if len(list_of_numbers) == 0:
        return 0
    return sum(list_of_numbers) / len(list_of_numbers)

class Point:
    """ Create a new Point, at coordinates x, y """

    def __init__(self, x=0.0, y=0.0):
        """ Create a new point at x, y """
        self.x = float(x)
        self.y = float(y)

    def distance(self, point):
        return math.sqrt((self.x-point.x)**2 + (self.y-point.y)**2)

    def move(self, vec):
        return Point( self.x + vec.x, self.y + vec.y)

    def get_middle(self, point):
        return Point((self.x + point.x)/2, (self.y + point.y)/2)

    def __str__(self):
        return "(%f, %f)" % (self.x, self.y)

    def __repr__(self):
        return "(%f, %f)" % (self.x, self.y)


class EntryPoint:
    def __init__(self, point, entry_time=0, window_size=WINDOW_SIZE):
        self.point = point
        self.age = 0
        self.entry_time = entry_time
        self.point_addr = None
        self.window_size = window_size

    def increase_age_one(self):
        self.age += 1

    def is_alive(self):
        return self.age < self.window_size

    def __str__(self):
        return "(%d, %d, %s)" %(self.entry_time, self.age, self.point)

    def __repr__(self):
        return "(%d, %d, %s)" %(self.entry_time, self.age, self.point)


def get_points_of_entries(entry_points):
    return [ep.point for ep in entry_points]


def get_point_coord(point, is_point_class):
    if is_point_class:
        x,y = point.x, point.y
    else:
        x,y = point
    return x,y


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

    def distance(self, p_addr):
        from_points = self.get_corners()
        to_points = p_addr.get_corners()
        max_dis = 0
        for p1 in from_points:
            for p2 in to_points:
                dis = p1.distance(p2)
                max_dis = max(max_dis, dis)
        return max_dis


class PointUtil:

    def __init__(self, eps=0.1, alpha=1, alpha_cells=0):
        self.eps = eps
        if alpha_cells == 0:
            self.alpha_cells = int(math.ceil((1.0*2*math.sqrt(2))/(1.0*self.eps/2)))
        else:
            self.alpha_cells = alpha_cells
        self.alpha = alpha
        self.cell_width = 1.0*self.alpha / self.alpha_cells

    @staticmethod
    def generate_random_point(max_axis_length):
        x = random.random() * max_axis_length - max_axis_length/2
        y = random.random() * max_axis_length - max_axis_length/2
        return Point(x, y)

    @staticmethod
    def generate_customized_random_point(x_0, y_0, x_1, y_1):
        x = random.random() * (x_1 - x_0) + x_0
        y = random.random() * (y_1 - y_0) + y_0
        return Point(x, y)

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

    def get_cell_distance(self, point1, point2):
        p_addr_1 = self.get_point_address(point1)
        p_addr_2 = self.get_point_address(point2)
        return p_addr_1.distance(p_addr_2)

    def is_in_same_cell(self, point1, point2):
        p_addr_1 = self.get_point_address(point1)
        p_addr_2 = self.get_point_address(point2)
        return p_addr_1.x_addr == p_addr_2.x_addr \
                and p_addr_1.y_addr == p_addr_2.y_addr

    def calculate_real_eps(self):
        m = self.alpha_cells / 2

        point_address_x_range = (-m, m+1)
        point_address_y_range = (-m, m+1)

        min_dis = INF
        max_dis = 0
        for i in range(*point_address_x_range):
            for j in range(*point_address_y_range):
                if i == 0 and j == 0:
                    continue
                tmp_min, tmp_max = self.get_min_max_dis(0, 0, i, j)
                if tmp_max < self.alpha or tmp_min > self.alpha:
                    continue
                min_dis = min(min_dis, tmp_min)
                max_dis = max(max_dis, tmp_max)

        return max(self.alpha-min_dis, max_dis - self.alpha) / self.alpha

    @staticmethod
    def get_distance_from_point(source, target, point_util=None):
        if point_util:
            dis = point_util.get_cell_distance(source.point, target.point)
        else:
            dis = source.point.distance(target.point)
        return dis

    @staticmethod
    def get_min_distance_from_points(source, entry_points, point_util=None):
        if point_util:
            dis = min([point_util.get_cell_distance(ep.point, source.point) for ep in entry_points])
        else:
            dis = min([ep.point.distance(source.point) for ep in entry_points])
        return dis

    @staticmethod
    def is_in_circle(source, c_ep_1, c_ep_2, point_util=None):
        if point_util:
            # TODO need refactor
            cep1_addr = point_util.get_point_address(c_ep_1.point)
            cep2_addr = point_util.get_point_address(c_ep_2.point)
            center_addr = PointAddress((cep1_addr.x_addr + cep2_addr.x_addr) / 2.0,
                                       (cep1_addr.y_addr + cep2_addr.y_addr) / 2.0, point_util.cell_width)
            radius = point_util.get_cell_distance(c_ep_1.point, c_ep_2.point) / (2 * (1 + point_util.eps))
            return center_addr.distance(point_util.get_point_address(source.point)) <= radius
        else:
            center = c_ep_1.get_middle(c_ep_2)
            radius = c_ep_1.distance(c_ep_2.point) / 2
            return center.distance(source.point) <= radius
