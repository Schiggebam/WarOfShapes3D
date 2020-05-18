from __future__ import annotations

from enum import Enum
from math import sqrt
from typing import List, Optional

from panda3d.core import Vec2, Vec3, GeomTriangles, Geom, GeomTristrips


class Orientation(Enum):
    North = 0
    NorthEast = 1
    East = 2
    SouthEast = 3
    South = 4
    SouthWest = 5
    West = 6
    NorthWest = 7

    @staticmethod
    def get_orient_from_normal_vec2(vec: Vec2) -> Optional[Orientation]:
        def close_by(val, tar) -> bool:
            return abs(val - tar) < 1E-4
        if close_by(vec.x, 0) and close_by(vec.y, 1):
            return Orientation.South
        elif close_by(vec.x, 0) and close_by(vec.y, -1):
            return Orientation.North
        elif close_by(vec.x, 1) and close_by(vec.y, 0):
            return Orientation.East
        elif close_by(vec.x, -1) and close_by(vec.y, 0):
            return Orientation.West
        elif close_by(vec.x, 0.5) and close_by(vec.y, sqrt(3)/2):
            return Orientation.SouthEast
        elif close_by(vec.x, 0.5) and close_by(vec.y, - sqrt(3)/2):
            return Orientation.NorthEast
        elif close_by(vec.x, -0.5) and close_by(vec.y, sqrt(3) / 2):
            return Orientation.SouthWest
        elif close_by(vec.x, -0.5) and close_by(vec.y, - sqrt(3) / 2):
            return Orientation.NorthWest
        else:
            print(f"ERROR {vec}")
            return None

    @staticmethod
    def get_opposite(orientation: Orientation) -> Orientation:
        return Orientation((orientation.value + 4) % 8)


class Hexagon:
    counter = 0

    def __init__(self, center: Vec3, width, height, x_grid, y_grid,
                 refinement_level=1, is_hill=True, map_style="pointy"):
        Hexagon.counter += 1
        self.vx_center: Vec3 = center
        self.refinement_level = refinement_level
        self.width = width
        self.height = height
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.adjacent_hexagons = []
        if map_style == "pointy":
            self.adjacent_hexagons = [Orientation.North, Orientation.NorthEast, Orientation.SouthEast,
                                      Orientation.South, Orientation.SouthWest, Orientation.NorthWest]
        # self.master_point_indices: List[int] = []
        # self.ref_points_indices: List[List[int]] = []
        self.triangulation: List[GeomTriangles] = []
        self.ref_points_indices: List[List[int]] = []
        self.connector_points_indices: List[int] = []
        from src.world.hexmap import MapPointMngr
        # print(f"ref level ({self.x_grid}|{self.y_grid}): {refinement_level}")

        # build up the vertices
        for i in range(refinement_level + 1):
            z_elevation = self.get_elevation(i)

            if i == 0:  # center point
                uv_map = self.get_uv_mapping(z_elevation, self.vx_center, None, i)
                idx = MapPointMngr.instance().add_critical_point((self.vx_center.x, self.vx_center.y, z_elevation),
                                                                 self.x_grid, self.y_grid, uv_map)
                self.ref_points_indices.append([idx])
                continue

            self.ref_points_indices.append([])
            fac = self.get_offset_factor(i)
            for o in self.adjacent_hexagons:
                p = self.get_vector(o, size=fac) + self.vx_center.xy
                n = self.get_normal(o, z_elevation)
                uv_map = self.get_uv_mapping(z_elevation, p, o, i)
                idx = MapPointMngr.instance().add_critical_point((p.x, p.y, z_elevation), self.x_grid, self.y_grid,
                                                                 uv_map, n=n)
                self.ref_points_indices[i].append(idx)

        # construct geometric triangulation
        # print(self.ref_points_indices)
        for i in range(refinement_level):
            if i == 0:
                for k in range(1, 7, 1):
                    t = GeomTriangles(Geom.UHStatic)

                    t.addVertex(self.ref_points_indices[i][0])
                    t.addVertex(self.ref_points_indices[i+1][k % 6])
                    t.addVertex(self.ref_points_indices[i+1][(k+1) % 6])
                    t.closePrimitive()
                    self.triangulation.append(t)
            else:
                t = GeomTristrips(Geom.UHStatic)
                for k in range(7):
                    t.addVertex(self.ref_points_indices[i][k % 6])
                    t.addVertex(self.ref_points_indices[i+1][k % 6])
                t.closePrimitive()
                # aat.decompose()
                self.triangulation.append(t)

    def get_vector(self, orientation: Orientation, size=1.0):
        if orientation is Orientation.North:
            return Vec2(0, - 0.5 * self.height) * size
        elif orientation is Orientation.NorthEast:
            return Vec2(0.5 * self.width, -0.25 * self.height) * size
        elif orientation is Orientation.SouthEast:
            return Vec2(0.5 * self.width, 0.25 * self.height) * size
        elif orientation is Orientation.South:
            return Vec2(0, 0.5 * self.height) * size
        elif orientation is Orientation.SouthWest:
            return Vec2(-0.5 * self.width, 0.25 * self.height) * size
        elif orientation is Orientation.NorthWest:
            return Vec2(-0.5 * self.width, -0.25 * self.height) * size

    def get_normal(self, orientation: Orientation, elevation):
        if self.refinement_level == 1 or elevation == 0:
            return Vec3(0, 0, 1)
        vec = None
        if orientation is Orientation.North:
            vec = Vec3(0, -1, 1)
        elif orientation is Orientation.NorthEast:
            vec = Vec3(1, -1, 1)
        elif orientation is Orientation.SouthEast:
            vec = Vec3(1, 1, 1)
        elif orientation is Orientation.South:
            vec = Vec3(0, 1, 1)
        elif orientation is Orientation.SouthWest:
            vec = Vec3(-1, 1, 1)
        elif orientation is Orientation.NorthWest:
            vec = Vec3(-1, -1, 1)
        else:
            print("ERROR")
        vec = vec.normalize()
        return vec

    def get_offset_factor(self, current_level):
        return 1 - (self.refinement_level - (current_level)) * 0.25

    def get_elevation(self, current_level):
        if self.refinement_level == 1:
            return .0
        elif self.refinement_level == 3 and current_level < 2:
            return .25
        elif self.refinement_level == 5:
            if 2 < current_level <= 4:
                return .25
            if current_level <= 2:
                return .5

        return .0

    def get_uv_mapping(self, elevation, vertex: Vec3, orientation, current_level):
        t = Vec2(.5, .5)
        fac = self.get_offset_factor(current_level)
        # t = Vec2(0.07, 0.50) if elevation > 0 else Vec2(0.07, 0.35)
        # fac =  0.03 if elevation > 0 else 0.06
        v = None
        if orientation:
            v = self.get_vector(orientation, size=.5)
        else:
            v = Vec2(0, 0)
        return (t + v * fac)

        # fac = 0.01 if elevation > 0 else 0.9
        # if orientation:
        #     v = self.get_vector(orientation)
        #     return v.xy * fac
        # else:
        #     v = Vec3(0, 0, 1)
        #     return v.xy * fac

        # if elevation > 0:
        #     #return vertex.xy * 0.01
        #
        #     return Vec2(1,1) * 0.01
        # else:
        #     #return vertex.xy * 0.01 + 0.9
        #     return Vec2(1,1) * 0.01 + 0.9

    def connect(self, other: Hexagon):
        from src.world.hexmap import MapPointMngr
        direction = self.vx_center - other.vx_center
        direction.normalize()
        print(f"Performing connection algorithm : dir {direction}")
        print(Orientation.get_orient_from_normal_vec2(direction))
        facing: Orientation = Orientation.get_orient_from_normal_vec2(direction)
        v1_orient = None
        v2_orient = None
        rotation = None
        a = 0

        if facing is Orientation.West:
            v1_orient = Orientation.NorthEast
            v2_orient = Orientation.SouthEast
            rotation = 0
            a = 0
        elif facing is Orientation.East:
            v1_orient = Orientation.NorthWest
            v2_orient = Orientation.SouthWest
            rotation = 3
            a = 1
        # elif facing is Orientation.NorthEast:
        #     v1_orient = Orientation.SouthWest
        #     v2_orient = Orientation.South
        #     rotation = 3
        #     a = 0
        # elif facing is Orientation.SouthWest:
        #     v1_orient = Orientation.North
        #     v2_orient = Orientation.NorthEast
        #     rotation = 3
        #     a = 1

        current_lvl = 3
        v1 = self.get_vector(v1_orient, size=self.get_offset_factor(current_lvl))
        v2 = self.get_vector(v2_orient, size=self.get_offset_factor(current_lvl))
        v1 = v1 + self.vx_center.xy
        v2 = v2 + self.vx_center.xy

        z_elevation = self.get_elevation(0)
        # v1
        uv_map = self.get_uv_mapping(z_elevation, v1, v1_orient, current_lvl)
        idx = MapPointMngr.instance().add_critical_point((v1.x, v1.y, z_elevation), self.x_grid, self.y_grid, uv_map)
        self.connector_points_indices.append(idx)
        # v2
        uv_map = self.get_uv_mapping(z_elevation, v2, v2_orient, current_lvl)
        idx = MapPointMngr.instance().add_critical_point((v2.x, v2.y, z_elevation), self.x_grid, self.y_grid, uv_map)
        self.connector_points_indices.append(idx)

        t = GeomTriangles(Geom.UHStatic)
        t.addVertex(self.connector_points_indices[a % 2])
        t.addVertex(self.ref_points_indices[1][1+rotation])
        t.addVertex(self.ref_points_indices[2][1+rotation])
        t.closePrimitive()
        self.triangulation.append(t)

        t = GeomTriangles(Geom.UHStatic)
        t.addVertex(self.connector_points_indices[a % 2])
        t.addVertex(self.ref_points_indices[1][2+rotation])
        t.addVertex(self.ref_points_indices[1][1+rotation])
        t.closePrimitive()
        self.triangulation.append(t)

        t = GeomTriangles(Geom.UHStatic)
        t.addVertex(self.connector_points_indices[(a+1) % 2])
        t.addVertex(self.ref_points_indices[2][2+rotation])
        t.addVertex(self.ref_points_indices[1][2+rotation])
        t.closePrimitive()
        self.triangulation.append(t)

        t = GeomTriangles(Geom.UHStatic)
        t.addVertex(self.connector_points_indices[a % 2])
        t.addVertex(self.connector_points_indices[(a+1) % 2])
        t.addVertex(self.ref_points_indices[1][2+rotation])
        t.closePrimitive()
        self.triangulation.append(t)

        t = GeomTriangles(Geom.UHStatic)
        t.addVertex(self.connector_points_indices[a % 2])
        t.addVertex(self.ref_points_indices[2][1+rotation])
        t.addVertex(self.ref_points_indices[3][1+rotation])
        t.closePrimitive()
        self.triangulation.append(t)

        t = GeomTriangles(Geom.UHStatic)
        t.addVertex(self.connector_points_indices[(a+1) % 2])
        t.addVertex(self.ref_points_indices[3][2+rotation])
        t.addVertex(self.ref_points_indices[2][2+rotation])
        t.closePrimitive()
        self.triangulation.append(t)

