"""
Author: Sean Bommer
Date: 03/03/2021
Example included in iopgdstoolkit demonstrating how to use the functions cart2pol and pol2cart
"""
import numpy as np
import iopgdstoolkit as iop

# example 1
# create a point at location (1, 1) on coordinate grid,
# find the polar coordinate equivalent and print it in terminal

point_cart = (1, 1)
point_polar = iop.cart2pol(point_cart[0], point_cart[1])
print(
    "Example 1:"
    + "\nthe polar coordinates are: rho = " + str(point_polar[0]) + "(AU) phi = " + str(point_polar[1])
    + "(radians) \nin the form " + str(point_polar)
)

# example 2
# create a point at location (1.414, pi/4) on polar coordinate grid,
# find the polar coordinate equivalent and print it in terminal

point_polar = (1.414, np.pi/4)
point_cart = iop.pol2cart(point_polar[0], point_polar[1])
print(
    "Example 2:"
    + "\nthe cartesian coordinates are: x = " + str(point_cart[0]) + "(AU) y = " + str(point_cart[1])
    + "(AU) \nin the form " + str(point_cart)
)
