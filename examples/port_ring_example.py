import iopgdstoolkit as iop
from gdshelpers.parts.port import Port
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.waveguide import Waveguide

# example 1
# create a waveguide and place a ring either side of the second port that can be used as a platform to print onto.
# place a ring with a section cut out so that the platform can get closer at the third port

first_port = Port((0, 0), 0, 1)

guide = Waveguide.make_at_port(first_port)
guide.add_straight_segment(50)

second_port = guide.current_port
guide.add_straight_segment(50)

third_port = guide.current_port
guide.add_straight_segment(50)

# ===============================

ring1 = iop.port_ring(15, 2, second_port, (0, 16))
# parameters allocated implicitly in order

ring2 = iop.port_ring(port=second_port, inner_radius=2, offset=(0, -16), outer_radius=15)
# parameters allocated explicitly at random

ring3, ring3_position = iop.port_ring(15, 2, third_port, (0, 13))
# output is separated at initialisation

cutout = guide.get_shapely_object().buffer(2)
ring3 = ring3.difference(cutout)

cell = Cell('port_shape_cartesian_example')
cell.add_to_layer(1, guide, ring1[0])  # red shapes
cell.add_to_layer(2, ring2[0])  # green shapes
cell.add_to_layer(3, ring3)  # blue shapes

cell.show()
