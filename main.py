import numpy as np
import math
import tkinter as tk
from tqdm import tqdm
from itertools import combinations

def get_rotation_matrix(A, B):
    A = A / np.linalg.norm(A)
    B = B / np.linalg.norm(B)

    v = np.linalg.cross(A, B)
    s = np.linalg.norm(v)
    c = np.dot(A, B)
    print(f's: {s}; c: {c}; v: {v}')

    vx = np.array([[0, -v[2], v[1]],
                   [v[2], 0, -v[0]],
                   [-v[1], v[0], 0]])

    if math.isclose(c, 1.0, rel_tol=1e-9):
        return np.eye(3)
    elif math.isclose(c, -1.0, rel_tol=1e-9):
        return -np.eye(3)
    else:
        rotation_matrix = np.eye(3) + vx + (vx @ vx) * (1 / (1 + c))
        return rotation_matrix

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

camera_plane = np.array([[0.5 - camera_width / 2, 0.5 - opposite, viewing_point[2] - height_of_camera + 5],
                         [0.5 - camera_width / 2, 0.5 + opposite, viewing_point[2] - height_of_camera],
                         [0.5 + camera_width / 2, 0.5 + opposite, viewing_point[2] - height_of_camera],
                         [0.5 + camera_width / 2, 0.5 - opposite, viewing_point[2] - height_of_camera]])

render_vectors = np.array([])

for point in pyramid:
    vector = np.array([[viewing_point[0] - point[0], viewing_point[1] - point[1], viewing_point[2] - point[2]]])
    render_vectors = np.append(render_vectors, vector)

render_vectors = render_vectors.reshape((render_vectors.shape[0] // 3, 3))

b = np.array([camera_plane[0, 0] - camera_plane[3, 0], camera_plane[0, 1] - camera_plane[3, 1],
              camera_plane[0, 2] - camera_plane[3, 2]])
A = np.array([1, 0, 0])

rotation = get_rotation_matrix(A, b)
print(rotation)
render_vectors = np.dot(render_vectors, rotation)

for vector in render_vectors:
    scale = np.dot(camera_plane, rotation)[1, 2]  / vector[2]
    print(scale)
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

pts = list(zip(flat_points[0::2], flat_points[1::2]))

for p1, p2 in combinations(pts, 2):
    canvas.create_line(p1, p2, fill='red')

root.mainloop()