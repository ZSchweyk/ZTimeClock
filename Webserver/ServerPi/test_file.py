from math import *


def get_theta_range(equation, count_accuracy=10):
    theta = 0
    theta_increment = .001
    cartesian_coordinates = []
    count = 0
    while True:
        r = eval(equation)
        x, y = r * cos(theta), r * sin(theta)
        reset_count = True
        for xc, yc in cartesian_coordinates:
            if abs(xc - x) <= .001 and abs(yc-y) <= .001:
                print((x, y), "already exists")
                count += 1
                reset_count = False
                break
        if reset_count:
            count = 0

        if count == count_accuracy:
            return theta

        cartesian_coordinates.append((x, y))
        theta += theta_increment



print(get_theta_range("10 * sin(5 * theta)", count_accuracy=3))



