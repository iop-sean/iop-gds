import iopgdstoolkit as iop
from gdshelpers.geometry.chip import Cell

# example 1
# create a shape, and surround it with labelled grid markers with minimal effort
# create a second shape, and surround it with labelled matching shape markers with minimal effort

shape1, shape1_loc = iop.port_shape_polar(100)
markers1, markers1_loc, markers1_overlay = iop.layout_marker(shape1)
markers1_label = iop.label_global_positions(markers1_loc)

shape2, shape2_loc = iop.port_shape_polar((20, 100), offset=(800, 0), sides=6)
markers2, markers2_loc, markers2_overlay = iop.layout_marker(shape2, size=(20, 80), radii=(10, 60), sides=6)
# ^ size refers to the overlay dimensions, radii to the port shape dimensions, both are handled by iop.port_shape_polar
markers2_label = iop.label_global_positions(markers2_loc)

cell = Cell('layout_marker_example')
cell.add_to_layer(1, shape1, shape2)
cell.add_to_layer(2, markers1, markers1_label, markers2, markers2_label)
cell.add_to_layer(3, markers1_overlay, markers2_overlay)

cell.show()
