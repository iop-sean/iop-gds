import iopgdstoolkit as iop
from gdshelpers.geometry.chip import Cell

# example 1
# generate several grid markers with different parameters based off a iop.port_shape_polar object

# create an iop.port_shape_polar
shape, shape_port = iop.port_shape_polar(25, offset=(-50, 0))

# bottom left
grid1, global_location1 = iop.grid_marker(100, offset=(50, 50))
# ^ creates a default grid_marker of size 100


# top left
grid2, global_location2 = iop.grid_marker(100, offset=(50, 250), num_grid=15)
# ^ creates a grid marker with 15 lines instead of 10

global_label2 = iop.label_global_positions(global_location2, offset=(0, -70))
# ^ creates a label of the global position of the marker


# top right
grid3, global_location3 = iop.grid_marker(100, offset=(250, 250), space_grad=(2, 3))
# ^ makes the gradient of the spacing more severe

global_label3 = iop.label_global_positions(global_location3, offset=(0, -90))
local_location3 = iop.distance_from_port(global_location3, port=shape_port)
local_label3 = iop.label_local_positions(global_location3, local_location3, offset=(0, -70))
# ^ adds a label of the local position (distance away from port_shape)

# bottom right
grid4, global_location4 = iop.grid_marker(100, offset=(250, 50), line_width=5)
# ^ makes the lines much thicker

global_label4 = iop.label_global_positions(global_location4)
local_location4 = iop.distance_from_port(global_location4, port=shape_port)
local_label4 = iop.label_local_positions(global_location4, local_location3)
# ^ uses default positions for marker labels that work well with marker size 100


cell = Cell('port_shape_polar_example')
cell.add_to_layer(1, shape)  # red shapes
cell.add_to_layer(2, grid1, grid2, grid3, grid4)  # green shapes
cell.add_to_layer(3, global_label2, global_label3, global_label4)  # blue shapes
cell.add_to_layer(4, local_label3, local_label4)  # turquoise shapes?

cell.show()
