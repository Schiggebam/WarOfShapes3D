from panda3d.core import *
from direct.showbase.ShowBase import ShowBase


class MyApp(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        # set up a light source
        p_light = PointLight("point_light")
        p_light.set_color((1., 1., 1., 1.))
        self.light = self.camera.attach_new_node(p_light)
        self.light.set_pos(5., -10., 7.)
        self.render.set_light(self.light)

        vertex_format = GeomVertexFormat.get_v3n3()
        vertex_data = GeomVertexData("triangle_data", vertex_format, Geom.UH_static)
        pos_writer = GeomVertexWriter(vertex_data, "vertex")
        normal_writer = GeomVertexWriter(vertex_data, "normal")
        # the following three points are listed in counter-clockwise order when
        # looking at the resulting triangle, in the direction of the positive Y-axis
        p1 = Point3(-1., 0., -.5)
        p2 = Point3(1., 0., -.5)
        p3 = Point3(0., 0., .5)
        pos_writer.add_data3(p1)
        pos_writer.add_data3(p2)
        pos_writer.add_data3(p3)
        v1 = p2 - p1  # vector pointing from p1 to p2
        v2 = p3 - p2  # vector pointing from p2 to p3
#        v3 = p1 - p3  # vector pointing from p3 to p1
        # the normal can be computed as the cross product of two out of the
        # above three side vectors:
        # v1 cross v2, v2 cross v3 or v3 cross v1
        normal = v1.cross(v2).normalized()
        # an easier alternative would be using a Plane, whose normal is equally
        # determined by that same winding order:
#        plane = Plane(p1, p2, p3)
#        normal = plane.get_normal()

        for _ in range(3):
            normal_writer.add_data3(normal)

        tris = GeomTriangles(Geom.UH_static)s
        # add the vertex indices in the same counter-clockwise order as above
        tris.add_vertices(0, 1, 2)
        geom = Geom(vertex_data)
        geom.add_primitive(tris)
        geom_node = GeomNode("triangle")
        geom_node.add_geom(geom)
        self.triangle = self.render.attach_new_node(geom_node)


app = MyApp()
app.run()