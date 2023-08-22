import math
import sys


def polynomial(t, x, c):
    """
    Defines a polynomial with degree t taking in a value x and constants c
    :param t: the subtype. in the case of a polynomial, this is just the degree
    :param x: the x value inputted
    :param c: c is an array of constants before the x, e.g. for 2x^3 + 4x^2 + 3 it would be [2, 4, 0, 3]
    :return: the y value
    """
    if len(c) < t + 1:
        for i in range(0, t - len(c) + 1):
            c.append(0)

    try:
        y = 0
        for i in range(0, t + 1):
            y += c[i] * (x ** (t - i))

    except Exception as e:
        print(f"Error when calculating polynomial: {e}")
        y = sys.float_info.max

    return y


def trigonometric(t, x, c):
    """
    y = c[0] * math.sin(c[1] * x + c[2]) + c[3]
    fills c with 0's if its length < 4
    :param t: the type of trig function. must be a string that corresponds to a trig function in the math library , e.g. "sin" or "atanh"
    :param x: x value
    :param c: constants
    :return: y value
    """
    if len(c) < 4:
        for i in range(0, 4 - len(c)):
            c.append(0)

    try:
        y = c[0] * getattr(math, t)(c[1] * x + c[2]) + c[3]
    except Exception as e:
        print(f"Input of {x} into {t} causes an error: {e}")
        y = sys.float_info.max

    return y


def exponential(t, x, c):
    """
    y = c[0] * (c[1] ** (x + c[2])) + c[3]
    makes sure exponential doesn't have an asymptote ax y=0
    :param t: reserved for any potential subtypes
    :param x: x value
    :param c: constants
    :return: y value
    """

    if c[3] == 0:
        print("Exponential has an asymptote at y=0")
        return

    if len(c) < 4:
        for i in range(0, 4 - len(c)):
            c.append(0)

    try:
        y = c[0] * (c[1] ** (x + c[2])) + c[3]

    except Exception as e:
        print(f"Error when calculating exponential: {e}")
        y = sys.float_info.max

    return y


def logarithm(t, x, c):
    """
    y = c[0] * math.log(c[1] * x, c[2]) + c[3] (base of log is c[2])
    :param t: reserved for any potential subtypes
    :param x: the x value inputted
    :param c: an array of constants
    :return: the y value
    """
    if len(c) < 4:
        for i in range(0, 4 - len(c)):
            c.append(0)

    try:
        y = c[0] * math.log(c[1] * x, c[2]) + c[3]

    except Exception as e:
        print(f"Error calculating logarithm: {e}")
        y = sys.float_info.max

    return y


def sum_of_functions(x, **kwargs):
    """
    function composed of multiple types of functions added together
    e.g. 2sin(x+4) + x^3 + 2x + 3^(x+7) which is trig + poly + expo
    NOT a composite function f[g(x)] like sin(x^2+2) or sin(1/x)
    :param x: x value
    :param kwargs: key word args for the type of function and the constants e.g: trigonometric=["sin", 2, 1, 4, 0], polynomial=[2, 3, 0, 0]. The first element will be the subtype, the rest will be the constants
    :return: adds y values of functions and returns it
    """
    f_sum = 0
    for i, name in enumerate(kwargs):

        # get function from name as string, call it and add function result to compound
        c = [*kwargs.values()][i]
        f_sum += globals()[name](c[0], x, c[1::])

    return f_sum


# TODO: expand functionality to any number of nested compound functions
def compound_function(x, **kwargs):
    """
    A compound function, takes in two functions and computes the compound of the second in the first
    e.g. sin(x) and 1/x will give sin(1/x), 1/x and sin(x) will give 1/sin(x)
    :param x: the x value to evaluate at
    :param kwargs: the two functions and their information, e.g. trigonometric=["sin", 1, 1, 0, 0], polynomial=[2, 1, 0, 0] will produce sin(x^2)
    :return: the y value of the composite function
    """
    compound = 0
    try:
        c1 = [*kwargs.values()][0]
        c2 = [*kwargs.values()][1]

        inner = globals()[[*kwargs.keys()][1]](c2[0], x, c2[1::])
        compound = globals()[[*kwargs.keys()][0]](c1[0], inner, c1[1::])
        print(inner, compound)

    except Exception as e:
        print(e)

    return compound


def tests():
    """
    Preforms basic checks to ensure the functions are returning correct values
    :return: None
    """
    types = ["polynomial", "trigonometric", "exponential"]
    inputs = {"polynomial": [[2, 1, [2, 3, -2]], [4, -2, [1, 0, 3, 0, 5]], [3, 0, [1, 2, 3, 4]]],
             "trigonometric": [["sin", 0, [1, 1, 0, 1]], ["cos", math.pi, [1, 1, 0, 0]]],
             "exponential": [[0, 2, [1, 2, 0, 4]], [0, -2, [2, 3, 1, -4]]]}

    expected = {"polynomial": [3, 33, 4],
                "trigonometric": [1, -1],
                "exponential": [8, -10/3]}

    print("(+) Testing functions")

    for t_type in types:
        print(f"\n(+) {t_type}:")

        for n, i in enumerate(inputs[t_type]):
            o = globals()[t_type](i[0], i[1], i[2])
            if o != expected[t_type][n]:
                print(f"(-) Failed with input {i}, expected {expected[t_type][n]} got {o}")
            else:
                print(f"(+) Passed input {i}")


if __name__ == "__main__":
    tests()
