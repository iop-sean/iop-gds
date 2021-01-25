import numpy as np
import matplotlib.pyplot as plt
# ======================================================================
from shapely.geometry import Polygon
from gdshelpers.geometry.chip import Cell
from gdshelpers.layout import GridLayout
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.port import Port
from gdshelpers.layout import GridLayout
from gdshelpers.parts.text import Text
import iopgdstoolkit as iop
# ===========================================================================================
# ===========================================================================================


def generate_layout_cell(size=50, line_width=10):
    cell = Cell('templateMembraneAlign, size = {}, line_width = {}'.format(size, line_width))

    # ring, ring_location = iop.port_ring(15, 10, offset=(100, 200))
    corners = [-30, -10, -30, 10, 30, 10, 30, -10]
    shape, shape_port = iop.port_shape_cartesian(corners, rotate=np.pi*0,
                                                 port=Port((-100, 250), 0, 1), offset=(100, 200))



    # ============================================
    cell.add_to_layer(1, shape)

    return cell


# ===========================================================================================
# ===========================================================================================
one_or_layout = 0
if one_or_layout == 0:
    cell = generate_layout_cell()
    cell.show()
else:
    layout = GridLayout(region_layer_type=None, frame_layer=0,
                        vertical_spacing=40, vertical_alignment=1,
                        horizontal_spacing=100, horizontal_alignment=50)

    for ii in range(0, 2):
        layout.begin_new_row()
        for jj in range(0, 2):
            cell = generate_layout_cell()
            layout.add_to_row(cell)

    layout_cell, mapping = layout.generate_layout()

    markers, marker_list, marker_overlay = iop.layout_marker(layout_cell)
    global_label = iop.label_global_positions(marker_list)
    layout_cell.add_to_layer(1, markers, global_label)

    layout_cell.show()
