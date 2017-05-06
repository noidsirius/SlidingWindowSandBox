from utils import *


class GeometryOptSWSolver(object):
    def __init__(self, eps, max_result_value, approx_factor=1):
        self.entry_points = []
        self.result = INF
        self.approx_factor = approx_factor
        self.extra_data = None
        self.max_result_value = max_result_value
        self.eps = eps
        self.point_util = PointUtil(self.eps, self.max_result_value)

    def max_valid_distance(self):
        return self.max_result_value * (1 + self.eps) * self.approx_factor

    def find_result(self, entry_points, geometry_solver=None):
        return INF, None

    def insert_entry_point(self, new_entry_point):
        for ep in self.entry_points:
            if not ep.is_alive() or self.point_util.is_in_same_cell(ep.point, new_entry_point.point):
                self.entry_points.remove(ep)
        self.entry_points.append(new_entry_point)

    # If there is no solution for this generic_solver, this method clears useless eps
    # TODO: should change the name
    def clear_extra_entry_points(self, new_entry_point=None):
        return False

    # check if this new point doesn't affect the result
    # TODO: it's better to change the name
    def does_new_point_fit(self, new_entry_point):
        return False

    def execute_one_cycle(self, new_entry_point):
        self.insert_entry_point(new_entry_point)
        if self.does_new_point_fit(new_entry_point):
            return

        if self.clear_extra_entry_points(new_entry_point):
            self.extra_data = None
            self.result = INF

        r_result, r_extra_data = self.find_result(self.entry_points, self)
        if r_result <= self.max_valid_distance():
            self.extra_data = r_extra_data
            self.result = r_result
        else:
            self.extra_data = None
            self.result = INF

    def get_points_for_draw(self):
        points = [self.point_util.get_point_address(ep.point).get_center_point() for ep in self.entry_points]
        return points


class GeometryOptSWSimulator:
    def __init__(self, geometry_opt_sw_solver_class, eps, max_radius=MAX_RADIUS, window_size=WINDOW_SIZE, approx_factor=1):
        self.eps = eps
        self.max_radius = max_radius
        self.gosw_solvers = []
        self.current_time = 0
        self.window_size = window_size
        self.entry_points = []
        self.alive_points = []
        self.approx_factor = approx_factor

        # Create parallel solvers
        alpha_tmp = self.eps
        eps_tmp = eps / 2
        d_count = int(math.log(self.max_radius/eps_tmp, (1+eps_tmp))) + 1
        for i in range(d_count):
            self.gosw_solvers.append(geometry_opt_sw_solver_class(self.eps, alpha_tmp, approx_factor=self.approx_factor))
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

    def execute_one_cycle(self, new_point=None, debug_method=None):
        new_entry_point = self.insert_entry_point(new_point)
        result = INF
        solver_result = None
        for solver in self.gosw_solvers:
            solver.execute_one_cycle(new_entry_point)
            if solver.result < INF and result == INF:
                result = solver.result
                solver_result = solver
        if debug_method:
            return solver_result, debug_method(self.alive_points)
        else:
            return solver_result

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
