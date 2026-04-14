import numpy as np

class Face:
    def __init__(self, vertices: np.typing.NDArray):
        self.vertices = vertices

class Ray:
    def __init__(self, brightness: int, origin: np.typing.NDArray, direction: np.typing.NDArray):
        self.brightness = brightness
        self.origin = origin
        self.direction = direction

    def bounce(self, collision_point: np.typing.NDArray, light: np.typing.NDArray, faces: np.typing.NDArray):
        self.direction = collision_point - light

        for face in faces:
            edge1 = face.vertices[1] - face.vertices[0]
            edge2 = face.vertices[2] - face.vertices[0]
            normal = np.linalg.cross(edge1, edge2)
            weight1 = 2
            weight2 = 5
            A = (face.vertices[0] + weight1 * (face.vertices[1] - face.vertices[0]) + weight2
                 * (face.vertices[2] - face.vertices[0]))

            if np.round(np.dot(normal, self.direction), 2) == 0:
                pass
            else:
                t = np.dot((A - self.origin), normal) / np.dot(normal, self.direction)
                if t < 0:
                    pass
                else:
                    intersection = self.origin + t * self.direction
                    v0 = face.vertices[1] - face.vertices[0]
                    v1 = face.vertices[2] - face.vertices[0]
                    v2 = intersection - face.vertices[0]

                    d00 = v0 @ v0
                    d01 = v0 @ v1
                    d11 = v1 @ v1
                    d20 = v2 @ v0
                    d21 = v2 @ v1

                    denom = d00 * d11 - d01 * d01
                    u = (d11 * d20 - d01 * d21) / denom
                    v = (d00 * d21 - d01 * d20) / denom

                    if u >= 0 and v >= 0 and (u + v) <= 1:
                        self.brightness = 0
                    else:
                        dist = np.sqrt(np.sum(self.direction ** 2))
                        self.brightness = 1 / dist ** 2