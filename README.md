# Root-Finder

A python program written as part of a school project. Uses [secant](https://en.wikipedia.org/wiki/Secant_method) and [bisection](https://en.wikipedia.org/wiki/Bisection_method) methods for finding the roots/solutions of equations using a range of inputs decided by the user, then plots the results on 2d matplotlib [colormap](https://matplotlib.org/stable/tutorials/colors/colormap-manipulation.html#sphx-glr-tutorials-colors-colormap-manipulation-py).


![tan(x) example](https://github.com/shasumag/Root-Finder/assets/86345158/b3c61771-4068-4a6d-8015-c4d1352ad6f9)

## Interpreting plot
The x and y axis are both x values. They are the initial x values given to the algorithm, and the color of that pixel corresponds to the solution found using those inputs, where white is no root found (either too many iterations without reaching tolerance or root was too big, as dictated by "max abs val root"). In the above example, solving tan(x) using secant with any 2 inputs from -4 to -2 will find the solution at pi, while if one input is -4 and another is around 2, small variations in the second input will either find different roots or no roots at all.

## Saving images
Images are saved to an "images" folder in the same directory as the main.py file, the folder is created if it does not exist. The file name has the date and time it was created and the function itself. all other information (algorith options) is displayed on the plot as text.

## Dependencies
Uses tkinter, matplotlib, numpy, textwrap, threading, gc, and os

## Settings

You can change the following settings through the tkinter gui:
 - function type
 - function subtype
 - max iterations
 - min input
 - max input
 - step
 - tolerance
 - fig width
 - max abs val root
 - function constants
 - toggle cancelling calculations

(this information is also in the "help" popup)

### Function type
Currently only 3 options: polynomial, trigonmetric, and exponential.

### Function subtype
For polynomial, this is the degree
For trigonometric, this is the specific function, e.g. sin
No subtypes for exponential

### max iterations
This decides how many iterations the algorithm can run before either reaching a solution or giving up. If an image looks noisy and has lots of white spots, sometimes increasing max iterations helps.
Example:
![white spots example](https://github.com/shasumag/Root-Finder/assets/86345158/37f78c18-caeb-4728-b7b5-85a15a92d486)

### Min, max, step
The min and max values set the min and max inputs that will be used as the initial x values in both secant and biseciton method. Step decides how many inputs there will be between the min and max. Example:

Min=-2, max=5, step=1: initial inputs=[-2, -1, 0, 1, 2, 3, 4, 5]

Min=2, max=5, step=0.5: initial inputs=[2, 2.5, 3, 3.5, 4, 4.5, 5]

### tolerance
How close to a solution the algorithm can get to 0 before concluding it got to a solution

### fig width
How wide the matplotlib figure will be (height=1/2 width). If you want more detailed plots (high step), you need to increase this otherwise there won't be enough pixels and it will look the same as if you had a low step value.

### max abs val root
Weird name, but beacuse secant can find solutions to trig functions past x>100,000 there needs to be a limit otherwise the colormap scale is way off (plotting x=100,000 means you can't tell the difference between x=3 and x=6). This value is this limit, i.e. its the absolute value of the maximum value that the algorithm is allowed to find a root at.
by default its 20, but this is completely arbitrary.

### toggle cancelling calculations
The program is not very good if I'm honest, the program creates a new thread to run calculations, but I don't call .join() anywhere. To stop the second thread that is created while it is doing the calculations you need to toggle this button to 1. While it is on 1, the plot function will immediately clear all arrays and return (incase it was frozen and taking up a lot of memory). You can then close the program or toggle it back to 0 and plot something else.
