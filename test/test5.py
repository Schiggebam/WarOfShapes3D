from panda3d.core import *
from direct.showbase.ShowBase import ShowBase


def create_cube(vertex_format):

    vertex_data = GeomVertexData("cube_data", vertex_format, Geom.UH_static)
    tris_prim = GeomTriangles(Geom.UH_static)

    pos_writer = GeomVertexWriter(vertex_data, "vertex")
    normal_writer = GeomVertexWriter(vertex_data, "normal")
    color_writer = GeomVertexWriter(vertex_data, "color")
    uv_writer = GeomVertexWriter(vertex_data, "texcoord")

    vertex_count = 0
    # (left=purple, back=green, down=blue, right=red, front=yellow, up=white)
    colors = ((1., 0., 1.), (0., 1., 0.), (0., 0., 1.),
              (1., 0., 0.), (1., 1., 0.), (1., 1., 1.))

    for direction in (-1, 1):

        for i in range(3):

            normal = VBase3()
            normal[i] = direction
            r, g, b = colors[i if direction == -1 else i-3]
            color = (r, g, b, 1.)

            for a, b in ((-1., -1.), (-1., 1.), (1., 1.), (1., -1.)):

                pos = Point3()
                pos[i] = direction
                pos[(i + direction) % 3] = a
                pos[(i + direction * 2) % 3] = b
                uv = (max(0., a), max(0., b))

                pos_writer.add_data3(pos)
                normal_writer.add_data3(normal)
#                color_writer.add_data4(color)
                uv_writer.add_data2(uv)

            vertex_count += 4

            tris_prim.add_vertices(vertex_count - 2, vertex_count - 3, vertex_count - 4)
            tris_prim.add_vertices(vertex_count - 4, vertex_count - 1, vertex_count - 2)

    geom = Geom(vertex_data)
    geom.add_primitive(tris_prim)
    node = GeomNode("cube_node")
    node.add_geom(geom)

    return node


class MyApp(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        # set up a light source
        p_light = PointLight("point_light")
        p_light.set_color((1., 1., 1., 1.))
        self.light = self.camera.attach_new_node(p_light)
        self.light.set_pos(5., -10., 7.)
        self.render.set_light(self.light)
        self.render.set_shader_auto()

        # Define a vertex format that includes "tangent" and "binormal" columns

        array_format = GeomVertexArrayFormat()
        array_format.add_column(InternalName.make("vertex"), 3, Geom.NT_float32, Geom.C_point)
        array_format.add_column(InternalName.make("color"), 4, Geom.NT_uint8, Geom.C_color)
        array_format.add_column(InternalName.make("normal"), 3, Geom.NT_float32, Geom.C_normal)
        array_format.add_column(InternalName.make("tangent"), 3, Geom.NT_float32, Geom.C_vector)
        array_format.add_column(InternalName.make("binormal"), 3, Geom.NT_float32, Geom.C_vector)
        array_format.add_column(InternalName.make("texcoord"), 2, Geom.NT_float32, Geom.C_texcoord)

        vertex_format = GeomVertexFormat()
        vertex_format.add_array(array_format)
        vertex_format = GeomVertexFormat.register_format(vertex_format)

        # create a cube parented to the scene root
        cube_node = create_cube(vertex_format)
        cube = self.render.attach_new_node(cube_node)
        geom = cube.node().modify_geom(0)
        self.update_tangent_space(geom)
        tex = self.loader.load_texture("brick-c.jpg")
        cube.set_texture(tex)
        tex_stage = TextureStage("normal")
        tex_stage.set_mode(TextureStage.M_normal)
        tex = self.loader.load_texture("brick-n.jpg")
        cube.set_texture(tex_stage, tex)
#        cube.set_tex_rotate(TextureStage.get_default(), 180.)
#        cube.set_tex_rotate(tex_stage, 180.)

    def update_tangent_space(self, geom, flip_tangent=False, flip_bitangent=False):

        positions = []
        normals = []
        uvs = []
        vertex_data = geom.modify_vertex_data()
        pos_reader = GeomVertexReader(vertex_data, "vertex")
        normal_reader = GeomVertexReader(vertex_data, "normal")
        uv_reader = GeomVertexReader(vertex_data, "texcoord")
        tan_writer = GeomVertexWriter(vertex_data, "tangent")
        bitan_writer = GeomVertexWriter(vertex_data, "binormal")

        for _ in range(vertex_data.get_num_rows()):
            positions.append(pos_reader.get_data3())
            normals.append(normal_reader.get_data3())
            uvs.append(uv_reader.get_data2())

        prim = geom.get_primitive(0)
        verts = prim.get_vertex_list()
        triangles = [verts[n:n + 3] for n in range(0, len(verts), 3)]
        processed_verts = []
        epsilon = 1.e-010

        for rows in triangles:

            for row in rows:

                if row in processed_verts:
                    continue

                vert = verts[row]
                other_rows = list(rows)
                other_rows.remove(row)
                pos = positions[row]
                pos1, pos2 = [positions[r] for r in other_rows]
                pos_vec1 = pos1 - pos
                pos_vec2 = pos2 - pos
                uv = Point2(uvs[row])
                uv1, uv2 = [Point2(uvs[r]) for r in other_rows]
                uv_vec1 = uv1 - uv
                uv_vec2 = uv2 - uv

                # compute a vector pointing in the +U direction, in texture space
                # and in object space

                if abs(uv_vec1.y) < epsilon:
                    u_vec_tex = uv_vec1
                    u_vec_obj = Vec3(pos_vec1)
                elif abs(uv_vec2.y) < epsilon:
                    u_vec_tex = uv_vec2
                    u_vec_obj = Vec3(pos_vec2)
                else:
                    scale = (uv_vec1.y / uv_vec2.y)
                    u_vec_tex = uv_vec1 - uv_vec2 * scale
                    # u_vec_tex.y will be 0 and thus point in the -/+U direction;
                    # replacing the texture-space vectors with the corresponding
                    # object-space vectors will therefore yield an object-space U-vector
                    u_vec_obj = pos_vec1 - pos_vec2 * scale

                if u_vec_tex.x < 0.:
                    u_vec_obj *= -1.

                # compute a vector pointing in the +V direction, in texture space
                # and in object space

                if abs(uv_vec1.x) < epsilon:
                    v_vec_tex = uv_vec1
                    v_vec_obj = Vec3(pos_vec1)
                elif abs(uv_vec2.x) < epsilon:
                    v_vec_tex = uv_vec2
                    v_vec_obj = Vec3(pos_vec2)
                else:
                    scale = (uv_vec1.x / uv_vec2.x)
                    v_vec_tex = uv_vec1 - uv_vec2 * scale
                    # v_vec_tex.x will be 0 and thus point in the -/+V direction;
                    # replacing the texture-space vectors with the corresponding
                    # object-space vectors will therefore yield an object-space V-vector
                    v_vec_obj = pos_vec1 - pos_vec2 * scale

                if v_vec_tex.y < 0.:
                    v_vec_obj *= -1.

                normal = normals[row]
                tangent_plane = Plane(normal, Point3())
                # the tangent vector is the object-space U-vector projected onto
                # the tangent plane
                tangent = Vec3(tangent_plane.project(Point3(u_vec_obj)))

                if not tangent.normalize():
                    continue

                # the bitangent vector is the object-space V-vector projected onto
                # the tangent plane
                bitangent = Vec3(tangent_plane.project(Point3(v_vec_obj)))

                if not bitangent.normalize():
                    continue

                if flip_tangent:
                    tangent *= -1.

                if flip_bitangent:
                    bitangent *= -1.

                tan_writer.set_row(row)
                tan_writer.set_data3(tangent)
                bitan_writer.set_row(row)
                bitan_writer.set_data3(bitangent)
                processed_verts.append(row)


app = MyApp()
app.run()