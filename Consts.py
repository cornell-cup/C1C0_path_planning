###########GLOBAL VARIABLES############

# time between updates for DynamicGUI in ms
speed_dynamic = 200
# time between updates for StaticGUI
speed_static = 10
# THE REAL LIFE REPRESENTATION OF TILE SIZE IN CM
tile_size = 40
# The GUI size of tiles in pixels(every pixel represents tile_size/GUI_tile_size)
GUI_tile_size = 4
# The tile sclaing factor is how many cm every pixel represents
tile_scale_fac = tile_size / GUI_tile_size

# height of window
tile_num_height = 200
# width of window
tile_num_width = 200
# visibility radius (in real life cm)
# INV: vis_radius/tile_size must be an int
vis_radius = 1000

# The radius of the robot
robot_radius = 80
# The bloat factor (how many times the radius of robot to bloat tiles by)
bloat_factor = 2

# recalculation rate
steps_to_recalc = 9

# line length for dynamic smoot path
length_draw = 1

# how many degrees to turn per iteration
turn_speed = 5

# degree frequency at which to generate lidar data
degree_freq = 1
