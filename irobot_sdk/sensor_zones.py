#
# Licensed under 3-Clause BSD license available in the License file. Copyright (c) 2020 iRobot Corporation. All rights reserved.
#

# TODO: Remove this file if not used

""" This function computes the pixels per zone and returns an array of
 sensor detection zones ready to be used by high level methods that deal
 with the color sensor. The distribution can be improved a lot, but
 for now the following are the zone counts that work better:

 Work nicely:
    1, 2, 3, 4, 5, 6, 8, 10, 14, 15, 16, 28, 29, 30, 31, 32

 Acceptable:
    7, 26.
 Horrible:
    9, 11, 12, 13, 17 (the worst), 18, 19, 20, 21, 22, 23, 24, 25, 27 """

def sensor_zones(sensors_count, colors):
    zones = []
    zones_count = len(colors)

    if zones_count <= 0:
        raise ValueError('There must be at least one sensor detection zone.')

    pixels_per_zone = sensors_count // zones_count
    remaining_pixels = sensors_count % zones_count

    for i in range(0, zones_count):
        newZone = [colors[i]] * pixels_per_zone
        zones += newZone

    # try to distribute the remaining pixels (if any) in a symmetric way:
    if remaining_pixels != 0:
        if zones_count % 2 == 0:
            if remaining_pixels % 2 == 0:
                # picks the color of the corresponding zone to generate the extra pixels
                # first zone
                zones = [colors[0]] * (remaining_pixels // 2) + zones
                # last zone
                zones += [colors[zones_count - 1]] * (remaining_pixels // 2)
            else:
                # pixels can not be distributed symmetrically
                raise ValueError('Invalid sensor detection zones count.')
        else:
            # picks the color from the central zone to generate the extra pixels
            extraPixels = [colors[zones_count // 2]] * (remaining_pixels)
            for i in extraPixels:
                zones.insert(len(zones) // 2, i)  # central zone

    return zones
