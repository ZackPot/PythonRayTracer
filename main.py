import numpy as np
import math
import tkinter as tk
from tqdm import tqdm

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

render_vectors = np.array([])

for point in pyramid:
    vector = np.array([[viewing_point[0] - point[0], viewing_point[1] - point[1], viewing_point[2] - point[2]]])
    render_vectors = np.append(render_vectors, vector)

render_vectors = render_vectors.reshape((render_vectors.shape[0] // 3, 3))

for vector in render_vectors:
    scale = (viewing_point[2] - height_of_camera) / vector[2]
    vector *= scale
print('Vectors assembeled...')

root = tk.Tk()
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

x_coords = render_vectors[:, 0]
y_coords = render_vectors[:, 1]
min_x, max_x = np.min(x_coords), np.max(x_coords)
min_y, max_y = np.min(y_coords), np.max(y_coords)

canvas_w, canvas_h = 400, 400
margin = 20

data_w = max_x - min_x if max_x != min_x else 1
data_h = max_y - min_y if max_y != min_y else 1
scale = min((canvas_w - 2 * margin) / data_w, (canvas_h - 2 * margin) / data_h)

flat_points = []
for x, y, _ in tqdm(render_vectors):
    screen_x = (x - min_x) * scale + margin
    screen_y = (y - min_y) * scale + margin
    flat_points.extend([screen_x, screen_y])

canvas.create_line(*flat_points, fill="blue", width=3)
root.mainloop()