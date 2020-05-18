from dataclasses import dataclass
from math import sqrt, ceil
from typing import Tuple, Dict, List

from panda3d.core import GeomNode, GeomVertexFormat, GeomVertexData, Geom, GeomVertexWriter, Vec3, Vec2, Notify

from src.misc.singleton import Singleton
from src.world.hexagon import Hexagon

TOL = 1e-5


@Singleton
class MapPointMngr:
    def __init__(self):
        # self.point_cloud: List[Tuple[Tuple[float, float, float], int]] = []
        self.v_data = None
        self.vert_writer = None
        self.color_writer = None
        self.uv_writer = None
        self.normal_writer = None
        self.draw_writer = None
        self.map_dim = (0, 0)
        self.crit_points_per_hex: List[List[Tuple[Tuple[float, float, float], int]]] = []

    def set_v_data(self, v_data):
        self.v_data = v_data
        self.vert_writer = GeomVertexWriter(self.v_data, "vertex")
        self.color_writer = GeomVertexWriter(self.v_data, "color")
        self.uv_writer = GeomVertexWriter(self.v_data, "texcoord")
        self.normal_writer = GeomVertexWriter(self.v_data, "normal")
        self.draw_writer = GeomVertexWriter(self.v_data, "drawFlag")

    def set_map_dim(self, map_dim: Tuple[int, int]):
        self.map_dim = map_dim

    def add_non_critical_point(self, p: Tuple[float, float, float], hex_x_grid: int, hex_y_grid: int,
                               uv_map: Vec2, n=Vec3(.0, .0, 1.0)) -> int:
        if not self.v_data:
            return -1
        lin_idx = self.linearize(hex_x_grid, hex_y_grid)
        if len(self.crit_points_per_hex) <= lin_idx:
            print("ERROR - can add non critical points only to a existing hexagon ..")
            return -1
        points_hex = self.crit_points_per_hex[lin_idx]
        idx = self.__add_point_to_vdata(p, n, uv_map)
        points_hex.append((p, idx))
        return idx

    def add_critical_point(self, p: Tuple[float, float, float], hex_x_grid: int, hex_y_grid: int,
                           uv_map: Vec2, n=Vec3(.0, .0, 1.0)) -> int:
        if not self.v_data:
            return -1

        lin_idx = self.linearize(hex_x_grid, hex_y_grid)
        if len(self.crit_points_per_hex) == lin_idx:
            # print(f"add center point: {p}")
            # new hexagon and point is a center-point (cannot exist already)
            self.crit_points_per_hex.append([])
            idx = self.__add_point_to_vdata(p, n, uv_map)
            self.crit_points_per_hex[lin_idx].append((p, idx))
            return idx
        else:
            # print(f"add non-center point {p}")
            # existing hexagon - 3 neighbouring hexagons possible
            # if hex_x_grid > 0:
            #     points_west = self.crit_points_per_hex[self.linearize(hex_x_grid-1, hex_y_grid)]
            #     for nei, idx in points_west:
            #         if self.close_enough(p, nei):
            #             return idx
            # if hex_y_grid > 0:
            #     points_south_west = self.crit_points_per_hex[self.linearize(hex_x_grid, hex_y_grid - 1)]
            #     for nei, idx in points_south_west:
            #         if self.close_enough(p, nei):
            #             return idx
            #     points_south_east = self.crit_points_per_hex[self.linearize(hex_x_grid+1, hex_y_grid - 1)]
            #     for nei, idx in points_south_east:
            #         if self.close_enough(p, nei):
            #             return idx
            idx = self.__add_point_to_vdata(p, n, uv_map)
            self.crit_points_per_hex[lin_idx].append((p, idx))
            return idx

        # for vec, idx in self.point_cloud:
        #     if abs(vec[0] - p[0]) < TOL and abs(vec[1] - p[1]) < TOL and abs(vec[2] - p[2]) < TOL:
        #         # print(f"point reused at {vec} -> ({p})")
        #         return idx

        # print(f"new point at {p}")

    def __add_point_to_vdata(self, p, n, uv_map) -> int:
        new_idx = self.v_data.getNumRows()
        self.vert_writer.setRow(new_idx)
        self.color_writer.setRow(new_idx)
        self.uv_writer.setRow(new_idx)
        self.draw_writer.setRow(new_idx)
        self.normal_writer.setRow(new_idx)
        position = Vec3(p[0], p[1], p[2])
        self.vert_writer.addData3f(position)
        self.color_writer.addData4f(.3, .3, .3, 1.0)
        self.normal_writer.addData3f(n)
        self.uv_writer.addData2f(uv_map[0], uv_map[1])  # not sure here
        return new_idx

    def linearize(self, x, y):
        return y * self.map_dim[0] + x

    def close_enough(self, p, other):
        return abs(other[0] - p[0]) < TOL and abs(other[1] - p[1]) < TOL and abs(other[2] - p[2]) < TOL


class HexMap:
    chunksize_x = 5

    def __init__(self, node: GeomNode, node_sea: GeomNode, map_dim: Tuple[int, int]):
        # self.v_data = GeomVertexData('hexmap', GeomVertexFormat.getV3n3cpt2(), Geom.UHStatic)
        self.map_point_mngr = MapPointMngr.instance()
        # self.map_point_mngr.set_v_data(self.v_data)
        self.map_point_mngr.set_map_dim(map_dim)
        self.map_dim = map_dim
        self.map: List[List[Hexagon]] = []
        self.hex_rad = 1
        self.hex_width = sqrt(3) * self.hex_rad
        self.hex_height = 2 * self.hex_rad
        self.geometries_v_data = []
        self.nodes = []

        self.connectable = []

        chunk = -1
        for j in range(self.map_dim[1]):
            for i in range(self.map_dim[0]):
                if i % HexMap.chunksize_x == 0:
                    chunk += 1
                    v = GeomVertexData('hexmap', GeomVertexFormat.getV3n3cpt2(), Geom.UHStatic)
                    self.geometries_v_data.append(v)
                    self.map_point_mngr.set_v_data(v)
                    self.map.append([])
                x_center = i * self.hex_width + (j & 1) * self.hex_width / 2
                y_center = j * self.hex_height * 3 / 4
                ref_lvl = 3 if (i > 0 and i < self.map_dim[0] - 1) and (j > 0 and j < self.map_dim[1] - 1) else 1
                # ref_lvl = 5
                center = Vec3(x_center, y_center, 0)
                h = Hexagon(center, self.hex_width, self.hex_height, i, j, refinement_level=ref_lvl)
                if ref_lvl > 1:
                    self.connectable.append(h)
                self.map[chunk].append(h)

        self.map_point_mngr.set_v_data(self.geometries_v_data[1])
        self.connectable[0].connect(self.connectable[1])
        self.connectable[1].connect(self.connectable[0])

        self.geometries = []
        for j in range(self.map_dim[1]):
            for c in range(ceil(self.map_dim[0] / HexMap.chunksize_x)):
                idx = c + j * ceil(self.map_dim[0] / HexMap.chunksize_x)
                g = Geom(self.geometries_v_data[idx])
                self.geometries.append(g)
                for hexagon in self.map[idx]:
                    for triangle in hexagon.triangulation:
                        g.addPrimitive(triangle)
                if j == 0 or j == self.map_dim[1] - 1:
                    node_sea.addGeom(g)
                else:
                    node.addGeom(g)

        print(f"Node has {node.getNumGeoms()} geos")

