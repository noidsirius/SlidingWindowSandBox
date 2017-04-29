import math
import sys

from utils import *


target_eps = 0.01
alpha = 1.0
eps = target_eps
print "alpha_cells,eps"
for a in range(1,1000):
    point_util = PointUtil(eps, alpha, a)
    new_eps = point_util.calculate_real_eps()
    print a, ',', new_eps
    sys.stdout.flush()
    # eps += 0.0001
    # print eps, new_eps, abs(new_eps - target_eps) < MIN_EPS , new_eps - target_eps
    # if new_eps < target_eps:
    #     if target_eps - new_eps > MIN_EPS:
    #         eps += 0.01
    #     else:
    #         break
    # elif new_eps - target_eps > MIN_EPS:
    #     eps = new_eps
    # else:
    #     break
    # alpha = alpha * (1+eps)
