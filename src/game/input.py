
from direct.showbase.ShowBase import ShowBase

class MouseInput:
    pass

class CameraHandler:
    def __init__(self, base: ShowBase, camera):
        self.base = base
        self.camera = camera

        self.camera_x = 5
        self.camera_y = -7
        self.camera_z = 10

        self.__set_camera_pos()
        self.camera.setHpr(0, -30, 0)
        self.is_close_up = False

    def setup_cam_keys(self):
        self.base.accept('w', self.move_camera_up)
        self.base.accept('w-repeat', self.move_camera_up)
        self.base.accept('s', self.move_camera_down)
        self.base.accept('s-repeat', self.move_camera_down)
        self.base.accept('a', self.move_camera_left)
        self.base.accept('a-repeat', self.move_camera_left)
        self.base.accept('d', self.move_camera_right)
        self.base.accept('d-repeat', self.move_camera_right)
        self.base.accept('space', self.close_up)

    def move_camera_up(self):
        self.camera_y += 1
        self.__set_camera_pos()

    def move_camera_down(self):
        self.camera_y -= 1
        self.__set_camera_pos()

    def move_camera_left(self):
        self.camera_x -= 1
        self.__set_camera_pos()

    def move_camera_right(self):
        self.camera_x += 1
        self.__set_camera_pos()

    def close_up(self):
        self.is_close_up = not self.is_close_up
        if self.is_close_up:
            self.camera.setPos(2, 2, 20)
            self.camera.setHpr(0, -90, 0)
        else:
            self.__set_camera_pos()
            self.camera.setHpr(0, -45, 0)

    def __set_camera_pos(self):
        self.camera.setPos(self.camera_x, self.camera_y, self.camera_z)