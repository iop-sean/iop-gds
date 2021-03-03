import iopgdstoolkit as iop
import numpy as np
from gdshelpers.parts.port import Port
from gdshelpers.geometry.chip import Cell

# example 1
# create a 2 layer cell, that demonstrates different functionality of iop.port_shape_polar

# bottom left
shape1 = iop.port_shape_polar(20)
# ^square with sides of length = 40, centre to side distance = 20
shape2 = iop.port_shape_polar(20, radial_type='to_corner')
# ^square with centre to corner distance = 20

# top left
shape3 = iop.port_shape_polar(20, offset=(0, 60), sides=5, rotate=np.pi/5)
# ^ create pentagon rotated 36 degrees.
shape4 = iop.port_shape_polar(20, offset=(0, 60), sides=5, radial_type="to_corner")
# ^ create pentagon using to_corner type to show that it corners touch shape 3's sides.

# top right
shape5 = iop.port_shape_polar((20, 15), offset=(60, 60))
# ^ specify multiple radii to create more complex shapes
shape6 = iop.port_shape_polar((20, 5), offset=(60, 60), sides=6)
# ^ specify multiple radii to create more complex shapes, regardless of sides

# bottom right
shape7 = iop.port_shape_polar(20, port=Port((60, 0), 0, 1), offset=(0, 0))
# ^ define shape position based off port
shape8 = iop.port_shape_polar(10, port=Port((30, 0), 0, 1), offset=(30, 0))
# ^ define shape position based off port and offset

cell = Cell('port_shape_polar_example')
cell.add_to_layer(1, shape1[0], shape3[0], shape5[0], shape7[0])  # red shapes
cell.add_to_layer(2, shape2[0], shape4[0], shape6[0], shape8[0])  # green shapes

cell.show()
