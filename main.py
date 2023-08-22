import gc
import os
import threading
# import time
import textwrap
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import functions
import algorithms

mpl.use("TkAgg")


# constants
MAX_INPUT_COUNT = 1000000
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
FUNCTION_OPTION_TEXT = ["Polynomial", "Trigonometric", "Exponential"]
TRIG_TYPES = ["sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "asinh", "acosh", "atanh"]


def plot(cancel):
    """
    Function that will calculate and plot the graph defined by the user inputs using matplotlib
    and display it in the tkinter window
    :param cancel: A tk.BooleanVar. when True, the calculations continue run. If it becomes false, the calculations are stopped and the function returns
    :return: None
    """

    # arrays to store the inputs
    inputs = []
    roots_secant = []  # stores the root found from the inputs of same index, will be a 2d array
    roots_bisection = []
    constants = []

    # get info user has put into the entries
    try:
        # get algorithm options
        l_bound = float(min_input_sv.get())
        u_bound = float(max_input_sv.get())
        max_iter = float(max_iter_sv.get())
        tol = float(tolerance_sv.get())
        step = float(step_sv.get())
        fig_width = int(fig_width_sv.get())
        abs_max_root = float(max_root_sv.get())

        # get function constants
        for entry in function_constants:
            constants.append(float(entry.get()))

        # catch any exceptions (likely a ValueError) and print them
    except Exception as e:
        print(e)
        return

    # check validity of user inputs
    if step <= 0 or tol < 0 or max_iter <= 0 or l_bound == u_bound or fig_width < 1 or abs_max_root < 0 or u_bound < l_bound:
        messagebox.showinfo(title="Invalid input", message="Rules for algorithm options: \n- Step must be > 0\n- Tolerance must be >= 0\n- Max iterations must be > 0\n- Lower bound cannot be = to upper bound\n- Figure width must be >= 1\n- Absolute value of max root must be >= 0")
        return

    # get function type
    if radiobutton_var.get() == FUNCTION_OPTION_TEXT[0]:
        f = functions.polynomial
    elif radiobutton_var.get() == FUNCTION_OPTION_TEXT[1]:
        f = functions.trigonometric
    elif radiobutton_var.get() == FUNCTION_OPTION_TEXT[2]:
        f = functions.exponential

    else:
        # not meant to be possible? just in case, make f a function that returns 0
        def f(*args, **kwargs):
            return 0

    # enforce an upper limit to the amount of inputs
    if ((abs(l_bound) + abs(u_bound)) / step)**2 > MAX_INPUT_COUNT:
        messagebox.showinfo(title="Too many inputs", message=f"Too many inputs (max={MAX_INPUT_COUNT}), increase step or decrease input range")
        return

    # add x values to be used as inputs
    for i in np.arange(l_bound, u_bound, step):
        inputs.append(i)

    # get roots found from the inputs, each input paired with each other input.
    # e.g for [-1, 0, 1, 2], -1 and -1 as inputs, then -1 and 0, -1 and 1, -1 and 2, then -1 and -1, 0 and -1 and so on
    # this is since using -1 and 0 as inputs might produce a different result to 0 and -1
    for i, inp0 in enumerate(inputs):
        roots_secant.append([])
        roots_bisection.append([])

        for j, inp1 in enumerate(inputs):

            # manually free memory from big arrays and return if cancel button pressed
            if cancel.get():
                print("Calculations cancelled")
                del inputs
                del roots_bisection
                del roots_secant
                gc.collect()
                return

            # calculate roots
            r_s = algorithms.secant(f, inp0, inp1, max_iter, constants, subtype_selected, tol)
            r_b = algorithms.bisection(f, inp0, inp1, max_iter, constants, subtype_selected, tol)

            # turn the NaN returned because of a divide by zero error into a np.nan so that it can be recognized later
            if r_s == "NaN":
                r_s = 0

            # if no root was found and, for example, it blows up wildly or never settles, the "root" found after max_iter
            # will not be at a y value close to 0, and will mess up the entire plot. to fix this, set these values to np.nan
            if abs(f(subtype_selected, r_s, constants)) > tol:
                r_s = np.nan
            if abs(f(subtype_selected, r_b, constants)) > tol:
                r_b = np.nan

            # since trig functions have an infinite amount of roots, limit the solutions to +- 20 or the algorithm finds roots at really high x values, and the resulting plot has no variation in color (since the difference between pi and 2pi is negligable compared to pi and 75000, the scale is completly off)
            if f.__name__ == "trigonometric":
                if abs(r_s) > abs_max_root:
                    r_s = np.nan
                # if abs(r_b) > 20:
                #     r_b = np.nan

            # add the root the the array
            roots_secant[i].append(r_s)
            roots_bisection[i].append(r_b)

    # the name of the plot
    plot_name = format_function(radiobutton_var.get(), subtype_selected, constants)

    # create a new child window to display the resulting graph. It will close automatically if the parent window closes
    plot_window = tk.Toplevel(window)
    plot_window.title("Calculation results")

    # the figure that will contain the plot
    fig = Figure(figsize=(fig_width, fig_width/2), layout="tight")

    # adding the subplot
    plot1 = fig.add_subplot(121)
    plot2 = fig.add_subplot(122)

    # create the colormap. viridis doesn't have white in it (and its basically the default anyway)
    cmap = plt.colormaps["viridis"]

    # set any values that are np.nan (bad values) to white
    cmap.set_bad((1, 1, 1, 1))

    # get the date as day-month-year hour:minute:second
    date = datetime.today().strftime("%Y-%m-%d (y-m-d) %Hh%Mm%Ss")

    # plot roots on matplotlib color maps, set their titles and ensure the text wraps, then create a colorbar for each plot
    # secant:
    secant_img = plot1.pcolormesh(inputs, inputs, roots_secant, cmap=cmap)
    plot1.set_title("\n".join(textwrap.wrap(f"Secant: {plot_name}", 20)), fontsize=10)
    fig.colorbar(secant_img, ax=plot1, label="Roots")

    # bisection:
    bisection_img = plot2.pcolormesh(inputs, inputs, roots_bisection, cmap=cmap)
    plot2.set_title("\n".join(textwrap.wrap(f"Bisection: {plot_name}", 20)), fontsize=10)
    fig.colorbar(bisection_img, ax=plot2, label="Roots")

    # add text with the plot info. move plots up to allow enough space
    fig.text(0, 0, f"max iter {max_iter}, tol {tol}, size {fig_width}x{fig_width/2}, l bound {l_bound}, u bound {u_bound}, step {step}, max root {abs_max_root}", fontsize=10, wrap=True)
    fig.subplots_adjust(bottom=0.15)

    # create images folder if it doesn't exist
    if not os.path.isdir("images"):
        os.mkdir("images")

    # save entire plot. this must be done before drawing it or the image saved is white.
    formatted_plot_name = plot_name.replace("*", "")
    fig.savefig(f"images/{date} function {formatted_plot_name}.png")

    # creating the Tkinter canvas containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, plot_window)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().grid(row=0, column=0)

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas, plot_window, pack_toolbar=False)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().grid(row=1, column=0)


# TODO: ui to build and add multiple function types together
def rb_function_type_select():
    """
    Function for when a radio button is pressed. Creates the subtype entries/buttons depending on the radio button
    :return: None
    """

    # the text from the selected radio button
    selected = radiobutton_var.get()

    # clear the subtype options array and remove everything in the frame
    subtype_options.clear()
    for widget in func_subtype_frame.winfo_children():
        widget.destroy()

    # add title back in since it was destroyed
    title = tk.Label(text="Function subtypes:", master=func_subtype_frame)
    title.grid(row=0, column=0, columnspan=len(TRIG_TYPES))

    # create subtype buttons
    if selected == FUNCTION_OPTION_TEXT[0]:  # if polynomial
        # create the title
        title = tk.Label(master=func_subtype_frame, text="Enter degree of polynomial [0..25]")
        title.grid(row=1, column=0)

        # create entry for polynomial degree and add it to the subtype_options array
        polynomial_degree = tk.Entry(master=func_subtype_frame, textvariable=func_constants_sv)
        polynomial_degree.grid(row=2, column=0)
        subtype_options.append(polynomial_degree)

    elif selected == FUNCTION_OPTION_TEXT[1]:  # trig

        # display a warning
        messagebox.showinfo(title="Note", message="Roots/solutions found by trig functions are limited to +- 20 by default, as secant method can find roots at x values above 100000.\n"
                                                  "This makes the scale of the colormap way off, and makes it impossible to distinguish between any other roots.\n"
                                                  "You can increase the limit, but this is not recommended.")
        row = 1
        col = 0

        # create all the buttons for the different trig functions
        for n, t_type in enumerate(TRIG_TYPES):

            # create button with the text from the array. each button calls the same function
            btn = tk.Button(master=func_subtype_frame, text=t_type, command=lambda t=t_type: generate_func_constants(t))

            # arrange the button in a grid
            btn.grid(row=row, column=col)

            # update tasks to force calculation of size and position
            btn.update_idletasks()

            # if placing this widget will make it go beyond the width of the frame above, wrap around by incrementing row
            if btn.winfo_reqwidth() + btn.winfo_x() > func_select_frame.winfo_width():
                row += 1
                col = 0
                btn.grid_remove()

                # place button in grid at new position
                btn.grid(row=row, column=col)

            # increment column for next button
            col += 1

            # add button to array
            subtype_options.append(btn)

    elif selected == FUNCTION_OPTION_TEXT[2]:  # exponential
        title = tk.Label(master=func_subtype_frame, text="No subtypes")
        title.grid(row=1, column=0)

        # no subtypes, so allow user to input constants after pressing radiobutton
        generate_func_constants()


def generate_func_constants(*args):
    """
    Generates an appropriate amount of tk.Entry widgets for the function constants
    :param args: First value is subtype info (like the degree of the polynomial or type of trig function)
    :return: None
    """

    global subtype_selected  # bad practice, I know

    # clear array and remove any widgets in the frame
    function_constants.clear()
    for widget in func_constants_frame.winfo_children():
        widget.destroy()

    # 4 constants for exponential and trigonometric, so this is the default value
    degree = 4

    # if polynomial, get the degree and default to 0 if user didn't enter an integer
    if radiobutton_var.get() == FUNCTION_OPTION_TEXT[0]:
        try:
            degree = int(args[0].get())
        except Exception as e:
            print(e)
            degree = 0

        # basic checks to make sure degree is valid
        if degree > 25:
            degree = 0
            messagebox.showinfo(title="Invalid input", message="Polynomial degree too big, must not be greater than 25.\nDegree has been set to 0")

        elif degree < 0:
            degree = 0
            messagebox.showinfo(title="Invalid input", message="polynomial degree too small, must not be less than 0\nDegree has been set to 0")

        subtype_selected = degree

        # update function info text
        # constant * x ^ (degree) + increment letter for constant * x ^ (degree - 1) ...
        info = ""
        for p in range(0, degree):
            info += f"{chr(ord('a') + p)}*x^{degree - p} + "

        # add in the last constant (can also be done by making for loop go to degree + 1)
        info += chr(ord('a') + degree)
        function_info_sv.set(info)

        # a polynomial has one extra constant at the end where the power of x is 0 (i.e. a degree 5 polynomial has 6 constants), and so create one more Entry in the for loop
        degree += 1

    elif radiobutton_var.get() == FUNCTION_OPTION_TEXT[1]:  # if trig
        function_info_sv.set(f"a*{args[0]}(b*x + c) + d")
        subtype_selected = args[0]

    elif radiobutton_var.get() == FUNCTION_OPTION_TEXT[2]:  # if exponential
        function_info_sv.set(f"a*b^(x + c) + d")
        subtype_selected = 0

    # start row at 1, since title is at row 0
    row = 1
    col = 0
    max_cols = 1

    # generate degree amount of Entries for constants
    for i in range(0, degree):

        # create entry and label with text as the same letter from before
        label = tk.Label(master=func_constants_frame, text=chr(ord('a') + i))
        entry = tk.Entry(master=func_constants_frame, width=10)  # TODO: numbers entered into entry will update info text
        label.grid(row=row, column=col, pady=(40, 0))
        entry.grid(row=row + 1, column=col)

        # perform update to force tkinter to calculate size of widgets
        label.update_idletasks()
        entry.update_idletasks()

        # if this placing this entry will go beyond the screen, wrap around by incrementing the row and setting column to 0
        if entry.winfo_reqwidth() + entry.winfo_x() + func_constants_frame.winfo_x() > window.winfo_width():
            row += 1
            col = 0
            entry.grid_remove()
            label.grid_remove()

            # arrange the label and entry accordingly
            label.grid(row=row, column=col, pady=(40, 0))
            entry.grid(row=row + 1, column=col)

        # add entry to array
        function_constants.append(entry)

        # increment column for next entry
        col += 1

        # update max_cols
        if col > max_cols:
            max_cols = col

    # add title back
    title = tk.Label(text="Function constants:", master=func_constants_frame)
    title.grid(row=0, column=0, columnspan=max_cols)


def format_function(f_type, subtype, constants):
    """
    Returns a string created from the type of function and its constants, e.g. "3*sin(x+2)+2.4"
    :param f_type: function type, like polynomial or trig
    :param subtype: subtype, e.g. 3 or "sin"
    :param constants: constants of func
    :return: the function as a string
    """
    func_str = ""

    # same code as in generate_func_constants to create the function info text, just now use the constants array instead of letters
    if f_type == FUNCTION_OPTION_TEXT[0]:
        for i in range(0, subtype):
            if constants[i] == 0:  # no need to write out if the constant is 0
                continue

            func_str += f"{constants[i]}*x^{subtype - i}+"

        func_str += f"{constants[-1]}"

    elif f_type == FUNCTION_OPTION_TEXT[1]:
        func_str = f"{constants[0]}*{subtype}({constants[1]}x+{constants[2]})+{constants[3]}"

    elif f_type == FUNCTION_OPTION_TEXT[2]:
        func_str = f"{constants[0]}*{constants[1]}^(x+{constants[2]})+{constants[3]}"

    return func_str


# create window and set title
window = tk.Tk()
window.title('Root Finder')

# setting the dimensions of the main window
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# create frames
func_select_frame = tk.Frame()
current_info_frame = tk.Frame()
func_subtype_frame = tk.Frame()
algorithm_options_frame = tk.Frame()
func_constants_frame = tk.Frame()
func_plot_frame = tk.Frame(highlightbackground="grey", highlightthickness=1)

# layout of the frames in a grid
func_select_frame.grid(row=0, column=0)
current_info_frame.grid(row=0, column=1)
func_subtype_frame.grid(row=1, column=0)
algorithm_options_frame.grid(row=1, column=1)
func_constants_frame.grid(row=2, column=0, columnspan=2)
func_plot_frame.grid(row=3, column=0, columnspan=2)

# create the label above the radio buttons
radio_select_label = tk.Label(text="Choose function type: ", master=func_select_frame)
radio_select_label.grid(row=0, column=0)

# array to hold radio buttons
radio_buttons = []

# variable that the radio buttons will share
radiobutton_var = tk.StringVar(value=" ")

# create the radio buttons
for i in range(0, len(FUNCTION_OPTION_TEXT)):
    rb = tk.Radiobutton(text=FUNCTION_OPTION_TEXT[i],
                        master=func_select_frame,
                        command=rb_function_type_select,
                        variable=radiobutton_var,
                        value=FUNCTION_OPTION_TEXT[i])

    rb.grid(row=i+1, column=0)
    radio_buttons.append(rb)

# create function info text and setting it to a StringVar that will be updated later
function_info_sv = tk.StringVar(value="Function info will be displayed here")
function_info_text = tk.Label(textvariable=function_info_sv, master=current_info_frame, justify="center")

# bind the configure event so that when the text is set/updated, the wraplength is resized to be the same as the frame below it (algorithm options)
function_info_text.bind('<Configure>', lambda e: function_info_text.config(wraplength=algorithm_options_frame.winfo_width()))
function_info_text.grid(row=1, column=0)

# create subtype label
subtype_label = tk.Label(text="Function subtypes:", master=func_subtype_frame)
subtype_label.grid(row=0, column=0)
subtype_options = []
subtype_selected = ""  # this will only be modified in generate_func_constants into either a number or string, depending on the subtype passed in

# create algorithm options
algorithm_options_label = tk.Label(text="Algorithm options:", master=algorithm_options_frame)
algorithm_options_label.grid(row=0, column=0, columnspan=3)

# create and arrange labels and buttons for algorithm options
tk.Label(text="Max iterations >0", master=algorithm_options_frame).grid(row=1, column=0)
tk.Label(text="Step >0", master=algorithm_options_frame).grid(row=1, column=1)
tk.Label(text="Min input", master=algorithm_options_frame).grid(row=1, column=2)
tk.Label(text="Max input", master=algorithm_options_frame).grid(row=2, column=0, pady=(40, 0))
tk.Label(text="Tolerance >=0", master=algorithm_options_frame).grid(row=2, column=1, pady=(40, 0))
tk.Label(text="Fig width >0", master=algorithm_options_frame).grid(row=2, column=2, pady=(40, 0))
tk.Label(text="Max Abs val root", master=algorithm_options_frame).grid(row=3, column=0, pady=(40, 0))

# each entry needs a DoubleVar so the user input can be used later
max_iter_sv, min_input_sv, max_input_sv, tolerance_sv, step_sv, fig_width_sv, max_root_sv = tk.DoubleVar(value=20), tk.DoubleVar(value=-5), tk.DoubleVar(value=5), tk.DoubleVar(value=0.00001), tk.DoubleVar(value=0.1), tk.IntVar(value=6), tk.DoubleVar(value=20)

max_iterations_entry = tk.Entry(master=algorithm_options_frame, textvariable=max_iter_sv).grid(row=2, column=0)
step_entry = tk.Entry(master=algorithm_options_frame, textvariable=step_sv).grid(row=2, column=1)
min_input_entry = tk.Entry(master=algorithm_options_frame, textvariable=min_input_sv).grid(row=2, column=2)
max_input_entry = tk.Entry(master=algorithm_options_frame, textvariable=max_input_sv).grid(row=3, column=0)
tolerance_entry = tk.Entry(master=algorithm_options_frame, textvariable=tolerance_sv).grid(row=3, column=1)
fig_width_entry = tk.Entry(master=algorithm_options_frame, textvariable=fig_width_sv).grid(row=3, column=2)
max_root_root = tk.Entry(master=algorithm_options_frame, textvariable=max_root_sv).grid(row=4, column=0)

# create function constants options
function_constants_label = tk.Label(text="Function constants:", master=func_constants_frame)
function_constants_label.grid(row=0, column=0)
function_constants = []

# bind the Entry for the degree of the polynomial to a StringVar and use the trace method to call generate_func_constants
# when the entry is modified ("w" is for write). This is necessary since an Entry doesn't have a "command" option like buttons do
func_constants_sv = tk.StringVar()
func_constants_sv.trace("w", lambda name, index, mode, sv=func_constants_sv: generate_func_constants(sv))

# button that will display the plot. creates a new thread to handle the plot function so the main window is still responsive
cancel_calculations = tk.BooleanVar(value=False)
plot_button = tk.Button(master=func_plot_frame, command=lambda c=cancel_calculations: threading.Thread(target=plot, args=(cancel_calculations,)).start(), height=2, width=10, text="Plot")
plot_button.grid(row=0, column=0)


# button that will allow the calculations to be canceled if they are taking to long without terminating the thread forcefully
disable_label = tk.Label(textvariable=cancel_calculations, master=func_plot_frame)
disable_btn = tk.Button(text="Toggle cancelling calculations", master=func_plot_frame, command=lambda: cancel_calculations.set(not cancel_calculations.get()), height=2)
disable_btn.grid(row=0, column=1)
disable_label.grid(row=1, column=1)


# toolbar
menu = tk.Menu(window)
menu.add_command(label="Help", command=lambda: messagebox.showinfo(title="Help", message="NOTE: closing the main window while calculations are still ongoing terminates the thread while its storing massive arrays in memory and is probably a bad idea.\nTo cancel calculations and clear the arrays press the 'Toggle cancelling calculations' button so that it is set to true (1 is true, 0 is false)\n\n\n"
                                                                                         "Summary: \nThis program solves for the roots/solutions/x-intercepts of a function using Bisection and Secant method. The results are displayed on a 2D matplotlib colormap.\n"
                                                                                         "\nFunction Types: \nPolynomial: max degree of 25, the general formula will be displayed on the top right when you change the degree.\nTrigonometric: 'a' stands for arc, so asin is the inverse sin function. 'h' means hyperbolic, so cosh is the hyperbolic cos function. Note that \n-   a. some of these functions don't have a domain of R (like atanh) and \n-   b. some functions like cosh grow extremely rapidly, and can overflow. (these errors are caught and printed if they occur)\nExponential: can't have an asymptote at y=0, since the program will find a non-existent root\n" 
                                                                                         "\nAlgorithm options and entering info: \nAfter selecting the function, you can set the algorithm options, they are: \n-   Max iter: the max num of iterations the algorithm can run\n-   Step: The step between each generated input from min and max values (smaller step more inputs)\n-   Min/max input: The min/max value that will be used as the initial input\n-   Tolerance: How close to 0 the algorithms can get before concluding they found a root\n-   Fig width: the width of the window that displays the plot\n-   Max abs val root: for trigonometric functions, this is the max value that the algorithm can find, this is necessary since secant can find, for example, a solution to sin at 500,000\n"
                                                                                         "\nPlotting: \nEach pixel represents the output of the respective algorithm, and the color represents the x-value of the output. The x and y position of the pixel represents the two x inputs for the algorithm that lead to it finding that root.\n"))
window.config(menu=menu)


# give equal weight to columns 0 and 1, so they are evenly spaced out
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)

# call function on window close
# window.protocol("WM_DELETE_WINDOW", on_closing)

# run the gui
if __name__ == "__main__":
    window.mainloop()

"""
Error Log:
 / errors and issues with pack() and grid()
 / figuring out Frames (and how pack/grid work for stuff inside it)
 / radio buttons not doing anything when pressed (had to give them a shared StringVar)
 / radio buttons all start out selected (StringVar init value changed to " ")
 * bisection method might be implemented wrong?
 / problems with layout of Frames
 * problems with tkinter + matplotlib for plot and toolbar
 / issues with widget winfo_x, winfo_rootx, update, and wrapping widgets
 / entry doesn't have a "command" option?
 / figuring out how to update function info text dynamically
 - needed doublevars instead of stringvars for algorithm options
 / too many trig subtypes, how to generalise trig function?
 / had to add "t" to all function types
 - tkinter canvas is weirdly shaped and messed up layout
 / algorithms are giving massive values for roots and result in unexpected colors/patterns
 / solved pack error message by going into _backend_tk.py from NavigationToolbar2Tk definition and finding that I needed to turn pack_toolbar=False
 / algorithms sometimes find massive roots and ruin the scale of the colormap
 / algorithms sometimes give only 0 as an output?
 / graph sizes are inconsistent (big titles), and since I don't want to hard code something so that it will fit into the window, so made the results show up in a smaller new window
 / program freezes when calculating, maybe multithreading will fix?
 / the x and y axis where the index of the inputs from the array, not the value of the inputs themselves
 / managed to find how to set specific pixels to white, but now how to decide which pixels are out of range?
 / the graphs are sometimes squished? for some reason the colorbar text is occasionally long? and only for polynomials of degree 3 or greater
 / managed to save plot as image without it being white, had to look at documentation and also simplified to one longer figure with 2 plots instead of 2 figures
 / couldn't save file with date and time, removed each part to check what was wrong, found out that cant use colons in file names
 / can't use * or + in a filename, so remove * and replace + with p
 / after playing around, realised that if figure small then small step will still produce grainy image because not enough pixels. added fig width entry
 / after running it with big fig width and small step caused it to use up over 1gb of memory, I a. went back and fixed the code to enforce a max input count and b. started trying to figure out a way to cancel calculations if they take too long 
 - found out I could use a tk.BooleanVar to store if the calculations should be done, and by passing it into the function I can effectively stop the second thread early without terminating it 
 / hyperbolic functions produce a math range error, and exponential functions don't display anything? oh, exponential was 1^x, so ofc no roots
"""