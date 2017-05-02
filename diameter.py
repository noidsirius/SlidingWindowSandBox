import random
import math

from itertools import combinations

from utils import *


def get_distance_from_point(source, target, point_util=None):
    if point_util:
        dis = point_util.get_cell_distance(source.point, target.point)
    else:
        dis = source.point.distance(target.point)
    return dis


def is_in_circle(source, c_ep_1, c_ep_2, point_util=None):

    if point_util:
        # TODO need refactor
        cep1_addr = point_util.get_point_address(c_ep_1.point)
        cep2_addr = point_util.get_point_address(c_ep_2.point)
        center_addr = PointAddress((cep1_addr.x_addr+cep2_addr.x_addr)/2.0,(cep1_addr.y_addr+cep2_addr.y_addr)/2.0, point_util.cell_width)
        radius = point_util.get_cell_distance(c_ep_1.point, c_ep_2.point) / (2*(1+point_util.eps))
        return center_addr.distance( point_util.get_point_address(source.point)) <= radius
    else:
        center = c_ep_1.get_middle(c_ep_2)
        radius = c_ep_1.distance(c_ep_2.point) / 2
        return center.distance(source.point) <= radius


class DiameterSolver:
    def __init__(self, eps, alpha):
        self.entry_points = []
        self.corner_old = None
        self.corner_new = None
        self.diameter = INF
        self.alpha = alpha
        self.eps = eps
        self.point_util = PointUtil(self.eps, self.alpha)
        self.test_int = 0

    @staticmethod
    def find_diameter(entry_points, point_util = None):
        if len(entry_points) < 2:
            corner_old, corner_new = entry_points[0], entry_points[0]
            diameter = 0
            return diameter, corner_old, corner_new

        diameter = 0
        corner_old, corner_new = None, None
        for possible_corners in combinations(entry_points, 2):
            tmp_diameter = get_distance_from_point(possible_corners[0], possible_corners[1], point_util)
            if tmp_diameter >= diameter:
                diameter, corner_old, corner_new = tmp_diameter, possible_corners[0], possible_corners[1]
        return diameter, corner_old, corner_new

    def max_valid_distance(self):
        return self.alpha *(1 + self.eps)

    def insert_entry_point(self, new_entry_point):
        for ep in self.entry_points:
            if not ep.is_alive() or self.point_util.is_in_same_cell(ep.point, new_entry_point.point):
                self.entry_points.remove(ep)
        self.entry_points.append(new_entry_point)

    # If there is no solution for this kc_solver, this method clears useless eps
    def clear_extra_entry_points(self):
        most_recent_farthest_ep_index = -1
        for i, ep_i in enumerate(self.entry_points):
            for j, ep_j in enumerate(self.entry_points[i+1:]):
                if get_distance_from_point(ep_i, ep_j, self.point_util) > self.max_valid_distance():
                    most_recent_farthest_ep_index = i
        if most_recent_farthest_ep_index != -1:
            self.entry_points = self.entry_points[most_recent_farthest_ep_index:]
            return True
        return False

    def does_new_point_fit(self, new_entry_point):
        if self.corner_old and self.corner_new and self.corner_old.is_alive() and self.corner_new.is_alive():
            return is_in_circle(new_entry_point, self.corner_old, self.corner_new, self.point_util)
            # cell_dis = get_distance_from_point(new_entry_point, self.centers, self.point_util)
            # if cell_dis <= self.max_valid_distance():
            #     self.radius = max(self.radius, cell_dis)
            #     return True
        return False

    def execute_one_cycle(self, new_entry_point):
        self.insert_entry_point(new_entry_point)
        if self.does_new_point_fit(new_entry_point):
            self.test_int += 1
            return

        r_diameter, r_corner_old, r_corner_new = DiameterSolver.find_diameter(self.entry_points, self.point_util)
        if r_diameter <= self.max_valid_distance():
            self.corner_old = r_corner_old
            self.corner_new = r_corner_new
            self.diameter = r_diameter
        else:
            self.clear_extra_entry_points()
            self.corner_old = None
            self.corner_new = None
            self.diameter = INF

    def get_points_for_draw(self):
        points = [self.point_util.get_point_address(ep.point).get_center_point() for ep in self.entry_points]
        # centers = [self.point_util.get_point_address(center.point).get_center_point() for center in
        #            self.centers] if self.centers else None
        # radius = self.radius
        return (points, None, None)


# point_series => [entry_points, centers, radius]
def draw_kc_points_series(point_series, cell_width = 1, is_point_class=True, max_radius=MAX_RADIUS):

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
    for points, centers, radius in point_series:
        index += 1
        color = colors[index%len(colors)]
        shape = shapes[index%len(shapes)]
        x_points = []
        y_points = []
        for p in points:
            x, y = get_point_coord(p, is_point_class)
            x_points.append(x)
            y_points.append(y)
        if centers:
            for center in centers:
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


class DiameterSimulator:
    def __init__(self, eps, max_radius=MAX_RADIUS, window_size=WINDOW_SIZE):
        self.eps = eps
        self.max_radius = max_radius
        self.d_solvers = []
        self.current_time = 0
        self.window_size = window_size
        self.entry_points = []
        self.alive_points = []

        # Create parallel kc_solvers
        alpha_tmp = self.eps
        eps_tmp = eps / 2
        d_count = int(math.log(self.max_radius/eps_tmp, (1+eps_tmp))) + 1
        for i in range(d_count):
            self.d_solvers.append( DiameterSolver(self.eps, alpha_tmp))
            alpha_tmp *= 1 + eps_tmp

    def insert_entry_point(self, point=None):
        if point is None:
            point = PointUtil.generate_random_point(self.max_radius*math.sqrt(2)/2)
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
        d_result = INF
        ds_result = None
        for ds in self.d_solvers:
            ds.execute_one_cycle(new_entry_point)
            if ds.diameter < INF and d_result == INF:
                d_result = ds.diameter
                ds_result = ds
        expected_diameter, expected_center_old, expected_center_new = DiameterSolver.find_diameter(self.alive_points)
        return (expected_center_old, expected_center_new, expected_diameter, ds_result)

    # def demo_execute_one_cycle(self):
    #     expected_centers, expected_radius, kcs_result = self.execute_one_cycle()
    #     draw_kc_points_series(
    #         [(get_points_of_entries(self.alive_points), get_points_of_entries(expected_centers), expected_radius),
    #          kcs_result.get_points_for_draw()], cell_width=kcs_result.point_util.cell_width, max_radius=self.max_radius)
    #     # print self.current_time
    #     # print "Expected: ", expected_center_1, expected_center_2, expected_radius
    #     # print "Computed: ", tcs_result.center_1, tcs_result.center_2, tcs_result.radius
    #     # print self.alive_points
    #     # for tcs in self.tc_solvers:
    #     #     print tcs.alpha
    #     #     print tcs.entry_points
    #     #     print "-----------"
