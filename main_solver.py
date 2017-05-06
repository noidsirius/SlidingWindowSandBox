import sys
import math


from utils import Point, PointUtil, MAX_RADIUS, get_point_coord
from geometry_opt_sw import GeometryOptSWSimulator
from solvers import DiameterSolver, KCenterSolver, KCenterCalculator


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
                    print("Problem with input")
                input_points += [Point(x,y) for i in range(number_of_points)]
            elif cmd == 'insert_in_range':
                x_0, y_0, x_1, y_1 = [float(arg) for arg in args[2:6]]
                input_points += [PointUtil.generate_customized_random_point \
                (x_0, y_0, x_1, y_1) for i in range(number_of_points)]
    if len(input_points) == 0:
        input_points = None
    return input_points, eps, max_radius, window_size


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


def run_simulator(simulation_time=10000, eps=0.7, max_radius=10000, window_size=100, input_points=None,
                    solver=DiameterSolver, debug_method=DiameterSolver.find_diameter):
    d_simulator = GeometryOptSWSimulator(solver, eps, max_radius=max_radius, window_size=window_size)
    if input_points:
        simulation_time = len(input_points)
    for i in range(simulation_time):
        new_point = input_points[i] if input_points else None
        ds_result, expected_data = d_simulator.execute_one_cycle(new_point, debug_method)
        expected_diameter, expected_corners = expected_data
        if expected_diameter == 0:
            print("Diameter is 0,", ds_result.result)
            continue

        is_correct = ds_result.max_result_value <= expected_diameter <= ds_result.max_result_value * (1+eps)
        print(d_simulator.current_time, is_correct, ds_result.max_result_value, expected_diameter, ds_result.result)

        # in case of any bug
        if is_correct == False and not expected_diameter <= d_simulator.eps :
            print("OHOH")
            # print oc_simulator.current_time, is_correct , expected_radius, ocs_result.radius
            # draw_oc_points_series([(get_points_of_entries(oc_simulator.alive_points), expected_center.point, expected_radius),
            # ocs_result.get_points_for_draw()], ocs_result.point_util.cell_width)
            # print oc_simulator.alive_points, ocs_result.entry_points, ocs_result.alpha
            break




if __name__ == "__main__":
    if len(sys.argv) == 1:
        # run_simulator()
        # run_simulator(k=1, simulation_time=40, eps=0.95, max_radius=10, window_size=10)
        run_simulator(simulation_time=10000, eps=0.5, max_radius=10, window_size=30, solver=KCenterSolver,
                      debug_method=KCenterCalculator(1).find_k_center)
    else:
        points, eps, max_radius, window_size = init_points(sys.argv[1])
        run_simulator(eps=eps, max_radius=max_radius, window_size=window_size, input_points=points)
