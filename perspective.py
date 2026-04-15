import numpy as np
import math
import tkinter as tk

# constants
angle = 0
barrier = 10
scale = 0

# functions
def generate_edge_list(shape):
    edge_map = {}
    for i, point in enumerate(shape):
        distances = []
        for j, point2 in enumerate(shape):
            if i == j: continue
            dist = np.linalg.norm(point - point2)
            distances.append((dist, j))

        distances.sort()
        edge_map[i] = [d[1] for d in distances[:4]]
    return edge_map

def get_rotation_matrix(A, B):
    A = A / np.linalg.norm(A)
    B = B / np.linalg.norm(B)

    v = np.linalg.cross(A, B)
    s = np.linalg.norm(v)
    c = np.dot(A, B)

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
    render_vectors = np.dot(render_vectors, rotation)

    for vector in render_vectors:
        scale = np.dot(camera_plane, rotation)[1, 2] / vector[2]
        vector *= scale
    return render_vectors, scale


def draw(render_vectors, canvas, canvas_w, canvas_h, margin, edge_list, scale, shape):
    if np.mean(viewing_point - np.mean(shape, axis = (0, 1))) > barrier:
        pass
    else:
        x_coords = render_vectors[:, 0]
        y_coords = render_vectors[:, 1]
        min_x, max_x = np.min(x_coords), np.max(x_coords)
        min_y, max_y = np.min(y_coords), np.max(y_coords)

        data_w = max_x - min_x if max_x != min_x else 1
        data_h = max_y - min_y if max_y != min_y else 1
        scale = min((canvas_w - 2 * margin) / data_w, (canvas_h - 2 * margin) / data_h)

        pts = []
        for x, y, _ in render_vectors:
            screen_x = (x - min_x) * scale + margin
            screen_y = (y - min_y) * scale + margin
            pts.append((screen_x, screen_y))

        for i, screen_pt in enumerate(pts):
            neighbor_indices = edge_list[i]
            for n_idx in neighbor_indices:
                neighbor_pt = pts[n_idx]
                canvas.create_line(screen_pt[0], screen_pt[1], neighbor_pt[0], neighbor_pt[1], fill="red")


def update_camera_plane(target_pos):
    forward = target_pos - viewing_point
    forward = forward / np.linalg.norm(forward)

    plane_center = viewing_point + (forward * 2)

    return np.array([
        plane_center + [-1, -1, 0],  # Top Left
        plane_center + [-1, 1, 0],  # Bottom Left
        plane_center + [1, 1, 0],  # Bottom Right
        plane_center + [1, -1, 0]  # Top Right
    ])

def key_handler(event):
    print(event.char)
    if event.char == 'a':
        viewing_point[0] += 1
    elif event.char == 'd':
        viewing_point[0] -= 1
    elif event.char == 's':
        viewing_point[1] += 1
    elif event.char == 'w':
        viewing_point[1] -= 1
    elif event.char == 'e':
        viewing_point[2] -= 1
    elif event.char == 'q':
        viewing_point[2] += 1
    else:
        pass

def animate():
    global angle, pyramid, camera_plane, viewing_point

    canvas.delete("all")
    camera_plane = update_camera_plane(np.mean(pyramid, axis=(0, 1)))
    current_render, current_scale = render(pyramid, camera_plane, viewing_point)
    draw(current_render, canvas, 400, 400, 50, edge_list, current_scale, pyramid)

    root.after(16, animate)

# main

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

controls = tk.Text(root, width=400, height=50)

control_text = """W - Forwards, S - Backwards
A - Right, D - Left
Q - Up, E - Down"""

controls.insert(tk.END, control_text)
controls.pack()

draw(render_vectors, canvas, 400, 400, 20, edge_list, scale, pyramid)
root.bind("<Key>", key_handler)
animate()
root.mainloop()