import sys
import math

from k_center import KCenterSimulator, draw_kc_points_series
from utils import Point, get_points_of_entries, PointUtil

def run_simulator(k=1, simulation_time=10000, eps=0.7, max_radius=10000, window_size=100, input_points=None):
    kc_simulator = KCenterSimulator(k, eps, max_radius=max_radius, window_size=window_size)
    if input_points:
        simulation_time = len(input_points)
    for i in range(simulation_time):
        new_point = input_points[i] if input_points else None
        expected_centers, expected_radius, kcs_result = kc_simulator.execute_one_cycle(new_point)
        if len(kc_simulator.alive_points) <= k or expected_radius == 0:
            print "Radius is 0,", kcs_result.radius
            continue

        # is_correct = (ocs_result.radius / expected_radius) <= (1 + eps) and expected_radius <= ocs_result.radius
        is_correct = kcs_result.alpha <= expected_radius <= kcs_result.alpha * (1+eps)
        print kc_simulator.current_time, is_correct, kcs_result.alpha, expected_radius, kcs_result.radius
        # print oc_simulator.current_time, is_correct, ocs_result.radius, expected_radius ,\
        #  len(oc_simulator.alive_points),\
        #  len(ocs_result.my_alpha_entry_points),\
        #   [len(ocs.my_alpha_entry_points) for ocs in oc_simulator.oc_solvers]

        # in case of any bug
        if is_correct == False and not expected_radius <= kc_simulator.eps :
            # print oc_simulator.current_time, is_correct , expected_radius, ocs_result.radius
            # draw_oc_points_series([(get_points_of_entries(oc_simulator.alive_points), expected_center.point, expected_radius),
            # ocs_result.get_points_for_draw()], ocs_result.point_util.cell_width)
            # print oc_simulator.alive_points, ocs_result.my_alpha_entry_points, ocs_result.alpha
            break

def init_points(file_name):
    input_points = []
    with open(file_name, 'r') as file:
        simulator_configure = file.readline().strip().split(' ')
        eps = float(simulator_configure[0])
        max_radius = float(simulator_configure[1])
        window_size = int(simulator_configure[2])
        max_axis_length = max_radius * math.sqrt(2)/2
        for line in file.readlines():
            args = line.strip().split(' ')
            cmd = args[0]
            number_of_points = int(args[1])
            if cmd == 'insert_random':
                input_points += [PointUtil.generate_random_point(max_axis_length)\
                                    for i in range(number_of_points)]
            elif cmd == 'insert_exact':
                x = float(args[2])
                y = float(args[2])
                if not(-max_axis_length/2 < x < max_axis_length/2 and \
                        -max_axis_length/2 < y < max_axis_length/2):
                    print "Problem with input"
                input_points += [Point(x,y) for i in range(number_of_points)]
            elif cmd == 'insert_in_range':
                x_0, y_0, x_1, y_1 = [float(arg) for arg in args[2:6]]
                input_points += [PointUtil.generate_customized_random_point \
                (x_0, y_0, x_1, y_1) for i in range(number_of_points)]
    if len(input_points) == 0:
        input_points = None
    return input_points, eps, max_radius, window_size


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # run_simulator()
        # run_simulator(k=1, simulation_time=40, eps=0.95, max_radius=10, window_size=10)
        run_simulator(k=3, simulation_time=100, eps=0.95, max_radius=100, window_size=30)
    else:
        points, eps, max_radius, window_size = init_points(sys.argv[1])
        run_simulator(eps=eps, max_radius=max_radius, window_size=window_size, input_points=points)
