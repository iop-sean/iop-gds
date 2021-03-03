import iopgdstoolkit as iop

# example 1
# create a create a list of length 7, with 3 unique variables
# print list in terminal

unique_variables = [1, 2, 3]
new_list = iop.fill_list(7, unique_variables)

print(
    "Example 1:"
    + "\nnew_list = " + str(new_list)
)

# example 2
# Take a list from a parameter dictionary, and replace with list of duplicated entries and sort in ascending order.
# print dictionary in terminal

parameter_dict = {
    "number_of_guides": 9,
    "line_widths": [2, 2.2, 2.4],
    "guide_length": 1000,
}

parameter_dict["line_widths"] = iop.fill_list(parameter_dict["number_of_guides"], 
                                              parameter_dict["line_widths"],
                                              sorting='ascending')

print(
    "Example 2:"
    + "\nparameter_dict = " + str(parameter_dict)
)
