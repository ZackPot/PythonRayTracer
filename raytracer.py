import numpy as np
import math
import matplotlib.pyplot as plt

def calc_euclid_dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)

class Light:
    def __init__(self, position: np.typing.NDArray, intensity: np.typing.NDArray):
        self.position = position
        self.intensity = intensity

class Face:
    def __init__(self, vertices: np.typing.NDArray):
        self.vertices = vertices

class Shape:
    def __init__(self, faces: np.typing.NDArray):
        self.faces = faces

    def flip_normals(self):
        for face in self.faces:
            face.vertices[[0, 1]] = face.vertices[[1, 0]]

class Ray:
    def __init__(self, origin: np.typing.NDArray, direction: np.typing.NDArray):
        self.brightness = 0
        self.origin = origin
        self.direction = direction

    @staticmethod
    def detect_collision(shape_faces, direction, origin):
        best_normal = None
        closest_t = float('inf')
        closest_hit = None

        for face in shape_faces:
            edge1 = face.vertices[1] - face.vertices[0]
            edge2 = face.vertices[2] - face.vertices[0]
            fnormal = np.linalg.cross(edge1, edge2)
            fnormal = fnormal / np.linalg.norm(fnormal)

            a = face.vertices[0]

            if np.round(np.dot(fnormal, direction), 2) == 0:
                pass
            else:
                t = np.dot((a - origin), fnormal) / np.dot(fnormal, direction)
                if t <= 0:
                    pass
                else:
                    intersection = origin + t * direction
                    v0 = face.vertices[1] - face.vertices[0]
                    v1 = face.vertices[2] - face.vertices[0]
                    v2 = intersection - face.vertices[0]

                    d00 = v0 @ v0
                    d01 = v0 @ v1
                    d11 = v1 @ v1
                    d20 = v2 @ v0
                    d21 = v2 @ v1

                    denominator = d00 * d11 - d01 * d01
                    u = (d11 * d20 - d01 * d21) / denominator
                    v = (d00 * d21 - d01 * d20) / denominator

                    if u >= 0 and v >= 0 and (u + v) <= 1:
                        if t < closest_t:
                            closest_t = t
                            closest_hit = intersection
                            best_normal = fnormal

        return closest_hit, best_normal

    def bounce(self, light, faces: np.typing.NDArray):
        intersection_point, normal = self.detect_collision(faces, self.direction, self.origin)

        if intersection_point is not None:
            light_vec = light.position - intersection_point
            total_dist = calc_euclid_dist(light.position, intersection_point)
            light_dir = light_vec / total_dist

            dot_product = np.dot(normal, light_dir)

            if dot_product <= 0:
                self.brightness = 0
            else:
                shadow_origin = intersection_point + normal * 1e-2
                shadow_point, _ = self.detect_collision(faces, light_dir, shadow_origin)

                if shadow_point is None or calc_euclid_dist(shadow_origin, shadow_point) >= total_dist:
                    self.brightness = (light.intensity * dot_product) / (4 * math.pi * total_dist ** 2)
                else:
                    self.brightness = 0
        else:
            self.brightness = 0


class Camera:
    def __init__(self, origin: np.typing.NDArray):
        self.origin = origin
        self.camera_plane = []
        self.render = []

    def update_camera_plane(self, target_pos, size=2.0, res=100):
        target_pos = np.array(target_pos, dtype=float)
        forward = target_pos - self.origin
        forward /= np.linalg.norm(forward)

        right = np.array([-forward[1], forward[0], 0.0])
        right /= np.linalg.norm(right)

        up = np.array([0.0, 0.0, 1.0])
        up -= np.dot(up, forward) * forward
        up /= np.linalg.norm(up)

        plane_center = self.origin + forward * 2
        ticks = np.linspace(-size / 2, size / 2, res)

        self.camera_plane = []
        for j in reversed(ticks):
            for i in ticks:
                self.camera_plane.append(plane_center + i * right + j * up)

    def render_img(self, faces, light, samples=4):
        res = int(math.sqrt(len(self.camera_plane)))
        pixels = np.array(self.camera_plane).reshape(res, res, 3)

        for row in range(res):
            for col in range(res):
                total = 0
                for _ in range(samples):
                    jitter = (np.random.rand(3) - 0.5) * 0.001
                    point = pixels[row, col] + jitter
                    direction = point - self.origin
                    direction /= np.linalg.norm(direction)
                    ray = Ray(self.origin, direction)
                    ray.bounce(light, faces)
                    total += ray.brightness
                self.render.append(total / samples)

        self.render = np.array(self.render).reshape(res, res)

        if np.max(self.render) > 0:
            self.render = self.render / np.max(self.render) * 0.8
        else:
            self.render = np.zeros_like(self.render)

        dy, dx = np.gradient(self.render)
        edge_intensity = np.sqrt(dx ** 2 + dy ** 2)
        edges = edge_intensity > 0.08

        self.render = np.where(edges, 1.0, self.render)
        plt.imshow(self.render, cmap='gray', interpolation='lanczos')
        plt.colorbar(label='Brightness')

camera = Camera(np.array([5.0, -5.0, 3.0]))
camera.update_camera_plane(np.array([0, 0, 1]), res=250, size=1)

light = Light(np.array([4.0, -4.0, 4.0]), 1000)

v0 = np.array([-1, -1, -1+1])
v1 = np.array([ 1, -1, -1+1])
v2 = np.array([ 1, -1, 1+1])
v3 = np.array([-1, -1, 1+1])
v4 = np.array([-1, 1, -1+1])
v5 = np.array([ 1, 1, -1+1])
v6 = np.array([ 1,  1,  1+1])
v7 = np.array([-1,  1,  1+1])

cube_faces = [
    Face(np.array([v0, v1, v2])), Face(np.array([v0, v2, v3])),
    Face(np.array([v4, v6, v5])), Face(np.array([v4, v7, v6])),
    Face(np.array([v0, v5, v1])), Face(np.array([v0, v4, v5])),
    Face(np.array([v3, v2, v6])), Face(np.array([v3, v6, v7])),
    Face(np.array([v0, v3, v7])), Face(np.array([v0, v7, v4])),
    Face(np.array([v1, v6, v2])), Face(np.array([v1, v5, v6]))
]

f0 = [-5, -5, -0.01]
f1 = [ 5, -5, -0.01]
f2 = [ 5,  5, -0.01]
f3 = [-5,  5, -0.01]

plane_faces = [
    Face(np.array([f0, f1, f2])),
    Face(np.array([f0, f2, f3]))
]

plane = Shape(plane_faces)
#plane.flip_normals()
cube = Shape(cube_faces)
# cube.flip_normals()
all_faces = plane.faces + cube.faces

camera.render_img(all_faces, light)
plt.show()