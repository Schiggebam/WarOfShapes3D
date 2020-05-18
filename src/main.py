import timeit
from typing import Optional

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, GeomNode, TextNode

from src.game.input import CameraHandler
from src.world.compose_world import WorldComposer
from src.world.hexmap import HexMap
from src.world.texture_world import WorldTexturer, TextureMode


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        properties = WindowProperties()
        properties.setSize(1000, 750)

        self.disableMouse()
        self.hex_map: Optional[HexMap] = None
        self.world_texturer: WorldTexturer = WorldTexturer(self.loader)
        self.world_composer: WorldComposer = WorldComposer(self.render)
        self.camera_handler: CameraHandler = CameraHandler(self, self.camera)

        self.shaderenable = 1
        self.inst5 = self.addInstructions(0.30, "Enter: Turn bump maps Off")

    def setup(self):
        self.camera_handler.setup_cam_keys()
        node_world = GeomNode('node_map')
        node_sea = GeomNode('node_map')
        t1 = timeit.default_timer()
        self.hex_map = HexMap(node_world, node_sea, (4, 3))
        print(f"Map creation took : {timeit.default_timer() - t1}")
        # nodes = self.hex_map.nodes
        # complete_map_node = GeomNode("map")
        # for node in nodes:
        #     complete_map_node.addChild(node)
        map = self.render.attachNewNode(node_world)
        sea = self.render.attachNewNode(node_sea)

        self.world_texturer.texture_tile(map, TextureMode.TILE_TEX_HILL_STONY_SPL)
        self.world_texturer.texture_tile(sea, TextureMode.TILE_TEX_WATER_BASIC)

        # map.flattenStrong()
        # map.setRenderModeWireframe()
        map.setPos(0, 0, 0.2)
        sea.setPos(0, 0, 0.2)
        # map.setTwoSided(True)

        self.accept("enter", self.toggleShader)

        print(f"shader support: {self.shaderSupported()}")

        self.world_composer.compose_filters(self.win, self.cam)
        self.world_composer.setup_world_lightning()
        self.setBackgroundColor(0, 0, 0.2, 0)

        self.show_debug_on_screen(True)

        self.camLens.setNearFar(1.0, 100)
        # self.camLens.setFov(75)

        self.render.setShaderAuto()

    def shaderSupported(self):
        return self.win.getGsg().getSupportsBasicShaders() and \
               self.win.getGsg().getSupportsDepthTexture() and \
               self.win.getGsg().getSupportsShadowFilter()

    def show_debug_on_screen(self, flag: bool):
        self.setFrameRateMeter(True)

    def addInstructions(self, pos, msg):
        return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                            shadow=(0, 0, 0, 1), parent=self.a2dTopLeft,
                            pos=(0.08, -pos - 0.04), align=TextNode.ALeft)

    def toggleShader(self):
        self.inst5.destroy()
        if (self.shaderenable):
            self.inst5 = self.addInstructions(0.30, "Enter: Turn bump maps On")
            self.shaderenable = 0
            self.render.setShaderOff()
        else:
            self.inst5 = self.addInstructions(0.30, "Enter: Turn bump maps Off")
            self.shaderenable = 1
            self.render.setShaderAuto()

def main():
    game = Game()
    game.setup()
    game.run()

if __name__ == "__main__":
    main()
