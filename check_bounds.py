import math

from utils import Point

# alpha = 1
eps = 0.05
base_delta = eps / (1.0*2*math.sqrt(2))

def calculate_bounds(delta, alpha):
    # delta = 0.5
    m = int(alpha/delta) + 1
    # m = int((1.0*2*math.sqrt(2))/eps) + 1
    # delta = 1.0 * alpha / m
    INF = alpha*10 + delta

    def get_corners(i,j):
        ret_list = []
        center_point = Point(i*delta + delta/2, j*delta + delta/2)
        for d_x in [-delta/2, delta/2]:
            for d_y in [-delta/2, delta/2]:
                ret_list.append( center_point.move(Point(d_x, d_y)))
        return ret_list

    def get_min_max_dis(point_addr_1, point_addr_2):
        from_points = get_corners(*point_addr_1)
        to_points = get_corners(*point_addr_2)
        min_dis = INF
        max_dis = 0
        for p1 in from_points:
            for p2 in to_points:
                dis = p1.distance(p2)
                min_dis = min(min_dis, dis)
                max_dis = max(max_dis, dis)
        return min_dis, max_dis

    point_address_x_range = (-m, m+1)
    point_address_y_range = (-m, m+1)

    base_address = (0, 0)
    min_dis = INF
    max_dis = 0
    valid_cells = 0
    for i in range(*point_address_x_range):
        for j in range(*point_address_y_range):
            if i == 0 and j == 0:
                continue
            tmp_min, tmp_max = get_min_max_dis(base_address, (i,j))
            # print m * delta,tmp_min, tmp_max, max(alpha-tmp_min, tmp_max - alpha), max(alpha-tmp_min, tmp_max - alpha)/alpha, i, j
            if tmp_max < alpha or tmp_min > alpha:
                continue
            valid_cells += 1
            min_dis = min(min_dis, tmp_min)
            max_dis = max(max_dis, tmp_max)


    # print min_dis, m * delta, max_dis, max(alpha-min_dis, max_dis - alpha)
    # print max(alpha-min_dis, max_dis - alpha)/alpha, delta, alpha, (2*m+1)**2, (max(alpha-min_dis, max_dis - alpha)/alpha) / delta
    # print max(alpha-min_dis, max_dis - alpha) / delta, valid_cells, 1.0*valid_cells/(2*m+1)**2
    # print m, m*eps, round(max(alpha-min_dis, max_dis - alpha)/alpha, 2), alpha, delta, delta2
    return round(max(alpha-min_dis, max_dis - alpha)/alpha, 2)
    # print max(alpha-min_dis, max_dis - alpha)/alpha


# for alpha in range(0,10):
    # for d in range(1, 10):
    #     delta = 1.0/(d**2)
    #     calculate_bounds(delta, alpha)


# base_delta = eps / (1.1*2*math.sqrt(2))
alpha = 1.0
# a, d = 194.619506836, 31.2765393261
# a, d = 129.746337891, 20.8510262174
# a, d = 194.619506836, 31.2765393261
# a, d = 291.929260254 ,46.9148089892
# a, d = 13549.1895544, 239.518095338
# a, d =1.05, 0.0185615530061
# calculate_bounds(d, a)
for a in range(1,1000):
    delta = base_delta*alpha
    eps1 = calculate_bounds(delta, alpha)
    eps2 = calculate_bounds(delta, alpha*2)
    print eps1, eps2
    alpha = alpha * (1+eps)
# calculate_bounds(0.01)
