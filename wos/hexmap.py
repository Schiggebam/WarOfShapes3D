from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, Vec3, GeomNode

from main.hexagon import Hexagon


class HexMap:

    def __int__(self):
        print("do something")
        format = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('blub', format, Geom.UHDynamic)

        snode = GeomNode('map')
        for i in range(3):
            hexagon = Hexagon.get_geometry(vdata, offset=Vec3(i, 0, 0))
            snode.add_geom(hexagon)


        cube = render.attachNewNode(snode)
        cube.setTwoSided(True)


