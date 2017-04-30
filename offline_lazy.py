
# 2-centers in 2-D with radius alpha (offline)
# 2 * sqrt(2) - approx
#init

#grid the plate (width and height = alpha)
#There should be only two centers (Cells) with their neighbors
#A cell and its neighbors consists of 9 Cells which constructs a 3alpha*3alpha square

class Cell:
    def __init__(self):
        self.neighbors = list of adjacent cells
        self.position = point

points = list of points
cells = get_cell(points)
center_1 , center_2 = cells[0], cells[1]

for cell in cells:
    if dis(center_1, cell) <= 1: #cell distance
        center_1.add_neighbor(cell)
    elif dis(center_2,cell) <= 1:
        center_2.add_neighbor(cell)
    else
        center_1, center_2 = find_2centers_from(all cells in center_1_and_2) # Brute force
