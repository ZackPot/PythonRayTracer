import numpy as np
import math
import tkinter as tk
from tqdm import tqdm
from itertools import combinations

def search_from_distance(distance, point, shape):
    euclidean_distance = lambda x1, y1, z1, x2, y2, z2: math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    for pt in shape:
        distance = euclidean_distance(point[0], point[1], point[2], pt[0], pt[1], pt[2])
        if distance == distance:
            return pt

def generate_edge_list(shape):
    euclidean_distance = lambda x1, y1, z1, x2, y2, z2: math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    point_distances = {} # dict {point data: [list of 3 closest points]}
    for point in shape:
        distances = []
        for point2 in shape:
            distances.append(euclidean_distance(point[0], point[1], point[2], point2[0], point2[1], point2[2]))

        distances.sort()
        four_closest = [distances[1], distances[2], distances[3], distances[4]]

        point_distances[tuple(point)] = four_closest

    return point_distances

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

def render(points, camera_plane, viewing_point):
    render_vectors = np.array([])

    for point in points:
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
        scale = np.dot(camera_plane, rotation)[1, 2] / vector[2]
        vector *= scale
    return render_vectors, scale


def draw(render_vectors, canvas, canvas_w, canvas_h, margin, edge_list, scale, shape):
    x_coords = render_vectors[:, 0]
    y_coords = render_vectors[:, 1]
    min_x, max_x = np.min(x_coords), np.max(x_coords)
    min_y, max_y = np.min(y_coords), np.max(y_coords)

    data_w = max_x - min_x if max_x != min_x else 1
    data_h = max_y - min_y if max_y != min_y else 1
    scale = min((canvas_w - 2 * margin) / data_w, (canvas_h - 2 * margin) / data_h)

    flat_points = []
    for x, y, _ in tqdm(render_vectors):
        screen_x = (x - min_x) * scale + margin
        screen_y = (y - min_y) * scale + margin
        flat_points.extend([screen_x, screen_y])

    pts = list(zip(flat_points[0::2], flat_points[1::2]))
    scaled_render_vectors = np.round(render_vectors / scale, decimals = 1)

    print(edge_list)

    for point in enumerate(pts):
        og_point = shape[point[0]]
        closest = edge_list[tuple(float(v) for v in og_point)]
        print(closest)

        close_points = []
        for distance in closest:
            close_points.append(search_from_distance(distance, og_point, shape))
        close_points = np.array(close_points)

        closest_indices = []
        for cp in close_points:
            matches = np.where(np.all(pyramid == cp, axis=1))[0]
            closest_indices.extend(matches)

        print(pts)
        pts = np.array(pts)
        closest_pts = pts[closest_indices]

        for close_pt in closest_pts:
            canvas.create_line(pts[1][0], pts[1][1], close_pt[0], close_pt[1], fill="red")


pyramid = np.array([
    [0, 0, 0],
    [0, 1, 0],
    [1, 0, 0],
    [1, 1, 0],
    [0.5, 0.5, 1]
])

edge_list = generate_edge_list(pyramid)
viewing_point = np.array([0.5, 0.5, 10])

viewing_angle = 60 # angle
height_of_camera = 3 # z of camera plane
opposite = height_of_camera * math.tanh(viewing_angle) # y of camera plane
camera_width = 2 # x of camera plane

camera_plane = np.array([[0.5 - camera_width / 2, 0.5 - opposite, viewing_point[2] - height_of_camera],
                         [0.5 - camera_width / 2, 0.5 + opposite, viewing_point[2] - height_of_camera],
                         [0.5 + camera_width / 2, 0.5 + opposite, viewing_point[2] - height_of_camera],
                         [0.5 + camera_width / 2, 0.5 - opposite, viewing_point[2] - height_of_camera ]])

render_vectors, scale = render(pyramid, camera_plane, viewing_point)

root = tk.Tk()
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()

draw(render_vectors, canvas, 400, 400, 20, edge_list, scale, pyramid)
root.mainloop()