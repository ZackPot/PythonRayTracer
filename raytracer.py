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

class Ray:
    def __init__(self, origin: np.typing.NDArray, direction: np.typing.NDArray):
        self.brightness = 0
        self.origin = origin
        self.direction = direction

    @staticmethod
    def detect_collision(shape_faces, direction, origin):
        fnormal = None
        best_normal = None
        closest_t = float('inf')
        closest_hit = None

        for face in shape_faces:
            edge1 = face.vertices[1] - face.vertices[0]
            edge2 = face.vertices[2] - face.vertices[0]
            fnormal = np.linalg.cross(edge1, edge2)
            weight1 = 2
            weight2 = 5
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
            light_dir = light.position - intersection_point
            light_dir /= np.linalg.norm(light_dir)
            dot_product = max(0, np.dot(normal, light_dir))

            light_dist = calc_euclid_dist(light.position, intersection_point)
            self.brightness = (light.intensity * dot_product) / (4 * math.pi * light_dist ** 2)
        else:
            self.brightness = 0

class Camera:
    def __init__(self, origin: np.typing.NDArray):
        self.origin = origin
        self.camera_plane = None
        self.render = []

    def update_camera_plane(self, target_pos, size=2.0, res=10):
        target_pos = np.array([float(point) for point in target_pos])
        forward = target_pos - self.origin
        forward /= np.linalg.norm(forward)

        world_up = np.array([0, 1, 0])
        right = np.cross(world_up, forward)
        right /= np.linalg.norm(right)
        up = np.cross(forward, right)

        plane_center = self.origin + (forward * 2)

        grid_points = []
        ticks = np.linspace(-size / 2, size / 2, res)
        for i in ticks:
            for j in ticks:
                point = plane_center + (i * right) + (j * up)
                grid_points.append(point)

        half = size / 2
        corners = np.array([
            plane_center - half * right - half * up,
            plane_center - half * right + half * up,
            plane_center + half * right + half * up,
            plane_center + half * right - half * up
        ])

        self.camera_plane = np.vstack((grid_points, corners))

    def render_img(self, faces, light):
        for point in self.camera_plane:
            ray = Ray(self.origin, point - self.origin)
            ray.bounce(light, faces)
            self.render.append(ray.brightness)

        self.render = self.render[:-4]
        res = int(math.sqrt(len(self.render)))
        self.render = np.array(self.render).reshape(res, res)
        self.render = self.render / np.max(self.render) * 0.8

        dy, dx = np.gradient(self.render)
        edge_intensity = dx ** 2 + dy ** 2
        edges = edge_intensity > 0.005

        self.render = np.where(edges, 1.0, self.render)
        plt.imshow(self.render, cmap='gray')
        plt.colorbar(label='Brightness')

camera = Camera(np.array([4, 4, 4]))
camera.update_camera_plane(np.array([0.5, 0.5, 0.5]), res=500)

pyramid_faces = []

light = Light(np.array([5, 5, 5]), 10)

v0 = [0, 0, 0]
v1 = [1, 0, 0]
v2 = [1, 0, 1]
v3 = [0, 0, 1]

v4 = [0, 1, 0]
v5 = [1, 1, 0]
v6 = [1, 1, 1]
v7 = [0, 1, 1]

cube_faces = [
    Face(np.array([v0, v1, v2])), Face(np.array([v0, v2, v3])),
    Face(np.array([v4, v5, v6])), Face(np.array([v4, v6, v7])),
    Face(np.array([v0, v1, v5])), Face(np.array([v0, v5, v4])),
    Face(np.array([v3, v2, v6])), Face(np.array([v3, v6, v7])),
    Face(np.array([v0, v3, v7])), Face(np.array([v0, v7, v4])),
    Face(np.array([v1, v2, v6])), Face(np.array([v1, v6, v5]))
]

cube = Shape(cube_faces)
camera.render_img(cube.faces, light)
plt.show()