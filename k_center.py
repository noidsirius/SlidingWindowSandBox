import random
import math

from itertools import combinations

from utils import *
from geometry_opt_sw import GeometryOptSWSolver

def get_min_distance_from_points(source, entry_points, point_util=None):
    if point_util:
        dis = min([point_util.get_cell_distance(ep.point, source.point) for ep in entry_points])
    else:
        dis = min([ep.point.distance(source.point) for ep in entry_points])
    return dis

k = 2
class TwoCenterSolver(GeometryOptSWSolver):
    def __init__(self, eps, max_result_value):
        super(TwoCenterSolver, self).__init__(eps, max_result_value, TwoCenterSolver.find_two_center)


    @staticmethod
    def find_two_center(entry_points, geometry_solver=None):
        point_util = None
        if geometry_solver:
            point_util = geometry_solver.point_util

        if len(entry_points) < k:
            centers = [entry_points[i % len(entry_points)] for i in range(k)]
            radius = 0
            return radius, centers

        radius = INF
        centers = None
        for possible_centers in combinations(entry_points, k):
            min_radius = 0
            for ep in entry_points:
                if ep in possible_centers:
                    continue
                dis = get_min_distance_from_points(ep, possible_centers, point_util)
                min_radius = max(min_radius, dis)
            if min_radius < radius:
                radius, centers = min_radius, possible_centers
        return radius, list(centers) if centers else None

    def clear_extra_entry_points(self, new_entry_point):
        selected_points = [new_entry_point]
        most_recent_farthest_ep = None
        for ep in reversed(self.entry_points):
            if get_min_distance_from_points(ep, selected_points, self.point_util) > 2 * self.max_valid_distance():
                if len(selected_points) == k:
                    most_recent_farthest_ep = ep
                    break
                selected_points.append(ep)
        if most_recent_farthest_ep:
            for ep in self.entry_points:
                cell_dis = get_min_distance_from_points(ep, selected_points, self.point_util)
                if ep != most_recent_farthest_ep and cell_dis > 2 * self.max_valid_distance():
                    self.entry_points.remove(ep)
            return True
        return False

    def does_new_point_fit(self, new_entry_point):
        centers = self.extra_data
        if centers and all([c.is_alive() for c in centers]):
            cell_dis = get_min_distance_from_points(new_entry_point, centers, self.point_util)
            if cell_dis <= self.max_valid_distance():
                self.result = max(self.result, cell_dis)
                return True
        return False


class KCenterSolver:
    def __init__(self, k, eps, alpha):
        self.entry_points = []
        self.centers = []
        self.radius = INF
        self.alpha = alpha
        self.eps = eps
        self.k = k
        self.point_util = PointUtil(self.eps, self.alpha)

    @staticmethod
    def find_k_center(entry_points, k, point_util = None):
        if len(entry_points) < k:
            centers = [entry_points[i%len(entry_points)] for i in range(k)]
            radius = 0
            return radius, centers

        radius = INF
        centers = None
        for possible_centers in combinations(entry_points, k):
            min_radius = 0
            for ep in entry_points:
                if ep in possible_centers:
                    continue
                dis = get_min_distance_from_points(ep, possible_centers, point_util)
                min_radius = max(min_radius, dis)
            if min_radius < radius:
                radius, centers = min_radius, possible_centers
        return radius, list(centers) if centers else None


    def max_valid_distance(self):
        return self.alpha *(1 + self.eps)

    def insert_entry_point(self, new_entry_point):
        for ep in self.entry_points:
            if not ep.is_alive() or self.point_util.is_in_same_cell(ep.point, new_entry_point.point):
                self.entry_points.remove(ep)
        self.entry_points.append(new_entry_point)

    # If there is no solution for this kc_solver, this method clears useless eps
    def clear_extra_entry_points(self, new_entry_point):
        selected_points = [new_entry_point]
        most_recent_farthest_ep = None
        for ep in reversed(self.entry_points):
            if get_min_distance_from_points(ep, selected_points, self.point_util) > 2 * self.max_valid_distance():
                if len(selected_points) == self.k:
                    most_recent_farthest_ep = ep
                    break
                selected_points.append(ep)
        if most_recent_farthest_ep:
            for ep in self.entry_points:
                cell_dis = get_min_distance_from_points(ep, selected_points, self.point_util)
                if ep != most_recent_farthest_ep and cell_dis> 2 * self.max_valid_distance():
                    self.entry_points.remove(ep)
            return True
        return False

    def does_new_point_fit(self, new_entry_point):
        if self.centers and all([c.is_alive() for c in  self.centers]):
            cell_dis = get_min_distance_from_points(new_entry_point, self.centers, self.point_util)
            if cell_dis <= self.max_valid_distance():
                self.radius = max(self.radius, cell_dis)
                return True
        return False

    def execute_one_cycle(self, new_entry_point):
        self.insert_entry_point(new_entry_point)
        if self.does_new_point_fit(new_entry_point):
            return

        r_radius, r_centers = KCenterSolver.find_k_center(self.entry_points, self.k, self.point_util)
        if r_radius <= self.max_valid_distance():
            self.centers = r_centers
            self.radius = r_radius
        else:
            self.clear_extra_entry_points(new_entry_point)
            self.centers = None
            self.radius = INF

    def get_points_for_draw(self):
        points = [self.point_util.get_point_address(ep.point).get_center_point() for ep in self.entry_points]
        centers = [self.point_util.get_point_address(center.point).get_center_point() for center in self.centers] if self.centers else None
        radius = self.radius
        return (points, centers, radius)


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


class KCenterSimulator:
    def __init__(self, k, eps, max_radius=MAX_RADIUS, window_size=WINDOW_SIZE):
        self.k = k
        self.eps = eps
        self.max_radius = max_radius
        self.kc_solvers = []
        self.current_time = 0
        self.window_size = window_size
        self.entry_points = []
        self.alive_points = []

        # Create parallel kc_solvers
        alpha_tmp = self.eps
        eps_tmp = eps / 2
        kc_count = int(math.log(self.max_radius/eps_tmp, (1+eps_tmp))) + 1
        for i in range(kc_count):
            self.kc_solvers.append( KCenterSolver(self.k, self.eps, alpha_tmp))
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
        kc_result = INF
        kcs_result = None
        for kcs in self.kc_solvers:
            kcs.execute_one_cycle(new_entry_point)
            if kcs.radius < INF and kc_result == INF:
                kc_result = kcs.radius
                kcs_result = kcs
        expected_radius, expected_centers = KCenterSolver.find_k_center(self.alive_points, self.k)
        return (expected_centers, expected_radius, kcs_result)

    def demo_execute_one_cycle(self):
        expected_centers, expected_radius, kcs_result = self.execute_one_cycle()
        draw_kc_points_series([(get_points_of_entries(self.alive_points), get_points_of_entries(expected_centers), expected_radius),
        kcs_result.get_points_for_draw()], cell_width=kcs_result.point_util.cell_width, max_radius=self.max_radius)
        # print self.current_time
        # print "Expected: ", expected_center_1, expected_center_2, expected_radius
        # print "Computed: ", tcs_result.center_1, tcs_result.center_2, tcs_result.radius
        # print self.alive_points
        # for tcs in self.tc_solvers:
        #     print tcs.alpha
        #     print tcs.entry_points
        #     print "-----------"
