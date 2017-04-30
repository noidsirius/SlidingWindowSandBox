import random
import math

from utils import *


class TwoCenterSolver:
    def __init__(self, eps, alpha):
        self.my_alpha_entry_points = []
        self.center_1 = None
        self.center_2 = None
        self.radius = INF
        self.alpha = alpha
        self.eps = eps
        self.point_util = PointUtil(self.eps, self.alpha)

    @staticmethod
    def find_two_cell_center(entry_points, point_util):
        radius = INF
        center_1 = None
        center_2 = None
        for i in range(len(entry_points)):
            for j in range(i+1, len(entry_points)):
                min_radius = 0
                for k in range(len(entry_points)):
                    if i == j:
                        continue
                    p_i = entry_points[i].point
                    p_j = entry_points[j].point
                    p_k = entry_points[k].point
                    dis_k = min(point_util.get_cell_distance(p_i, p_k), point_util.get_cell_distance(p_j, p_k))
                    min_radius = max(min_radius, dis_k)
                if min_radius < radius:
                    radius, center_1, center_2 = min_radius,  entry_points[i], entry_points[j]
        return radius, center_1, center_2

    def insert_entry_point(self, new_entry_point):
        for ep in self.my_alpha_entry_points:
            if not ep.is_alive() or self.point_util.is_in_same_cell(ep.point, new_entry_point.point):
                self.my_alpha_entry_points.remove(ep)
        self.my_alpha_entry_points.append(new_entry_point)
        r_radius, r_center_1, r_center_2 = TwoCenterSolver.find_two_cell_center(self.my_alpha_entry_points, self.point_util)
        max_valid_distance = self.alpha *(1 + self.eps)
        if len(self.my_alpha_entry_points) <= 2:
            self.center_1 = self.my_alpha_entry_points[0]
            self.center_2 = self.my_alpha_entry_points[0] if len(self.my_alpha_entry_points) == 1 else self.my_alpha_entry_points[1]
            self.radius = 0
        elif r_radius < max_valid_distance:
            self.center_1 = r_center_1
            self.center_2 = r_center_2
            self.radius = r_radius
        else:
            most_recent_farthest_ep = None
            for ep in reversed(self.my_alpha_entry_points):
                if self.point_util.get_cell_distance(new_entry_point.point, ep.point) > 2*max_valid_distance:
                    most_recent_farthest_ep = ep
                    break
            if most_recent_farthest_ep:
                second_most_recent_farthest_ep = None
                for ep in reversed(self.my_alpha_entry_points):
                    cell_dis = min(self.point_util.get_cell_distance(new_entry_point.point, ep.point),\
                                    self.point_util.get_cell_distance(most_recent_farthest_ep.point, ep.point))
                    if cell_dis > 2 * max_valid_distance:
                        second_most_recent_farthest_ep = ep
                        break
                for ep in self.my_alpha_entry_points:
                    cell_dis = min(self.point_util.get_cell_distance(new_entry_point.point, ep.point),\
                                    self.point_util.get_cell_distance(most_recent_farthest_ep.point, ep.point))
                    if ep != second_most_recent_farthest_ep and cell_dis > 2 * max_valid_distance:
                        # print self.alpha, new_entry_point, most_recent_farthest_ep, ep
                        # print "####"
                        self.my_alpha_entry_points.remove(ep)
            self.center_1 = None
            self.center_2 = None
            self.radius = INF

    def get_points_for_draw(self):
        points = [self.point_util.get_point_address(ep.point).get_center_point() for ep in self.my_alpha_entry_points]
        center_1 = self.point_util.get_point_address(self.center_1.point).get_center_point() if self.center_1 else None
        center_2 = self.point_util.get_point_address(self.center_2.point).get_center_point() if self.center_2 else None
        radius = self.radius
        return (points, center_1, center_2, radius)


# point_series => [entry_points, center_1, center_2, radius]
def draw_tc_points_series(point_series, cell_width = 1, is_point_class=True, max_radius=MAX_RADIUS):

    import matplotlib.pyplot as plt
    import numpy
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xticks(numpy.arange(1.0*-max_radius/2, 1.0*max_radius/2, cell_width))
    ax.set_yticks(numpy.arange(1.0*-max_radius/2, 1.0*max_radius/2, cell_width))
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
    for points, center_1, center_2, radius in point_series:
        index += 1
        color = colors[index%len(colors)]
        shape = shapes[index%len(shapes)]
        x_points = []
        y_points = []
        for p in points:
            x, y = get_point_coord(p, is_point_class)
            x_points.append(x)
            y_points.append(y)
        if center_1 and center_2:
            center_1_x, center_1_y = get_point_coord(center_1, is_point_class)
            center_2_x, center_2_y = get_point_coord(center_2, is_point_class)
            circle1 = plt.Circle((center_1_x, center_1_y), radius, color=color, fill=False, clip_on=False)
            circle2 = plt.Circle((center_2_x, center_2_y), radius, color=color, fill=False, clip_on=False)
            # TODO: 0.1 should be generalize
            circle1_1 = plt.Circle((center_1_x, center_1_y), 0.1, color=color, fill=False)
            circle2_1 = plt.Circle((center_2_x, center_2_y), 0.1, color=color, fill=False)
            ax.add_artist(circle1)
            ax.add_artist(circle2)
            ax.add_artist(circle1_1)
            ax.add_artist(circle2_1)
            title += " %s.Radius = %f" % (color, radius)
        p = ax.plot(x_points, y_points, '%s%s'%(color,shape))

    ax.set_title(title)
    fig.show()


class TwoCenterSimulator:
    def __init__(self, eps, max_radius=MAX_RADIUS, window_size=WINDOW_SIZE):
        self.eps = eps / 2
        self.max_radius = max_radius
        self.tc_solvers = []
        self.current_time = 0
        self.window_size = window_size
        self.entry_points = []
        self.alive_points = []

        alpha_tmp = self.eps
        tc_count = int(math.log(self.max_radius/self.eps, (1+self.eps))) + 1
        for i in range(tc_count):
            self.tc_solvers.append( TwoCenterSolver(self.eps, alpha_tmp))
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
    def find_two_center(entry_points):
        radius = INF
        center_1 = None
        center_2 = None
        for i in range(len(entry_points)):
            for j in range(i+1,len(entry_points)):
                min_radius = 0
                for k in range(len(entry_points)):
                    if i == j:
                        continue
                    p_i = entry_points[i].point
                    p_j = entry_points[j].point
                    p_k = entry_points[k].point
                    dis_k = min(p_i.distance(p_k), p_j.distance(p_k))
                    min_radius = max(min_radius, dis_k)
                if min_radius < radius:
                    radius, center_1, center_2 = min_radius,  entry_points[i], entry_points[j]
        return radius, center_1, center_2


    def insert_entry_point(self, point=None):
        if point is None:
            point = TwoCenterSimulator.generate_random_point(self.max_radius*math.sqrt(2)/2)
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
        tc_result = INF
        tcs_result = None
        for tcs in self.tc_solvers:
            tcs.insert_entry_point(new_entry_point)
            if tcs.radius < INF and tc_result == INF:
                tc_result = tcs.radius
                tcs_result = tcs
        expected_radius, expected_center_1, expected_center_2 = TwoCenterSimulator.find_two_center(self.alive_points)
        return (expected_center_1, expected_center_2, expected_radius, tcs_result)

    def demo_execute_one_cycle(self):
        expected_center_1, expected_center_2, expected_radius, tcs_result = self.execute_one_cycle()
        draw_tc_points_series([(get_points_of_entries(self.alive_points), expected_center_1.point, expected_center_2.point, expected_radius),
        tcs_result.get_points_for_draw()], cell_width=tcs_result.point_util.cell_width, max_radius=self.max_radius)
        # print self.current_time
        # print "Expected: ", expected_center_1, expected_center_2, expected_radius
        # print "Computed: ", tcs_result.center_1, tcs_result.center_2, tcs_result.radius
        # print self.alive_points
        # for tcs in self.tc_solvers:
        #     print tcs.alpha
        #     print tcs.my_alpha_entry_points
        #     print "-----------"
