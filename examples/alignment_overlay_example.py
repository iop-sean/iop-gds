import iopgdstoolkit as iop
from gdshelpers.geometry.chip import Cell

# example 1
# create a grid marker and create an alignment overlay for use with coarse alignment processes.

grid1, location1 = iop.grid_marker(100)
overlay1 = iop.alignment_overlay(grid1, offset=location1, radii=60)
# ^ overlay works by creating a shape, then performing a geometric subtraction then applies a negative buffer

grid2, location2 = iop.grid_marker(100, offset=(150, 0))
overlay2 = iop.alignment_overlay(grid2, offset=location2, radii=(60, 80), sides=6, buffer=-2)
# ^ shape creation works by iop.port_shape_polar, so some variables can be passed through to modify it.

cell = Cell('alignment_overlay_example')
cell.add_to_layer(1, grid1, grid2)
cell.add_to_layer(2, overlay1, overlay2)
cell.show()

