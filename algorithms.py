

def secant(f, x0, x1, NMAX, c, s, tol=1.e-6, **kwargs):
    """
    solves for a functions root by secant method
    loops until NMAX iterations reached or tolerance is achieved or divide by zero error occurs
    iterative formula for secant: x_{k+1} = x_k - {f(x_k) * (x_k - x_{k-1})}/{f(x_k) - f(x_{k-1})}
    :param f: the function
    :param x0: initial x val
    :param x1: second initial x val
    :param NMAX: the max num of iterations
    :param c: the constants of the function that will be passed into it
    :param s: the subtype of the function
    :param tol: tolerance for the absolute error of two subsequent approximations
    :param **kwargs: if a kwarg with a name of "sum_of_functions" or "compound_function" is passed in, its value will be used as the functions "c" instead
    :return: the x value of the root found
    """

    for i, name in enumerate(kwargs):
        if name == "compound_function" or name == "sum_of_functions":
            c = [*kwargs.values()][i]

    # update params xk and xk1, then update x0 and x1
    # iterative formula for secant: x_{k+1} = x_k - {f(x_k) * (x_k - x_{k-1})}/{f(x_k) - f(x_{k-1})}
    err = 1.0
    iteration = 0
    while (err > tol) and (iteration < NMAX):
        if f(s, x0, c) == f(s, x1, c):
            return "NaN"
        xk = x0
        xk1 = x1
        err = xk
        xk1 = xk - (f(s, xk, c) * (xk - xk1)) / (f(s, xk, c) - f(s, xk1, c))
        err = abs(xk1 - err)
        x0 = x1
        x1 = xk1
        iteration += 1

        if iteration > NMAX:
            break

    return x1


def bisection(f, x0, x1, NMAX, c, s, tol=1.e-6):
    """
    solves for root of equation using bisection algorithm
    :param f: the function
    :param x0: initial x val
    :param x1: second initial x val
    :param NMAX: max number of iterations
    :param c: the constants
    :param s: the subtype
    :param tol: tolerance before algorithm concludes it has reached a root
    :return: the x value of the root found
    """

    iteration = 1
    condition = True
    while condition and (iteration < NMAX):
        x2 = (x0 + x1) / 2

        if f(s, x0, c) * f(s, x2, c) < 0:
            x1 = x2
        else:
            x0 = x2

        iteration += 1
        condition = abs(f(s, x2, c)) > tol

    return x2


def newton(f, df, x0, tol=1.e-6):
    """
    :param: f = the function f(x)
    :param: df = the derivative of f(x)
    :param: x0 = the initial guess of the solution
    :param: tol = tolerance for the absolute error of two subsequent approximations
    :return: x value of root reached
    """
    err = 1.0
    iteration = 0

    xk = x0
    while err > tol:
        iteration = iteration + 1
        err = xk
        xk = xk - f(xk) / df(xk)
        err = abs(err - xk)
        print(iteration, xk)
    return xk


def main():
    def f(t, x, c):
        y = x**20 - 1
        return y

    tol = 1.e-4
    x1 = -5
    x2 = 4
    MAX_ITER = 100
    rx = secant(f, x1, x2, MAX_ITER, 0, 0, tol)
    print('The aproximate solution is: ', rx)
    print('And the error is: ', f(0, rx, 0))


if __name__ == "__main__":
    main()
