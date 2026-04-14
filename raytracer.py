import numpy as np

class Ray:
    def __init__(self, brightness: int, origin: np.typing.NDArray, direction: np.typing.NDArray):
        self.brightness = brightness
        self.origin = origin
        self.direction = direction