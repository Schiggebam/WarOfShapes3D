from direct.filter.CommonFilters import CommonFilters
from panda3d.core import AmbientLight, DirectionalLight, Spotlight, LVector3, NodePath, LightRampAttrib, PandaNode


class WorldComposer:
    def __init__(self, render):
        self.render = render
        self.separation = .0

    def setup_world_lightning(self):
        """
        Sets up the ambient and specular lighting of the world
        :return:
        """
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((2, 2, 2, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setShadowCaster(True)
        directionalLight.setDirection(LVector3(-1, -1, -1))
        directionalLight.setColor((.5, .5, .5, 1))

        dir_light_node = self.render.attachNewNode(directionalLight)
        # dir_light_node.setPos(10, 2, 7)
        # dir_light_node.lookAt(2, 2, 0)
        self.render.setLight(dir_light_node)
        self.render.setLight(self.render.attachNewNode(ambientLight))
        spot = Spotlight("Spot")
        spot.setColorTemperature(9000)
        spot.setColor(LVector3(1, 1, 1))
        light = self.render.attachNewNode(spot)
        light.node().setScene(self.render)
        light.node().setShadowCaster(True)
        # light.node().showFrustum()
        light.node().getLens().setFov(40)
        light.node().getLens().setNearFar(2, 100)
        # light.setPos(10, 2, 7)
        light.setPos(10, 20, 20)
        light.lookAt(2, 2, 0)
        self.render.setLight(light)
        # plight = PointLight('plight')
        # plight.setColor((1, 1, 1, 1))
        # plight.setAttenuation(LVector3(0.7, 0.05, 0))
        #
        # plnp = self.render.attachNewNode(plight)
        # plnp.setPos(0, 0, 5)
        # self.render.setShaderAuto()

    def compose_filters(self, win, cam, seperation=.6):
        """
        function to handle the composing, which makes for the basic look and feel of the game
        also handles any filters which are attached to the cam
        :return:
        """
        # set up the lightramp effect
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.4))           # warning can be ignored..
        tempnode.setShaderAuto()
        cam.node().setInitialState(tempnode.getState())

        self.separation = seperation  # Pixels
        self.filters = CommonFilters(win, cam)
        filterok = self.filters.setCartoonInk(separation=self.separation)
        if (filterok == False):
            return