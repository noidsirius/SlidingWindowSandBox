import random
import math

from itertools import combinations

from utils import *


def get_min_distance_from_points(source, entry_points, point_util=None):
    if point_util:
        dis = min([point_util.get_cell_distance(ep.point, source.point) for ep in entry_points])
    else:
        dis = min([ep.point.distance(source.point) for ep in entry_points])
    return dis

class KCenterSolver:
    def __init__(self, k, eps, alpha):
        self.my_alpha_entry_points = []
        self.centers = []
        self.radius = INF
        self.alpha = alpha
        self.eps = eps
        self.k = k
        self.point_util = PointUtil(self.eps, self.alpha)

    @staticmethod
    def find_k_center(entry_points, k, point_util = None):
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

    def insert_entry_point(self, new_entry_point):
        for ep in self.my_alpha_entry_points:
            if not ep.is_alive() or self.point_util.is_in_same_cell(ep.point, new_entry_point.point):
                self.my_alpha_entry_points.remove(ep)
        self.my_alpha_entry_points.append(new_entry_point)
        max_valid_distance = self.alpha *(1 + self.eps)
        if self.centers and all([c.is_alive() for c in  self.centers]):
            cell_dis = get_min_distance_from_points(new_entry_point, self.centers, self.point_util)
            if cell_dis <= max_valid_distance:
                self.radius = max(self.radius, cell_dis)
                return
        r_radius, r_centers = KCenterSolver.find_k_center(self.my_alpha_entry_points, self.k, self.point_util)
        if len(self.my_alpha_entry_points) <= self.k:
            self.centers = [c for c in self.my_alpha_entry_points]
            if len(self.centers) < self.k:
                self.centers += [self.my_alpha_entry_points[0] for i in range(self.k - len(self.centers))]
            self.radius = 0
        elif r_radius <= max_valid_distance:
            self.centers = r_centers
            self.radius = r_radius
        else:
            selected_points = [new_entry_point]
            most_recent_farthest_ep = None
            for ep in reversed(self.my_alpha_entry_points):
                if get_min_distance_from_points(ep, selected_points, self.point_util) > 2*max_valid_distance:
                    if len(selected_points) == self.k:
                        most_recent_farthest_ep = ep
                        break
                    selected_points.append(ep)
            if most_recent_farthest_ep:
                for ep in self.my_alpha_entry_points:
                    cell_dis = get_min_distance_from_points(ep, selected_points, self.point_util)
                    if ep != most_recent_farthest_ep and \
                            cell_dis> 2 * max_valid_distance:
                        self.my_alpha_entry_points.remove(ep)
            self.centers = None
            self.radius = INF

    def get_points_for_draw(self):
        points = [self.point_util.get_point_address(ep.point).get_center_point() for ep in self.my_alpha_entry_points]
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
            kcs.insert_entry_point(new_entry_point)
            if kcs.radius < INF and kc_result == INF:
                kc_result = kcs.radius
                kcs_result = kcs
        expected_radius, expected_centers = KCenterSolver.find_k_center(self.alive_points, self.k)
        if expected_radius == 0:
                expected_centers = [c for c in self.alive_points]
                if len(expected_centers) < self.k:
                    expected_centers += [self.alive_points[0] for i in range(self.k - len(expected_centers))]
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
        #     print tcs.my_alpha_entry_points
        #     print "-----------"
