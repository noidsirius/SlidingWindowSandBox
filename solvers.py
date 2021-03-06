from itertools import combinations

from geometry_opt_sw import GeometryOptSWSolver
from utils import INF, PointUtil


class KCenterCalculator:
    def __init__(self, k):
        self.k = k

    def find_k_center(self, entry_points, geometry_solver=None):
        point_util = None
        if geometry_solver:
            point_util = geometry_solver.point_util

        if len(entry_points) < self.k:
            centers = [entry_points[i % len(entry_points)] for i in range(self.k)]
            radius = 0
            return radius, centers

        radius = INF
        centers = None
        for possible_centers in combinations(entry_points, self.k):
            min_radius = 0
            for ep in entry_points:
                if ep in possible_centers:
                    continue
                dis = PointUtil.get_min_distance_from_points(ep, possible_centers, point_util)
                min_radius = max(min_radius, dis)
            if min_radius < radius:
                radius, centers = min_radius, possible_centers
        return radius, list(centers) if centers else None

    def find_approx_k_center(self, entry_points, geometry_solver=None):
        point_util = None
        if geometry_solver:
            point_util = geometry_solver.point_util

        if len(entry_points) <= self.k:
            centers = [entry_points[i % len(entry_points)] for i in range(self.k)]
            radius = 0
            return radius, centers

        centers = [entry_points[0]]
        for i in range(1,self.k):
            next_center = None
            distance = 0
            for ep in entry_points:
                ep_dis = PointUtil.get_min_distance_from_points(ep, centers, point_util)
                if distance < ep_dis:
                    distance = ep_dis
                    next_center = ep
            centers.append(next_center)

        radius = 0
        for ep in entry_points:
            if ep in centers:
                continue
            radius = max(radius, PointUtil.get_min_distance_from_points(ep, centers, point_util))
        return radius, list(centers) if centers else None

class KCenterSolver(GeometryOptSWSolver):
    def __init__(self, eps, max_result_value, approx_factor=1, k=4):
        self.k = k
        super(KCenterSolver, self).__init__(eps, max_result_value, approx_factor=approx_factor)
        self.k_center_calculator = KCenterCalculator(self.k)

    def find_result(self, entry_points, geometry_solver=None):
        approx = True
        if approx:
            return self.k_center_calculator.find_approx_k_center(entry_points, geometry_solver=geometry_solver)
        else:
            return self.k_center_calculator.find_k_center(entry_points, geometry_solver=geometry_solver)

    def clear_extra_entry_points(self, new_entry_point):
        selected_points = [new_entry_point]
        most_recent_farthest_ep = None
        for ep in reversed(self.entry_points):
            if PointUtil.get_min_distance_from_points(ep, selected_points, self.point_util) > 2 * self.max_valid_distance():
                if len(selected_points) == self.k:
                    most_recent_farthest_ep = ep
                    break
                selected_points.append(ep)
        if most_recent_farthest_ep:
            for ep in self.entry_points:
                cell_dis = PointUtil.get_min_distance_from_points(ep, selected_points, self.point_util)
                if ep != most_recent_farthest_ep and cell_dis > 2 * self.max_valid_distance():
                    self.entry_points.remove(ep)
            return True
        return False

    def does_new_point_fit(self, new_entry_point):
        centers = self.extra_data
        if centers and all([c.is_alive() for c in centers]):
            cell_dis = PointUtil.get_min_distance_from_points(new_entry_point, centers, self.point_util)
            if cell_dis <= self.max_valid_distance():
                self.result = max(self.result, cell_dis)
                return True
        return False


class DiameterSolver(GeometryOptSWSolver):
    def __init__(self, eps, max_result_value, approx_factor=1):
        super(DiameterSolver, self).__init__(eps, max_result_value, approx_factor=approx_factor)

    def find_result(self, entry_points, geometry_solver=None):
        return DiameterSolver.find_diameter(entry_points, geometry_solver)

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
            tmp_diameter = PointUtil.get_distance_from_point(possible_corners[0], possible_corners[1], point_util)
            if tmp_diameter >= diameter:
                diameter, corner_old, corner_new = tmp_diameter, possible_corners[0], possible_corners[1]

        if corner_old is not None:
            return diameter, (corner_old, corner_new)
        return diameter, None

    def clear_extra_entry_points(self, new_entry_point):
        most_recent_farthest_ep_index = -1
        for i, ep_i in enumerate(self.entry_points):
            for j, ep_j in enumerate(self.entry_points[i + 1:]):
                if PointUtil.get_distance_from_point(ep_i, ep_j, self.point_util) > self.max_valid_distance():
                    most_recent_farthest_ep_index = i
        if most_recent_farthest_ep_index != -1:
            self.entry_points = self.entry_points[most_recent_farthest_ep_index:]
            return True
        return False

    def does_new_point_fit(self, new_entry_point):
        if self.extra_data:
            corner_old, corner_new = self.extra_data
            if corner_old.is_alive() and corner_new.is_alive():
                return PointUtil.is_in_circle(new_entry_point, corner_old, corner_new, self.point_util)
                # cell_dis = get_distance_from_point(new_entry_point, self.centers, self.point_util)
                # if cell_dis <= self.max_valid_distance():
                #     self.radius = max(self.radius, cell_dis)
                #     return True
        return False
