import os
import sys
from os import path

from typing import List

from direct.directtools.DirectGeometry import LineNodePath
from panda3d.core import Geom, GeomVertexWriter, GeomNode, GeomVertexFormat, GeomVertexData, Vec4, \
    GeomTriangles, Notify
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties

from wos.primitive import HexagonCreator, Hexagon


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.camera.setPos(0, 0, 20)
        self.camera.setHpr(0, -90, 0)
        self.win.requestProperties(properties)
        print(path.dirname(path.abspath(__file__)))

    def setup(self):

        format = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('hexmap', format, Geom.UHStatic)
        # PointData.generate_point_data(vdata)
        hexagons: List[Hexagon] = HexagonCreator.make_4_hexagons()
        vertWriter = GeomVertexWriter(vdata, "vertex")
        normalWriter = GeomVertexWriter(vdata, "normal")
        colorWriter = GeomVertexWriter(vdata, "color")
        counter = 0
        for p in HexagonCreator.all_points:
            print(f"adding {p}")
            vertWriter.add_data3f(p)
            if counter > 0:
                colorWriter.addData4f(1.0, 1.0, 1.0, 1.0)
            else:
                colorWriter.addData4f(0, 1.0, 1.0, 1.0)
            p.setZ(p.getZ() * 1)
            p.normalize()
            normalWriter.addData3f(p)
            counter += 1
        mapGeom = Geom(vdata)

        self.print_vdata(vdata)

        for h in hexagons:
            t = GeomTriangles(Geom.UHStatic)
            t.add_vertex(0)
            t.add_vertex(1)
            t.add_vertex(2)
            h.triangles.append(t)

            t = GeomTriangles(Geom.UHStatic)
            t.add_vertex(0)
            t.add_vertex(2)
            t.add_vertex(3)
            h.triangles.append(t)

            t = GeomTriangles(Geom.UHStatic)
            t.add_vertex(0)
            t.add_vertex(3)
            t.add_vertex(4)
            h.triangles.append(t)

            t = GeomTriangles(Geom.UHStatic)
            t.addVertex(0)
            t.add_vertex(4)
            t.add_vertex(5)
            h.triangles.append(t)

            t = GeomTriangles(Geom.UHStatic)
            t.add_vertex(0)
            t.add_vertex(5)
            t.add_vertex(6)
            h.triangles.append(t)

            t = GeomTriangles(Geom.UHStatic)
            t.add_vertex(0)
            t.add_vertex(6)
            t.add_vertex(1)
            h.triangles.append(t)

        for h in hexagons:
            for t in h.triangles:
                mapGeom.addPrimitive(t)
        snode = GeomNode('node_map')
        snode.add_geom(mapGeom)

        # t1 = GeomTriangles(Geom.UHStatic)
        # t1.add_vertex(0)
        # t1.add_vertex(1)
        # t1.add_vertex(3)
        # mapGeom = Geom(vdata)
        # mapGeom.addPrimitive(t1)
        # snode = GeomNode('node_map')
        # grid = Grid.make_grid()
        # # hexagon1 = Hexagon.get_geometry(vdata, offset=Vec3(0, 0, 0))
        # # hexagon2 = Hexagon.get_geometry(vdata, offset=Vec3(0, 2, 0))
        # # hexagon3 = Hexagon.get_geometry(vdata, offset=Vec3(2, 0, 0))
        # snode.add_geom(mapGeom)
        # # snode.add_geom(hexagon2)
        # # snode.add_geom(hexagon3)
        map = render.attachNewNode(snode)
        map.setPos(0, 0, 0.2)
        # map.setRenderModeWireframe()
        map.setTwoSided(True)

    def print_vdata(self, vdata):
        ostream = Notify.out()
        vdata.write(ostream)
        # for i in range(vdata.get_num_rows()):
        #     print(vdata[i])


# class Hexagon:
#
#     @staticmethod
#     def get_geometry(vdata, offset=Vec3(0, 0, 0), direction=1):
#         numVertices = 6
#         circleGeom = Geom(vdata)
#
#         vertWriter = GeomVertexWriter(vdata, "vertex")
#         normalWriter = GeomVertexWriter(vdata, "normal")
#         colorWriter = GeomVertexWriter(vdata, "color")
#         uvWriter = GeomVertexWriter(vdata, "texcoord")
#         drawWriter = GeomVertexWriter(vdata, "drawFlag")
#
#         # make sure we start at the end of the GeomVertexData so we dont overwrite anything
#         # that might be there already
#         startRow = vdata.getNumRows()
#
#         vertWriter.setRow(startRow)
#         colorWriter.setRow(startRow)
#         uvWriter.setRow(startRow)
#         normalWriter.setRow(startRow)
#         drawWriter.setRow(startRow)
#
#         angle = 2 * math.pi / numVertices
#         currAngle = angle
#         center = offset
#         vertWriter.addData3f(center)
#         colorWriter.addData4f(0.0, 0.0, 0.0, 1.0)
#         center.normalize()
#         normalWriter.addData3f(center)
#
#         for i in range(numVertices):
#             position = Vec3(math.cos(currAngle) + offset.getX(), math.sin(currAngle) + offset.getY(), offset.getZ())
#             vertWriter.addData3f(position)
#             uvWriter.addData2f(position.getX() / 2.0 + 0.5, position.getY() / 2.0 + 0.5)
#             colorWriter.addData4f(1.0, 1.0, 1.0, 1.0)
#             position.setZ(position.getZ() * direction)
#             position.normalize()
#             normalWriter.addData3f(position)
#
#             # at default Opengl only draws "front faces" (all shapes whose vertices are arranged CCW). We
#             # need direction so we can specify which side we want to be the front face
#             currAngle += angle * direction
#
#         circle = GeomTrifans(Geom.UHStatic)
#         circle.addConsecutiveVertices(startRow, numVertices+1)
#         circle.closePrimitive()
#
#         circleGeom.addPrimitive(circle)
#
#         return circleGeom


class Grid:

    @staticmethod
    def make_grid():
        raws1unit = 20
        rawsfithunit = 100
        d = 0
        X1 = 10
        X2 = -10
        Y1 = 10
        Y2 = -10

        linesX = LineNodePath(render, 'quad', 2, Vec4(.3, .3, .3, .3))
        linesXX = LineNodePath(render, 'quad', 1, Vec4(.3, .3, .3, .3))
        axis = LineNodePath(render, 'axis', 4, Vec4(.2, .2, .2, .2))
        quad = LineNodePath(render, 'quad', 4, Vec4(.2, .2, .2, .2))

        x1 = (0, Y2, 0)
        x2 = (0, Y1, 0)

        x3 = (X2, 0, 0)
        x4 = (X1, 0, 0)

        axis.drawLines([[x1, x2], [x3, x4]])
        axis.create()

        # q1 = (X1, Y1, 0)
        # q2 = (X1, Y2, 0)
        #
        # q3 = (q2)
        # q4 = (X2, Y2, 0)
        #
        # q5 = (q4)
        # q6 = (X2, Y1, 0)
        #
        # q7 = (q6)
        # q8 = (X1, Y1, 0)
        #
        # quad.drawLines([[q1, q2], [q3, q4], [q5, q6], [q7, q8]])
        # quad.create()

        for l in range(raws1unit - 1):
            d += 1
            l1 = (X2 + d, Y1, 0)
            l2 = (X2 + d, Y2, 0)

            l3 = (X2, Y1 - d, 0)
            l4 = (X1, Y1 - d, 0)

            linesX.drawLines([[l1, l2], [l3, l4]])
        linesX.create()

        for l in range(rawsfithunit):
            d -= .2
            lx1 = (X2 + 1 + d, Y1, 0)
            lx2 = (X2 + 1 + d, Y2, 0)

            lx3 = (X2, Y1 - 1 - d, 0)
            lx4 = (X1, Y1 - 1 - d, 0)

            linesXX.drawLines([[lx1, lx2], [lx3, lx4]])
        linesXX.create()

def main():
    game = Game()
    game.setup()
    game.run()

if __name__ == "__main__":
    main()
