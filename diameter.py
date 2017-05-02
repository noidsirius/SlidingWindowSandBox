import random
import math

from itertools import combinations

from utils import *

from geometry_opt_sw import GeometryOptSWSolver

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


class DiameterSolver(GeometryOptSWSolver):
    def __init__(self, eps, max_result_value):
        super(DiameterSolver, self).__init__(eps, max_result_value, DiameterSolver.find_diameter)

    @staticmethod
    def find_diameter(entry_points, geometry_solver=None):
        point_util = None
        if geometry_solver:
            point_util = geometry_solver.point_util
        if len(entry_points) < 2:
            corner_old, corner_new = entry_points[0], entry_points[0]
            diameter = 0
            return diameter, (corner_old, corner_new)

        diameter = 0
        corner_old, corner_new = None, None
        for possible_corners in combinations(entry_points, 2):
            tmp_diameter = get_distance_from_point(possible_corners[0], possible_corners[1], point_util)
            if tmp_diameter >= diameter:
                diameter, corner_old, corner_new = tmp_diameter, possible_corners[0], possible_corners[1]

        if corner_old is not None:
            return diameter, (corner_old, corner_new)
        return diameter, None

    def clear_extra_entry_points(self):
        most_recent_farthest_ep_index = -1
        for i, ep_i in enumerate(self.entry_points):
            for j, ep_j in enumerate(self.entry_points[i + 1:]):
                if get_distance_from_point(ep_i, ep_j, self.point_util) > self.max_valid_distance():
                    most_recent_farthest_ep_index = i
        if most_recent_farthest_ep_index != -1:
            self.entry_points = self.entry_points[most_recent_farthest_ep_index:]
            return True
        return False

    def does_new_point_fit(self, new_entry_point):
        if self.extra_data:
            corner_old, corner_new = self.extra_data
            if corner_old.is_alive() and corner_new.is_alive():
                return is_in_circle(new_entry_point, corner_old, corner_new, self.point_util)
                # cell_dis = get_distance_from_point(new_entry_point, self.centers, self.point_util)
                # if cell_dis <= self.max_valid_distance():
                #     self.radius = max(self.radius, cell_dis)
                #     return True
        return False
