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


# ===========================================================================================
# ===========================================================================================

cell = generate_layout_cell()
cell.show()

# ===========================================================================================
# ===========================================================================================


"""
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
"""