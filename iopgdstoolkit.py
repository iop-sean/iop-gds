from math import pi
import numpy as np
# ======================================================================
from shapely.geometry import Polygon
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.port import Port
from gdshelpers.parts.text import Text


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return rho, phi


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y


def port_shape(radii, port=Port((0, 0), 0, 1), coord=(0, 0), sides=4, radial_type='outer', rotate=0*pi):
    origin = port.origin
    angle = 2*pi/sides
    theta = pi/sides + rotate
    rho = []

    if np.size(radii) == 1:
        radii = [radii]

    q, r = divmod(sides, np.size(radii))
    radii = q * radii + radii[:r]

    if radial_type == 'inner':
        rho = radii
    elif radial_type == 'outer':
        # rho = np.sqrt(np.multiply(np.square(radii), 2))
        rho = np.divide(radii, np.cos(pi/sides))
    points = np.add(pol2cart(rho[0], theta), coord+origin)

    for num in range(1, sides):
        theta += angle
        temp = np.add(pol2cart(rho[num], theta), coord+origin)
        points = np.append(points, temp)

    points = np.reshape(points, (-1, 2))
    shape = Polygon(points)
    shape_port = Port((coord+origin), port.angle, port.width)

    return shape, shape_port


def grid_marker(size, port=Port((0, 0), 0, 1), coord=(0, 0), num_grid=10, space_grad=(1.5, 1.2),
                line_width=2, theta=(0*pi, np.pi/2)):
    origin = port.origin
    spacing = np.linspace(0, size, num_grid)

    spacing1 = spacing**space_grad[0]
    spacing1 = spacing1/(np.max(spacing1)/size)
    spacing1 = spacing1 - (size/2) + coord[1] + origin[1]

    spacing2 = spacing**space_grad[1]
    spacing2 = spacing2/(np.max(spacing2)/size)
    spacing2 = spacing2 - (size/2) + coord[0] + origin[0]

    grid = []
    for num in range(0, np.size(spacing1)):
        temp_port = Port((coord[0] + origin[0] - (size/2), spacing1[num]), angle=theta[0], width=line_width)
        wg_1 = Waveguide.make_at_port(temp_port)
        wg_1.add_straight_segment(size)
        wg_1 = wg_1.get_shapely_object()
        if num == 0:
            grid = wg_1
        else:
            grid = grid.union(wg_1)

    for num in range(0, np.size(spacing2)):
        temp_port = Port((spacing2[num], coord[1] + origin[1] - (size / 2)), angle=theta[1], width=line_width)
        wg_1 = Waveguide.make_at_port(temp_port)
        wg_1.add_straight_segment(size)
        wg_1 = wg_1.get_shapely_object()
        grid = grid.union(wg_1)

    return grid, coord


def alignment_overlay(shape, radii=60, sides=4, buffer=-1, coord=(0, 0), rotate=0, port=Port((0, 0), 0, 1)):
    al_overlay, al_overlay_port = port_shape(radii, radial_type='outer', coord=coord, port=port, sides=sides, rotate=rotate)
    al_overlay = al_overlay.difference(shape)
    al_overlay = al_overlay.buffer(buffer)
    return al_overlay


def layout_marker(shape_or_cell_or_port, offset=(120, 120), size=100):
    port_class = type(Port((0, 0), 0, 1))
    if isinstance(shape_or_cell_or_port, port_class):
        area = shape_or_cell_or_port.origin
        cell_corners = [
            [area[0] - offset[0], area[1] - offset[1]],
            [area[0] - offset[0], area[1] + offset[1]],
            [area[0] + offset[0], area[1] + offset[1]],
            [area[0] + offset[0], area[1] - offset[1]]
        ]
    else:
        area = shape_or_cell_or_port.bounds
        cell_corners = [
            [area[0] - offset[0], area[1] - offset[1]],
            [area[0] - offset[0], area[3] + offset[1]],
            [area[2] + offset[0], area[3] + offset[1]],
            [area[2] + offset[0], area[1] - offset[1]]
        ]

    temp, temp_position = grid_marker(size, coord=cell_corners[0])
    temp_overlay = alignment_overlay(temp, coord=cell_corners[0])
    marker = temp
    marker_list = [temp_position]
    al_overlay = temp_overlay

    for mm in range(1, np.size(cell_corners, 0)):

        temp, temp_position = grid_marker(size, coord=cell_corners[mm])
        temp_overlay = alignment_overlay(temp, coord=cell_corners[mm])

        marker = marker.union(temp)
        marker_list.append(temp_position)
        al_overlay = al_overlay.union(temp_overlay)

    marker_list = np.reshape(marker_list, (-1, 2))
    return marker, marker_list, al_overlay


def distance_from_port(coordinate_list, port=Port((0, 0), 0, 1), offset=(0, 0)):
    origin = port.origin
    coordinate_list = np.reshape(coordinate_list, (-1, 2))

    port_distances = coordinate_list[0] - origin - offset
    for num in range(1, len(coordinate_list)):
        port_distances = np.append(port_distances, coordinate_list[num] - origin - offset)

    port_distances = np.reshape(port_distances, (-1, 2))
    return port_distances


def label_local_positions(global_position, local_position, offset=(0, -70), size=10):
    if len(global_position) != len(local_position):
        print('global_position =', global_position)
        print('local_position =', local_position)
        raise ValueError('lengths of global_position and local_position do not match \n')
    else:
        if np.size(local_position) == 2:
            temp_label = Text((np.add(global_position, offset)), size, 'L ' + str(local_position),
                              alignment='center-top')
            temp_label = temp_label.get_shapely_object()
            local_labels = temp_label
        else:
            temp_label = Text((np.add(global_position[0], offset)), size, 'L ' + str(local_position[0]),
                              alignment='center-top')
            temp_label = temp_label.get_shapely_object()
            local_labels = temp_label
            for num in range(1, len(local_position)):
                temp_label = Text((np.add(global_position[num], offset)), size, 'L ' + str(local_position[num]),
                                  alignment='center-top')
                temp_label = temp_label.get_shapely_object()
                local_labels = local_labels.union(temp_label)

    return local_labels


def label_global_positions(global_position, offset=(0, -90), size=10):
    if np.size(global_position) == 2:
        temp_label = Text((np.add(global_position, offset)), size, 'G ' + str(global_position),
                          alignment='center-top')
        temp_label = temp_label.get_shapely_object()
        global_labels = temp_label
    else:
        temp_label = Text((np.add(global_position[0], offset)), size, 'G ' + str(global_position[0]),
                          alignment='center-top')
        temp_label = temp_label.get_shapely_object()
        global_labels = temp_label
        for num in range(1, len(global_position)):
            temp_label = Text((np.add(global_position[num], offset)), size, 'G ' + str(global_position[num]),
                              alignment='center-top')
            temp_label = temp_label.get_shapely_object()
            global_labels = global_labels.union(temp_label)

    return global_labels
