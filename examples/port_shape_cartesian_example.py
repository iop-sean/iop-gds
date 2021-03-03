import iopgdstoolkit as iop
import numpy as np
from gdshelpers.parts.port import Port
from gdshelpers.geometry.chip import Cell

# Note, port_shape_cartesian operates much the same way as Shapely Polygon, but supports positioning based off ports
# and also allows for rotation.

# example 1
# create a 1 layer cell, that demonstrates different functionality of iop.port_shape_cartesian

corners = [(20, 10), (20, -10), (-20, -10), (-20, 10)]  # rectangle centred around (0, 0)

# bottom left
shape1 = iop.port_shape_cartesian(corners)
# ^ rectangle at (0, 0)

# top left
shape2 = iop.port_shape_cartesian(corners, offset=(0, 60))
# ^ rectangle at (0, 60) based off offset

# top right
shape3 = iop.port_shape_cartesian(corners, port=Port((60, 0), 0, 1), offset=(0, 60))
# ^ rectangle at (60, 60) based off port position and offset

# bottom right
shape4 = iop.port_shape_cartesian(corners, offset=(60, 0), rotate=np.pi/5)
# ^ rectangle at (60, 0) and rotated 36 degrees


cell = Cell('port_shape_cartesian_example')
cell.add_to_layer(1, shape1[0], shape2[0], shape3[0], shape4[0])  # red shapes

cell.show()
