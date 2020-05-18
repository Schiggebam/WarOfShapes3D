from typing import Set, List

from panda3d.core import GeomVertexData, Vec3, GeomVertexWriter, GeomTriangles


class Hexagon:
    def __init__(self):
        self.vertices = []
        self.triangles: List[GeomTriangles] = []


class HexagonCreator:
    all_points: List[Vec3] = []
    @staticmethod
    def get_hexagon(center_point: Vec3):
        matrix = [[0, 2, 0], [1, 1, 0], [1, -1, 0],
                  [0, -2, 0], [-1, -1, 0], [-1, 1, 0]]
        points = [center_point]
        for m in matrix:
            points.append(Vec3(center_point.getX() + m[0], center_point.getY() + m[1], center_point.getZ() + m[2]))
        # hexagon = Hexagon(points[1], points[2], points[3], points[4], points[5], points[6], points[7])
        return points

    @staticmethod
    def make_4_hexagons():
        center_points = []
        hexagons = []
        center_points.append(Vec3(0, 0, 0))
        # center_points.append(Vec3(2, 0, 0))
        # center_points.append(Vec3(0, 2, 0))
        # center_points.append(Vec3(2, 2, 0))

        for cp in center_points:
            points = HexagonCreator.get_hexagon(cp)
            hexagon = Hexagon()
            for p in points:
                if p not in HexagonCreator.all_points:
                    HexagonCreator.all_points.append(p)
                    hexagon.vertices.append(p)
                else:
                    for existing_p in HexagonCreator.all_points:
                        if existing_p.getX() == p.getX() and existing_p.getY() == p.getY() and existing_p.getZ() == p.getZ():
                            hexagon.vertices.append(existing_p)
                            break
                    else:
                        print("error")
            hexagons.append(hexagon)

        return hexagons



class PointData:

    @staticmethod
    def generate_point_data(vdata: GeomVertexData):
        vertWriter = GeomVertexWriter(vdata, "vertex")
        normalWriter = GeomVertexWriter(vdata, "normal")
        colorWriter = GeomVertexWriter(vdata, "color")
        # uvWriter = GeomVertexWriter(vdata, "texcoord")
        # drawWriter = GeomVertexWriter(vdata, "drawFlag")

        for i in range(3):
            for j in range(3):
                position = Vec3(float(i), float(j), 0)
                vertWriter.add_data3f(position)
                colorWriter.addData4f(1.0, 1.0, 1.0, 1.0)
                position.setZ(position.getZ() * 1)
                position.normalize()
                normalWriter.addData3f(position)

