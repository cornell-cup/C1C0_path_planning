###########GLOBAL VARIABLES############

# Speed ie time between updates
speed = 300
# THE REAL LIFE REPRESENTATION OF TILE SIZE IN CM
tile_size = 40
# The GUI size of tiles in pixels(every pixel represents tile_size/GUI_tile_size)
GUI_tile_size = 4
# The tile sclaing factor is how many cm every pixel represents
tile_scale_fac = tile_size/GUI_tile_size

# height of window
tile_num_height = 160
# width of window
tile_num_width = 160
# visibility radius
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