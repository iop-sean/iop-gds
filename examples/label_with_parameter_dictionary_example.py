import iopgdstoolkit as iop
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.port import Port
from gdshelpers.geometry.chip import Cell

# create a function that generates waveguides based off a parameter dictionary,
# then label group of guides using iop.label_with_parameter_dictionary


def generate_bunch_of_guides(number_of_lines, line_widths, length):
    guides = Cell('guides')
    line_widths = iop.fill_list(number_of_lines, line_widths, sorting='ascending')

    for y in range(0, number_of_lines):
        guide = Waveguide.make_at_port(Port((0, y*5), 0, line_widths[y]))
        guide.add_straight_segment(length)
        guides.add_to_layer(1, guide)
    return guides


parameter_dict = {  # dictionary keys have to be an exact match for bunch_of_guides inputs
    'number_of_lines': 9,
    'line_widths': [2, 3],
    'length': 500
}

bunch_of_guides = generate_bunch_of_guides(**parameter_dict)

label = iop.label_with_parameter_dictionary(parameter_dict, parameters_per_line=1, position=(200, 30))
bunch_of_guides.add_to_layer(2, label)

bunch_of_guides.show()
