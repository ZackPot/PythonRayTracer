import numpy as np

class Camera:
    def __init__(self, origin: np.typing.NDArray):
        self.origin = origin
        self.camera_plane = None

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
        print(self.camera_plane)

class Face:
    def __init__(self, vertices: np.typing.NDArray):
        self.vertices = vertices

class Shape:
    def __init__(self, faces: np.typing.NDArray):
        self.faces = faces

class Ray:
    def __init__(self, brightness: int, origin: np.typing.NDArray, direction: np.typing.NDArray):
        self.brightness = brightness
        self.origin = origin
        self.direction = direction

    @staticmethod
    def detect_collision(shape_faces, direction, origin):
        for face in shape_faces:
            edge1 = face.vertices[1] - face.vertices[0]
            edge2 = face.vertices[2] - face.vertices[0]
            normal = np.linalg.cross(edge1, edge2)
            weight1 = 2
            weight2 = 5
            a = (face.vertices[0] + weight1 * (face.vertices[1] - face.vertices[0]) + weight2
                 * (face.vertices[2] - face.vertices[0]))

            if np.round(np.dot(normal, direction), 2) == 0:
                dist = np.sqrt(np.sum(direction ** 2))
                brightness = 1 / dist ** 2
                return brightness
            else:
                t = np.dot((a - origin), normal) / np.dot(normal, direction)
                if t < 0:
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
                        return 0
                    else:
                        dist = np.sqrt(np.sum(direction ** 2))
                        brightness = 1 / dist ** 2
                        return brightness
        return 0

    def bounce(self, collision_point: np.typing.NDArray, light: np.typing.NDArray, faces: np.typing.NDArray):
        self.direction = collision_point - light
        self.brightness = self.detect_collision(faces, self.direction, self.origin)

camera = Camera(np.array([0, 0, 10]))
camera.update_camera_plane(np.array([0, 0, 0]))

pyramid_faces = []

face1 = Face(np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]]))
face2 = Face(np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]]))
face3 = Face(np.array([[0, 0, 0], [0, 0, 1], [1, 0, 0]]))
face4 = Face(np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]]))
pyramid_faces.append(np.array([face1, face2, face3, face4]))
pyramid_faces = np.array(pyramid_faces)

pyramid = Shape(pyramid_faces)