from math import *


def is_equation_valid(equation):
    builtin_restrictions = {
        "min": min,
        "max": max,
    }
    other_restrictions = {
        "sqrt": sqrt,
        "sin": sin,
        "cos": cos,
    }
    theta = 0
    other_restrictions["theta"] = theta

    try:
        eval(equation, {"__builtins__": builtin_restrictions}, other_restrictions)
    except Exception as exception:
        return False
    return True












