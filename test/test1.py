import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.task import Task
from direct.showbase.DirectObject import DirectObject


# TO USE
#
# import hlview
# mouseControl=hlview.hlview()
# mouseControl.start()

# This is basically the drive mode with the ability to look up and down
# A version with keyboard navigation will be here too
# controls:
# Mouse looks around
# Left mouse button moves forward
# Middle mouse button toggles the control scheme
# Right mouse button moves backwards

class hlview(DirectObject):
    def __init__(self):
        self.m = MouseControls()
        base.enableMouse()
        # to allow mouse button navigation
        self.forward = False
        self.backward = False
        self.left = False
        self.right = False
        self.accept("q", self.toggle)
        self.running = False
        self.justHit = False
        self.speed = .1

    def setRunSpeed(self, speed):
        self.speed = speed

    def start(self):
        self.m.startMouse()
        base.disableMouse()
        par = camera.getParent()
        self.parent = par
        # Our base node that only holds position
        self.posNode = par.attachNewNode("PosNode")
        self.posNode.setPos(camera.getPos(par))
        # Two nodes that sits on posNode, and gives us directions
        self.forwardNode = camera.attachNewNode("forwardNode")
        self.forwardNode.setPos(0, .1, 0)
        self.rightNode = camera.attachNewNode("strafeNode")
        self.rightNode.setPos(.1, 0, 0)

        # Orient the camera on the posNode
        camera.setPos(0, 0, 0)
        camera.reparentTo(self.posNode)

        # Task for changing direction/position
        taskMgr.add(self.camTask, "hlview::camTask")
        self.accept("w", setattr, [self, "forward", True])
        self.accept("w-up", setattr, [self, "forward", False])
        self.accept("s", setattr, [self, "backward", True])
        self.accept("s-up", setattr, [self, "backward", False])
        self.accept("a", setattr, [self, "left", True])
        self.accept("a-up", setattr, [self, "left", False])
        self.accept("d", setattr, [self, "right", True])
        self.accept("d-up", setattr, [self, "right", False])
        self.accept("mouse1", setattr, [self, "justHit", True])
        self.running = True

        # call to stop control system

    def toggle(self):
        if (self.running):
            self.stop()
        else:
            self.start()

    # TODO: write a transform that allows for transition from hlview to
    # trackball. In the end, probably should never allow the two to meet
    def stop(self):
        taskMgr.remove("hlview::camTask")
        camera.reparentTo(self.parent)

        # problem spot, base keeps a last position to update from that we
        # need to change to the current pos
        # Unfortunately, transforming the position [i]and[/i] hpr such that
        # they conform to the trackball control scheme is no mean feat
        base.enableMouse()
        self.forward = False
        self.backward = False
        self.left = False
        self.right = False

        self.running = False
        self.m.stopMouse()
        self.ignore("w")
        self.ignore("w-up")
        self.ignore("s")
        self.ignore("s-up")
        self.ignore("a")
        self.ignore("a-up")
        self.ignore("d")
        self.ignore("d-up")
        self.ignore("mouse1")

    def camTask(self, task):
        # position change
        finalMove = Vec3(0, 0, 0)
        basePosition = self.posNode.getPos(self.parent)
        if (self.forward):
            # get derivative
            move = self.forwardNode.getPos(self.parent) - basePosition
            # and flatten it
            move.setZ(0)
            finalMove += move
        if (self.backward):
            # get derivative
            move = self.forwardNode.getPos(self.parent) - basePosition
            # and flatten it
            move.setZ(0)
            finalMove -= move
        if (self.left):
            # get derivative
            move = self.rightNode.getPos(self.parent) - basePosition
            # and flatten it
            move.setZ(0)
            finalMove -= move
        if (self.right):
            # get derivative
            move = self.rightNode.getPos(self.parent) - basePosition
            # and flatten it
            move.setZ(0)
            finalMove += move

        # The goal here is to make sure that pressing left and up doesn't
        # move you twice as fast
        finalMove.normalize()

        # TODO: make the change in position scaled by dt, as david suggests
        finalMove *= self.speed

        self.posNode.setPos(self.posNode.getPos() + finalMove)

        if (not self.justHit):
            x = -self.m.mouseChangeX * .2
            y = -self.m.mouseChangeY * .1
            # orientation change
            camera.setH(camera.getH() + x)
            camera.setP(camera.getP() + y)
        else:
            self.justHit = 0
        return Task.cont