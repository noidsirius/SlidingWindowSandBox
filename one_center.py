import random
import math

from utils import *


def get_points_of_entries(entry_points):
    return [ep.point for ep in entry_points]

class OneCenterSolver:
    def __init__(self, eps, alpha):
        self.my_alpha_entry_points = []
        self.center = None
        self.radius = INF
        self.alpha = alpha
        self.eps = eps
        self.point_util = PointUtil(self.eps, self.alpha)

    @staticmethod
    def find_one_cell_center(entry_points, point_util):
        radius = INF
        center = None
        for i in range(len(entry_points)):
            min_i_radius = 0
            for j in range(len(entry_points)):
                if i == j:
                    continue
                ep = entry_points[j]
                min_i_radius = max(min_i_radius, point_util.get_cell_distance(ep.point, entry_points[i].point))
            if min_i_radius < radius:
                radius, center = min_i_radius,  entry_points[i]
        return radius, center

    def insert_entry_point(self, new_entry_point):
        for ep in self.my_alpha_entry_points:
            if not ep.is_alive() or self.point_util.is_in_same_cell(ep.point, new_entry_point.point):
                self.my_alpha_entry_points.remove(ep)
        self.my_alpha_entry_points.append(new_entry_point)
        r_radius, r_center = OneCenterSolver.find_one_cell_center(self.my_alpha_entry_points, self.point_util)
        max_valid_distance = self.alpha *(1 + self.eps)
        if r_center is None and len(self.my_alpha_entry_points) == 1:
            self.center = self.my_alpha_entry_points[0]
            self.radius = 0
        elif r_radius < max_valid_distance:
            self.center = r_center
            self.radius = r_radius
        else:
            last_recent_farthest_ep = None
            for ep in self.my_alpha_entry_points:
                if self.point_util.get_cell_distance(new_entry_point.point, ep.point) > 2*max_valid_distance:
                    last_recent_farthest_ep = ep
            for ep in self.my_alpha_entry_points:
                if ep != last_recent_farthest_ep and self.point_util.get_cell_distance(new_entry_point.point, ep.point) > 2 * max_valid_distance:
                    self.my_alpha_entry_points.remove(ep)
            self.center = None
            self.radius = INF

    def get_points_for_draw(self):
        points = [self.point_util.get_point_address(ep.point).get_center_point() for ep in self.my_alpha_entry_points]
        center = self.point_util.get_point_address(self.center.point).get_center_point() if self.center else None
        radius = self.radius
        return (points, center, radius)

def get_point_coord(point, is_point_class):
    if is_point_class:
        x,y = point.x, point.y
    else:
        x,y = point
    return x,y

# point_series => [entry_points, center, radius]
def draw_oc_points_series(point_series, cell_width = 1, is_point_class=True):

    import matplotlib.pyplot as plt
    import numpy
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xticks(numpy.arange(1.0*-MAX_RADIUS/2, 1.0*MAX_RADIUS/2, cell_width))
    ax.set_yticks(numpy.arange(1.0*-MAX_RADIUS/2, 1.0*MAX_RADIUS/2, cell_width))
    ax.set_autoscale_on(False)
    plt.grid()
    ax.set_xlabel('x-points')
    ax.set_ylabel('y-points')
    title = ""
    if cell_width != 1:
        title += "Cell Width: %f" % cell_width

    colors = 'bgrcmyk'
    shapes = 'ov^<>12348s'
    index = 0
    for points, center, radius in point_series:
        index += 1
        color = colors[index%len(colors)]
        shape = shapes[index%len(shapes)]
        x_points = []
        y_points = []
        for p in points:
            x, y = get_point_coord(p, is_point_class)
            x_points.append(x)
            y_points.append(y)
        if center:
            center_x, center_y = get_point_coord(center, is_point_class)
            circle1 = plt.Circle((center_x, center_y), radius, color=color, fill=False, clip_on=False)
            # TODO: 0.1 should be generalize
            circle2 = plt.Circle((center_x, center_y), 0.1, color=color, fill=False)
            ax.add_artist(circle1)
            ax.add_artist(circle2)
            title += " %s.Radius = %f" % (color, radius)
        p = ax.plot(x_points, y_points, '%s%s'%(color,shape))

    ax.set_title(title)
    fig.show()


class OneCenterSimulator:
    def __init__(self, eps, max_radius=MAX_RADIUS, window_size=WINDOW_SIZE):
        self.eps = eps / 2
        self.max_radius = max_radius
        self.oc_solvers = []
        self.current_time = 0
        self.window_size = window_size
        self.entry_points = []
        self.alive_points = []

        alpha_tmp = self.eps
        oc_count = int(math.log(self.max_radius/self.eps, (1+self.eps))) + 1
        for i in range(oc_count):
            self.oc_solvers.append( OneCenterSolver(self.eps, alpha_tmp))
            alpha_tmp *= 1 + self.eps
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

    @staticmethod
    def find_one_center(entry_points):
        radius = INF
        center = None
        for i in range(len(entry_points)):
            min_i_radius = 0
            for j in range(len(entry_points)):
                if i == j:
                    continue
                ep = entry_points[j]
                min_i_radius = max(min_i_radius, ep.point.distance(entry_points[i].point))
            if min_i_radius < radius:
                radius, center = min_i_radius,  entry_points[i]
        return radius, center


    def insert_entry_point(self, point=None):
        if point is None:
            point = OneCenterSimulator.generate_random_point(self.max_radius*math.sqrt(2)/2)
        new_entry_point = EntryPoint(point, self.current_time, window_size=self.window_size)
        self.current_time += 1
        self.entry_points.append(new_entry_point)
        for ep in self.alive_points:
            ep.increase_age_one()
        self.alive_points.append(new_entry_point)
        if len(self.alive_points) > self.window_size:
            self.alive_points.pop(0)
        return new_entry_point


    def execute_one_cycle(self, new_point=None):
        new_entry_point = self.insert_entry_point(new_point)
        oc_result = INF
        ocs_result = None
        for ocs in self.oc_solvers:
            ocs.insert_entry_point(new_entry_point)
            if ocs.radius < INF and oc_result == INF:
                oc_result = ocs.radius
                ocs_result = ocs
        expected_radius, expected_center = OneCenterSimulator.find_one_center(self.alive_points)
        return (expected_center, expected_radius, ocs_result)

    def demo_execute_one_cycle(self):
        expected_center, expected_radius, ocs_result = self.execute_one_cycle()
        draw_points_series([(get_points_of_entries(self.alive_points), expected_center.point, expected_radius),
        ocs_result.get_points_for_draw()], ocs_result.point_util.cell_width)
