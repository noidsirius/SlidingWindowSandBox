import random
import math

from utils import *

WINDOW_SIZE = 10
entry_points = []
alive_points = []
current_time = 0
max_radius = 10

class EntryPoint:

    def __init__(self, point, entry_time=0):
        self.point = point
        self.age = 0
        self.entry_time = entry_time
        self.point_addr = None

    def increase_age_one(self):
        self.age += 1

    def is_alive(self):
        return self.age < WINDOW_SIZE

    def __str__(self):
        return "(%d, %d, %s)" %(self.entry_time, self.age, self.point)

    def __repr__(self):
        return "(%d, %d, %s)" %(self.entry_time, self.age, self.point)

def generate_random_point(max_radius=MAX_ALPHA):
    x = random.random() * max_radius - max_radius/2
    y = random.random() * max_radius - max_radius/2
    return Point(x, y)

def insert_entry_point(point = None):
    global current_time
    if point is None:
        point = generate_random_point(max_radius*math.sqrt(2)/2)
    new_entry_point = EntryPoint(point, current_time)
    current_time += 1
    entry_points.append(new_entry_point)
    for ep in alive_points:
        ep.increase_age_one()
    alive_points.append(new_entry_point)
    if len(alive_points) > WINDOW_SIZE:
        alive_points.pop(0)
    return new_entry_point

def get_points_of_entries(entry_points):
    return [ep.point for ep in entry_points]

def find_one_center(entry_points):
    radius = INF
    center = None
    for i in range(len(entry_points)-1):
        min_i_radius = 0
        min_i_radius = max([ep.point.distance(entry_points[i].point) for ep in entry_points[i+1:]])
        # for ep in entry_points[i+1:]:
        #     min_i_radius = max(min_i_radius, ep.point.distance(entry_points[i].point))
        if min_i_radius < radius:
            radius, center = min_i_radius,  entry_points[i]
    return radius, center

def find_one_cell_center(entry_points, point_util):
    radius = INF
    center = None
    for i in range(len(entry_points)-1):
        min_i_radius = max([point_util.get_cell_distance(ep.point, entry_points[i].point) for ep in entry_points[i+1:]])
        # for ep in entry_points[i+1:]:
        #     min_i_radius = max(min_i_radius, point_util.get_cell_distance(ep.point, entry_points[i].point))
        if min_i_radius < radius:
            radius, center = min_i_radius,  entry_points[i]
    return radius, center

class OneCenterSolver:
    def __init__(self, eps, alpha):
        self.my_alpha_entry_points = []
        self.center = None
        self.radius = INF
        self.alpha = alpha
        self.eps = eps
        self.point_util = PointUtil(self.eps, self.alpha)

    def insert_entry_point(self, new_entry_point):
        for ep in self.my_alpha_entry_points:
            if not ep.is_alive():
                self.my_alpha_entry_points.remove(ep)
        self.my_alpha_entry_points.append(new_entry_point)
        r_radius, r_center = find_one_cell_center(self.my_alpha_entry_points, self.point_util)
        if r_center is None and len(self.my_alpha_entry_points) == 1:
            self.center = self.my_alpha_entry_points[0]
            self.radius = 0
        elif r_radius < self.alpha *(1 + self.eps):
            self.center = r_center
            self.radius = r_radius
        else:
            for ep in self.my_alpha_entry_points:
                if self.point_util.get_cell_distance(new_entry_point.point, ep.point) > 2 * (self.alpha * (1+self.eps)):
                    self.my_alpha_entry_points.remove(ep)
            self.center = None
            self.radius = INF

# oc_solver_3 = OneCenterSolver(0.1, 3)
#
# for i in range(20):
#     new_entry_point = insert_entry_point()
#     oc_solver_3.insert_entry_point(new_entry_point)
#     print len(oc_solver_3.my_alpha_entry_points)
#     print current_time, find_one_center(alive_points)[0], (oc_solver_3.radius, oc_solver_3.center)[0]
#     print "-------------------"


oc_solvers = []

eps_tmp = 0.5
alpha_tmp = eps_tmp
oc_count = int(math.log(max_radius/eps_tmp, (1+eps_tmp))) + 1
for i in range(oc_count):
    oc_solvers.append( OneCenterSolver(eps_tmp, alpha_tmp))
    alpha_tmp *= 1 + eps_tmp

def just_do_it():
    for i in range(100):
        new_entry_point = insert_entry_point()
        oc_result = INF
        ocs_result = None
        for ocs in oc_solvers:
            ocs.insert_entry_point(new_entry_point)
            if ocs.radius < INF and oc_result == INF:
                oc_result = ocs.radius
                ocs_result = ocs
        # print len(oc_solver_3.my_alpha_entry_points)
        expected_radius, expected_center = find_one_center(alive_points)
        # print current_time, expected_radius, oc_result, (oc_result / expected_radius)
        is_correct = (oc_result / expected_radius) < (1 + eps_tmp*1.1)

        print current_time, is_correct , expected_radius, oc_result
        if not is_correct:
            expected_points_str = ""
            x_points = []
            y_points = []
            plot_points = []
            for ep in alive_points:
                x_points.append(ep.point.x)
                y_points.append(ep.point.y)
                plot_points.append([ep.point.x, ep.point.y])
            oc_x_points = []
            oc_y_points = []
            for ep in ocs_result.my_alpha_entry_points:
                cell_point = ocs_result.point_util.get_point_address(ep.point).get_center_point()
                oc_x_points.append(cell_point.x)
                oc_y_points.append(cell_point.y)
                # plot_points.append([ep.point.x, ep.point.y])
            import matplotlib.pyplot as plt
            import numpy
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xticks(numpy.arange(-max_radius/2, max_radius/2, ocs_result.point_util.cell_width))
            ax.set_yticks(numpy.arange(-max_radius/2, max_radius/2, ocs_result.point_util.cell_width))
            plt.grid()
            circle1 = plt.Circle((expected_center.point.x, expected_center.point.y), max_radius, color='g')
            ax.add_artist(circle1)
            p = ax.plot(x_points, y_points, 'rs', oc_x_points, oc_y_points, 'b^')
            print plot_points
            # p = ax.plot(*zip(*plot_points), 'b')
            ax.set_xlabel('x-points')
            ax.set_ylabel('y-points')
            ax.set_title('Simple XY point plot')
            fig.show()
            break
        # for ep in alive_points:
        #     expected_points_str += str(ep.point)
        # print expected_points_str
        # our_points_str = ""
        # for ep in ocs.my_alpha_entry_points:
        #     our_points_str += str(ep.point)
        # print our_points_str

    # print "-------------------"
