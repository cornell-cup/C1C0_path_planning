========================================================================================================================
======================================Cornell Cup C1C0 path planning simulation=========================================
========================================================================================================================

This is a simulation that shows C1C0 planning paths and animates the movement of C1C0.
There are many different simulations that can be run, All you need to run these simulations is Python installed.

    1. Run 'python DynamicSmoothedGUI.py' - this runs a simulation where C1C0 is in an unknown environment and plans
    a path from the center of the grid to a user specified endpoint. In this simulation C1C0 slowly discovers the
    environment as mock sensor data is fed to the robot. The path is also smoothed So C1C0 always travels in straight
    lines. The GUI can not draw small lines, so the animation appears as grid tiles being filled in instead of small
    lines being drawn

    2. Run 'python staticGUI.py' - This runs a simulation where C1C0 is in a known environment and plans a path from
    the top left of the screen to the bottom right. This is not animated and draws a single smoothed line.

    3. Run 'DynamicGUI.py' - This runs a simulation where C1C0 starts in an unknown environment and then plans a path
    from the center of the grid do a specified endpoint. There is not path smoothing in this algorithm so C1C0