
# 2-centers in 2-D with radius alpha (offline)
# 2 * sqrt(2) - approx
#init

#grid the plate (width and height = alpha / delta)
# There should be only two centers (Cells) with their neighbors
# A cell and its neighbors consists of (delta*2+1)^2 Cells \
#                       which constructs a (2*alpha+alpha/delta)^2 square

class Cell:
    def __init__(self):
        self.neighbors = list of adjacent cells
        self.position = point

points = list of points
cells = get_cell(points)
center_1 , center_2 = cells[0], cells[1]

for cell in cells:
    if dis(center_1, cell) <= alpha: # max(dis(every 4 points of center_1,every 4 points of cell ))
        center_1.add_neighbor(cell)
    elif dis(center_2,cell) <= delta:
        center_2.add_neighbor(cell)
    else
        center_1, center_2 = find_2centers_from(all cells in center_1_and_2) # Brute force
