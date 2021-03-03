from math import pi
import numpy as np
# ======================================================================
from shapely.geometry import Polygon
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.port import Port
from gdshelpers.parts.text import Text
from gdshelpers.geometry.chip import Cell
from shapely.geometry import Point


def cart2pol(x, y):
    """
    converts cartesian coordinates x and y to polar coordinates rho and phi via numpy functions np.sqrt and np.arctan2.

    :param x: this is the cartesian x coordinate
    :param y: this is the cartesian y coordinate
    :return: list containing rho and phi polar coordinates as [rho, phi]
    """

    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return rho, phi


def pol2cart(rho, phi):
    """
    converts polar coordinates rho and phi to cartesian coordinates x and y via numpy functions np.cos and np.sin.

    :param rho: shortest distance from origin to endpoint on polar axis
    :param phi: angle between the x axis and the line of length rho to the endpoint
    :return: list containing x and y cartesian coordinates as [x, y]
    """
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y


def fill_list(number_of_items, current_list, sorting='cyclic'):
    """
    Utility function, takes an existing 1 dimensional list and repeats it to fit length determined by number_of_items.
    new length doesn't have to be a multiple of original length of list.

    intended use is for parameter sweeps, such that:

    import iopgdstoolkit as iop
    list_dictionary = {
    'number_of_items': 7,
    'current_list': [1, 2, 3],
    'sorting': 'cyclic',
    }
    list = iop.fill_list(**list_dictionary)
    print(list) # [1, 2, 3, 1, 2, 3, 1]

    :param number_of_items: determines the length of the new list
    :param current_list: current list of items to be repeated in new list
    :param sorting: final order of variables after being repeated, choose 'cyclic', 'ascending' or 'descending'
    :return: new list
    """

    size = np.size(current_list)
    if size == 1:
        current_list = [current_list]
    else:
        current_list = list(current_list)

    q, r = divmod(number_of_items, size)

    if sorting == 'cyclic':
        new_list = q * current_list + current_list[:r]
    elif sorting == 'ascending':
        new_list = q * current_list + current_list[:r]
        new_list.sort()
    elif sorting == 'descending':
        new_list = q * current_list + current_list[:r]
        new_list.sort()
    else:
        new_list = q * current_list + current_list[:r]
        print(sorting, 'sorting is not supported, defaulted to cyclic')

    return new_list


def port_shape_polar(radii, port=Port((0, 0), 0, 1), offset=(0, 0), sides=4, radial_type='to_edge', rotate=0 * pi):
    """
    creates a shape defined in polar coordinates around a port location, ideal for creating shapes like hexagons
    or octagons in a location that is a fixed distance away from an imPORTant port location. Supports more complex
    shapes by setting radii to a list of values. radii list uses iop.fill_list functionality
    Shape is created using the shapely library.


    :param radii: single value or list of values, distance away from centre of port + offset
    :param port: the imPORTant port, which you want the shapes centre to be in relation to.
    :param offset: the cartesian distance away from the port origin that you wan the shapes centre to be at.
    :param sides: number of sides the shape has e.g. 6 = hexagon. sides separated by angle = 2*pi/sides
    :param radial_type: choose 'to_corner' or 'to_edge' defines whether the radius is the distance to the corners
    or the middle of the sides
    :param rotate: in radians, overal rotation of the whole shape.
    :return: list containing the shapely geometry and the port associated with it as [shape, shape_port]
    """

    origin = port.origin
    angle = 2*pi/sides
    theta = pi/sides + rotate
    rho = []

    if np.size(radii) == 1:
        radii = [radii]

    q, r = divmod(sides, np.size(radii))
    radii = q * radii + radii[:r]

    if radial_type == 'to_corner':
        rho = radii
    elif radial_type == 'to_edge':
        # rho = np.sqrt(np.multiply(np.square(radii), 2))
        rho = np.divide(radii, np.cos(pi/sides))
    points = np.add(pol2cart(rho[0], theta), offset+origin)

    for num in range(1, sides):
        theta += angle
        temp = np.add(pol2cart(rho[num], theta), offset+origin)
        points = np.append(points, temp)

    points = np.reshape(points, (-1, 2))
    shape = Polygon(points)
    shape_port = Port((offset+origin), port.angle, port.width)

    return shape, shape_port


def port_shape_cartesian(coordinate_list, port=Port((0, 0), 0, 1), offset=(0, 0), rotate=0 * pi):
    """
    another method of created a shapely object with cartesian coordinates in relation to a port's position.
    Note: this function was added for symmetry with port_shape_polar, it is straight forward to create the above using
    just shapely and gdshelpers functions. key feature is the ability to rotate the shape in radians around
    it's centre position.

    :param coordinate_list: list of cartesian coordinates that define the corners of the shapely object.
    :param port: the imPORTant port in which the shape coordinates are based off.
    :param offset: the fixed distance away from the port added to each value in coordinate_list
    :param rotate: in radians, the angle the shape is rotated, centre of rotation is at port.origin + offset
    :return: list containing the shapely geometry and the port associated with it as [shape, shape_port]
    """

    points = np.reshape(coordinate_list, (-1, 2))
    origin = port.origin

    polar_points = points*0.0  # make sure its a list of floats, else shapes get messed up
    port_points = points*0.0

    if rotate != 0 * pi:
        for num in range(0, len(points)):
            polar_points[num, 0], polar_points[num, 1] = cart2pol(points[num, 0], points[num, 1])
            port_points[num, 0], port_points[num, 1] = pol2cart(polar_points[num, 0],
                                                                polar_points[num, 1] + rotate) + origin + offset

    else:
        for num in range(0, len(points)):
            port_points[num] = points[num] + origin + offset

    shape = Polygon(port_points)
    shape_port = Port((offset+origin), port.angle, port.width)

    return shape, shape_port


def port_ring(outer_radius, inner_radius, port=Port((0, 0), 0, 1), offset=(0, 0), radial_type='outer_inner'):
    """
    this is a quick method to make a ring resonator centred around a port location, gdshelpers creates
    ring resonators positioned by the coupling region which is usually more useful. this is for the edge cases where
    that isn't desired. Such as creating a platform for a disk resonator to be printed on.

    :param outer_radius: outer radius of the ring, this minus inner radius determines thickness of line
    :param inner_radius: inner radius of the ring, this subtracted from outer radius determines thickness of line
    :param port: the imPORTant port in which the shape coordinates are based off.
    :param offset: the fixed distance away from the port that the ring is centred around.
    :param radial_type: either 'outer_inner' or 'centre-span', however centre-span is yet to be implemented.
    :return: list including the shapely ring object and a cartesian coordinate list of the ring's centre in
    the form [ring, [x, y]]. future update should change second entry to a port object
    """

    origin = port.origin
    if radial_type == 'outer_inner':
        ring_location = np.add(origin, offset)
        temp = Point(ring_location)
        shell = temp.buffer(outer_radius)
        core = temp.buffer(inner_radius)
        ring = shell.difference(core)
    elif radial_type == 'center-span' or radial_type == 'centre-span':
        print('center-span not yet implemented! defaulted to outer-inner')
        ring_location = np.add(origin, offset)
        temp = Point(ring_location)
        shell = temp.buffer(outer_radius)
        core = temp.buffer(inner_radius)
        ring = shell.difference(core)

    return ring, ring_location


def grid_marker(size, port=Port((0, 0), 0, 1), offset=(0, 0), num_grid=10, space_grad=(1.5, 1.2),
                line_width=2, theta=(0*pi, np.pi/2)):

    """
    Creates a square aperiodic grid marker used for alignment during transfer printing.

    :param size: integer value that determines the length of the grid marker's sides
    :param port: the imPORTant port in which the shape coordinates are based off.
    :param offset: the fixed distance away from the port that the grid is centred around.
    :param num_grid: integer number of horizontal and vertical grid lines
    :param space_grad: a tuple of form (a, b), a and b represent the gradient of the spacing between the grid lines
    :param line_width: thickness of the grid marker lines
    :param theta: leave as default, legacy feature that changes the angle of the grid lines, set as perpendicular.
    :return: returns a list containing the gridmarker shapely object and cartesian offset from the port it is based off
    Note: this behaviour is different from other functions in that is gives a local position rather than a global.
    """

    origin = port.origin
    spacing = np.linspace(0, size, num_grid)

    spacing1 = spacing**space_grad[0]
    spacing1 = spacing1/(np.max(spacing1)/size)
    spacing1 = spacing1 - (size/2) + offset[1] + origin[1]

    spacing2 = spacing**space_grad[1]
    spacing2 = spacing2/(np.max(spacing2)/size)
    spacing2 = spacing2 - (size/2) + offset[0] + origin[0]

    grid = []
    for num in range(0, np.size(spacing1)):
        temp_port = Port((offset[0] + origin[0] - (size / 2), spacing1[num]), angle=theta[0], width=line_width)
        wg_1 = Waveguide.make_at_port(temp_port)
        wg_1.add_straight_segment(size)
        wg_1 = wg_1.get_shapely_object()
        if num == 0:
            grid = wg_1
        else:
            grid = grid.union(wg_1)

    for num in range(0, np.size(spacing2)):
        temp_port = Port((spacing2[num], offset[1] + origin[1] - (size / 2)), angle=theta[1], width=line_width)
        wg_1 = Waveguide.make_at_port(temp_port)
        wg_1.add_straight_segment(size)
        wg_1 = wg_1.get_shapely_object()
        grid = grid.union(wg_1)

    return grid, offset


def alignment_overlay(shape, radii=60, sides=4, port=Port((0, 0), 0, 1), offset=(0, 0), buffer=-1, rotate=0):
    """
    takes a shape and subtracts it from an iop.port_shape_polar object to create an inverse of the image with a buffer.
    this could be useful for coarse alignment during transfer printing or exposure. Such as defining a location for a
    membrane to be printed within

    :param shape: the shape that you are creating a negative of.
    :param radii: the radius of the iop.port_shape_polar you are subtracting from
    :param sides: the number of sides of the iop.port_shape_polar you are subtracting from
    :param port: the imPORTant port in which the shape coordinates are based off.
    :param offset: the fixed distance away from the port that the overlay is centred around.
    :param buffer: the spacing between the shape and overlay sides
    :param rotate: the rotation of the iop.port_shape_polar
    :return: shapely object, which is a negative of the input shape.
    """
    # print('radii = ', radii)
    al_overlay, al_overlay_port = port_shape_polar(radii=radii, radial_type='to_edge', offset=offset,
                                                   port=port, sides=sides, rotate=rotate)
    al_overlay = al_overlay.difference(shape)
    al_overlay = al_overlay.buffer(buffer)
    return al_overlay


def layout_marker(shape_cell_port_or_bounds, offset=(120, 120), size=100, radii=None, sides=4):
    """
    places alignment markers a fixed distance away from the corners of a shape, cell, port or bounds,
    this is a quick way to get 4 markers around an object that is of interest and are related to each other in
    separation. default behaviour is to produce iop.grid_markers but iop.port_shape_polar can substituted by specifying
    values for radii.

    :param shape_cell_port_or_bounds: can be a shapely object, a device cell, a port or just cartesian bounds
    :param offset: a tuple in form (a, b) that represents the magnitude of the distance away from the corners of the
    target area. The sign of the values are modified appropriately depending on which corner of four they represent.
    :param size: the length of iop.grid_marker's sides, ignored if radii specified
    :param radii: radius of iop.port_shape_polar from centre to middle of side, specifying causes size to be ignored.
    :param sides: integer number of sides the iop.port_shape_polar has, default of 4
    :return: a list containing the 4 shapely markers after geometric union, their local position in respect to their
    respective corner and an iop.alignment_overlay of the markers.
    In the form of [marker, marker_local_position, marker_overlay]
    """

    if hasattr(shape_cell_port_or_bounds, 'origin'):
        area = shape_cell_port_or_bounds.origin
        cell_corners = [
            [area[0] - offset[0], area[1] - offset[1]],
            [area[0] - offset[0], area[1] + offset[1]],
            [area[0] + offset[0], area[1] + offset[1]],
            [area[0] + offset[0], area[1] - offset[1]]
        ]
    elif hasattr(shape_cell_port_or_bounds, 'bounds'):
        area = shape_cell_port_or_bounds.bounds
        cell_corners = [
            [area[0] - offset[0], area[1] - offset[1]],
            [area[0] - offset[0], area[3] + offset[1]],
            [area[2] + offset[0], area[3] + offset[1]],
            [area[2] + offset[0], area[1] - offset[1]]
        ]
    else:
        area = shape_cell_port_or_bounds
        cell_corners = [
            [area[0] - offset[0], area[1] - offset[1]],
            [area[0] - offset[0], area[3] + offset[1]],
            [area[2] + offset[0], area[3] + offset[1]],
            [area[2] + offset[0], area[1] - offset[1]]
        ]

    if type(radii) == tuple or type(radii) == list:
        # print(radii)
        temp, temp_port = port_shape_polar(radii, offset=cell_corners[0], sides=sides)
        temp_position = temp_port.origin
        temp_overlay = alignment_overlay(temp, radii=size, sides=sides, offset=cell_corners[0])
    else:
        temp, temp_position = grid_marker(size, offset=cell_corners[0])
        temp_overlay = alignment_overlay(temp, offset=cell_corners[0])


    marker = temp
    marker_list = [temp_position]
    al_overlay = temp_overlay

    for mm in range(1, np.size(cell_corners, 0)):

        if type(radii) == tuple or type(radii) == list:
            temp, temp_port = port_shape_polar(radii, offset=cell_corners[mm], sides=sides)
            temp_position = temp_port.origin
            temp_overlay = alignment_overlay(temp, radii=size, sides=sides, offset=cell_corners[mm])
        else:
            temp, temp_position = grid_marker(size, offset=cell_corners[mm])
            temp_overlay = alignment_overlay(temp, offset=cell_corners[mm])



        marker = marker.union(temp)
        marker_list.append(temp_position)
        al_overlay = al_overlay.union(temp_overlay)

    marker_list = np.reshape(marker_list, (-1, 2))
    return marker, marker_list, al_overlay


def distance_from_port(coordinate_list, port=Port((0, 0), 0, 1), offset=(0, 0)):
    """
    A utility function that takes a list of coordinates (x, y) and finds there distance
    from an imPORTant port + (x, y) offset in your design.
    The intended use is to know the distance from an alignment marker to key area in the design, for example
    a ring resonator coupling region.


    :param coordinate_list: this expects a list of coordinates in the form (x, y, x, y, x, y) like that given from
    iop.layout_marker as marker_list.
    :param port: the imPORTant port that you would like to know the distance from.
    :param offset: adds an offset to the port location, as the key area may actually be a
    fixed distance away from the port.
    :return: a list of coordinates that represent distance of coordinate list to a particular port.
    """
    origin = port.origin
    coordinate_list = np.reshape(coordinate_list, (-1, 2))

    port_distances = coordinate_list[0] - origin - offset
    for num in range(1, len(coordinate_list)):
        port_distances = np.append(port_distances, coordinate_list[num] - origin - offset)

    if len(port_distances) > 2:
        port_distances = np.reshape(port_distances, (-1, 2))

    return port_distances


def label_local_positions(global_position, local_position, offset=(0, -70), size=10):
    """
    creates a text label under a marker that denotes the distance away from a particular port location (local position).
    Supports lists for global and local positions, like that given in iop.layout_marker and iop.distance_from_port.
    list of distances should be of same dimensions. labeled with 'l' for local

    :param global_position: coordinate or coordinate list of positions relative to the entire design.
    :param local_position: coordinate or coordinate list of positions relative to the particular port.
    :param offset: the text label positions is based off the global positions, an offset can be added
    for better visual alignment
    :param size: the size of the text
    :return: shapely object that is the geometric union of all of the labels
    """
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
    """
    creates a text label under a marker that denotes its position based off the whole chip design (global position).
    Supports lists for global and local positions, like that given in iop.layout_marker and iop.distance_from_port.
    list of distances should be of same dimensions. labelled with 'g' for global

    :param global_position: coordinate or coordinate list of positions relative to the entire design.
    :param offset: the text label positions is based off the global positions, an offset can be added
    for better visual alignment
    :param size: the size of the text
    :return: shapely object that is the geometric union of all of the labels
    """
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


def label_with_parameter_dictionary(dictionary, parameters_per_line=2, position=(0, 0), text_height=10):
    """
    When creating new designs that are to be iterated over it can be handy to utilise python dictionaries,
    create a custom function for your design and use the '**dict' unpacking method to pass parameters into it.
    this function allows you create a text object, that contains a text label of all the parameters in the dictionary.
    this can then be added to the gdshelpers grid layout for easy labeling.

    :param dictionary: the dictionary you would pass through to your design function.
    :param parameters_per_line: integer, how many parameters do you want on each line of text.
    large dictionaries may look better with a value > 2.
    :param position: the absolute position of the text box, relative positions can be defines in gdshelpers add_to_row
    :param text_height: the height of the font used in the labels
    :return: the formatted text object ready to be added to a cell.
    """
    ii = 0
    string = [''] * len(dictionary)
    for key, value in dictionary.items():
        if (ii + 1) % parameters_per_line == 0:
            string[ii] = f'{key} = {value},  \n'
        else:
            string[ii] = f'{key} = {value}, '
        ii += 1
    label = ''.join(string)
    cell_label = Text(position, text_height, label, 'left-bottom')
    return cell_label


def _cell_alignment_points(cell_to_copy):
    """
    incomplete function, recommended to not use as not operating as intended and subject to abrupt changes.
    Attempt at a brute force technique to take all the port locations stored within an gridlayout nested data structure.
    potentially useful for advanced transfer printing protocols where the machine can know the locations of every
    aspect of your design after alignment to markers. searches for specific objects in structure and pulls port
    locations that way, would require each object type to be hard coded in.

    :param cell_to_copy: the cell you would like to extract all the port locations from
    :return: a nx2 list of coordinate positions that relate to every port in the design.
    """
    cell = cell_to_copy
    layer_nums = list(cell.__dict__['layer_dict'].keys())

    for layer in layer_nums:
        shape_length = len(cell.__dict__['layer_dict'][layer])

        for shape in range(0, shape_length):
            print(type(cell.__dict__['layer_dict'][layer][shape]))
            if isinstance(cell.__dict__['layer_dict'][layer][shape], Polygon):
                centre = cell.__dict__['layer_dict'][layer][shape].centroid
                # print('Centroids = ', [centre.x, centre.y])
                if 'key_positions' in locals():
                    key_positions = np.append(key_positions, [centre.x, centre.y])
                else:
                    key_positions = centre.x, centre.y

            elif isinstance(cell.__dict__['layer_dict'][layer][shape], Waveguide):
                helpers_ports = cell.__dict__['layer_dict'][layer][shape].current_port.origin
                helpers_object = cell.__dict__['layer_dict'][layer][shape].get_segments()
                # helpers_ports = helpers_object[0][0].origin
                for port in range(0, len(helpers_object)):
                    helpers_ports = np.append(helpers_ports, helpers_object[port][0].origin)
                helpers_ports = np.reshape(helpers_ports, (-1, 2))
                if 'key_positions' in locals():
                    key_positions = np.append(key_positions, helpers_ports)
                else:
                    key_positions = key_positions
                # print('Ports = ', helpers_ports)

    key_positions = np.reshape(key_positions, (-1, 2))
    print(key_positions)

    return key_positions


def _recursion(cell_dict, key_positions=[]):
    """
    incomplete function, recommended to not use as not operating as intended and subject to abrupt changes.
    Attempt at an elegant technique to take all the port locations stored within an gridlayout nested data structure.
    potentially useful for advanced transfer printing protocols where the machine can know the locations of every
    aspect of your design after alignment to markers. designed as a recursive function that looks 1 layer deep into a
    gridlayout data structure and contains anything that can be deemed as a port. I then feeds entries back into itself
    to check another layer down in the data structure.

    :param cell_dict:
    :param key_positions:
    :return:
    """

    if type(cell_dict) == dict:
        for key, value in cell_dict.items():
            _recursion(value, key_positions=key_positions)

    elif type(cell_dict) == Cell:
        _recursion(cell_dict.__dict__, key_positions=key_positions)

    elif type(cell_dict) == list:

        for entry in cell_dict:
            if type(entry) == dict:
                _recursion(entry, key_positions=key_positions)

            elif hasattr(entry, 'current_port'):
                # print('has attribute: current_port')
                origin = list(entry.current_port.origin)
                # print(sub_value.current_port.origin)
                key_positions += origin

            elif hasattr(entry, 'geoms'):  # deals with MultiPolygon before Polygon
                # print('has attribute: geoms')
                shape_list = list(entry.geoms)
                centre = []
                for shape in shape_list:
                    centre = shape.centroid
                    centre = list([centre.x, centre.y])
                    key_positions += centre

            elif hasattr(entry, 'centroid'):  # deals with Polygon after MultiPolygon
                # print('has attribute: centroid')
                centre = entry.centroid
                centre = list([centre.x, centre.y])
                # print(centre)
                key_positions += centre

    key_positions = np.reshape(key_positions, (-1, 2))
    return key_positions
