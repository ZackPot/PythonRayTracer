import numpy as np
import math

pyramid = np.array([
    [0, 0, 0],
    [0, 1, 0],
    [1, 0, 0],
    [1, 1, 0],
    [0.5, 0.5, 1]
])

viewing_point = np.array([0.5, 0.5, 10])

viewing_angle = 60 # angle
height_of_camera = 3 # z of camera plane
opposite = height_of_camera * math.tanh(viewing_angle) # y of camera plane
camera_width = 2 # x of camera plane

camera_plane = np.array([[0.5 - camera_width / 2, 0.5 - opposite, viewing_point[2] - height_of_camera],
                         [0.5 - camera_width / 2, 0.5 + opposite, viewing_point[2] - height_of_camera],
                         [0.5 + camera_width / 2, 0.5 + opposite, viewing_point[2] - height_of_camera],
                         [0.5 + camera_width / 2, 0.5 - opposite, viewing_point[2] - height_of_camera]])