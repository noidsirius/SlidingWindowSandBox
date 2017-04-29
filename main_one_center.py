from one_center import OneCenterSimulator, draw_oc_points_series, get_points_of_entries



def run_simulator(simulation_time=10000, eps=0.5, max_radius=10000, window_size=100):
    oc_simulator = OneCenterSimulator(eps, max_radius=max_radius, window_size=window_size)
    for i in range(simulation_time):
        expected_center, expected_radius, ocs_result = oc_simulator.execute_one_cycle()
        if len(oc_simulator.alive_points) == 1:
            print "It's only one point"
            continue

        is_correct = (ocs_result.radius / expected_radius) < (1 + oc_simulator.eps*1.1) and expected_radius <= ocs_result.radius

        print oc_simulator.current_time, is_correct , len(oc_simulator.alive_points),\
         len(ocs_result.my_alpha_entry_points),\
          [len(ocs.my_alpha_entry_points) for ocs in oc_simulator.oc_solvers]

        # in case of any bug
        if is_correct == False and not expected_radius <= oc_simulator.eps :
            print oc_simulator.current_time, is_correct , expected_radius, ocs_result.radius
            draw_oc_points_series([(get_points_of_entries(oc_simulator.alive_points), expected_center.point, expected_radius),
            ocs_result.get_points_for_draw()], ocs_result.point_util.cell_width)
            print oc_simulator.alive_points, ocs_result.my_alpha_entry_points, ocs_result.alpha
            break


if __name__ == "__main__":
    run_simulator()
