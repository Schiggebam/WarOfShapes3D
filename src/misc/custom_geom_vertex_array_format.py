from enum import Enum

from panda3d.core import GeomVertexArrayFormat, Geom, InternalName, GeomVertexFormat, GeomVertexReader


class ArrayFormatColunm(Enum):
    """
    Enum representation of columns in the VertexArrayFormat
    """
    Vertex = "vertex"
    Color = "color"
    Normal = "normal"
    Tangent = "tangent"
    Binormal = "binormal"
    UVMap = "texcoords"


class MyGeomVertexArrayFormat:
    """
    Class which is supposed to extend the existing vertex array format of Panda3d
    Panda supports : vertex, color, normal and uv-coordinates natively.
    However, for normal (bump)-mapping, tangent and binormal vector for each vertex are required.
    Thus:
    vertex: Vertex in 3D space
    color: Color in 4D color space (rgb with alpha channel)
    normal: normal vector of vertex, e.g. required for smooth lightning
    tangent: tangent vector to the normal vector of the vertex. Required for normal(bump) mapping
    bi-normal: sometimes referred to as bi-tangent. Cross product of normal and tangent vector n_v x t_v
    texcoord: UV coordinates -> mapping of each vertex to a 2D [0,1]x[0,1] space

    """

    # noinspection PyArgumentList,PyCallByClass
    def __init__(self):
        array_format = GeomVertexArrayFormat()
        array_format.addColumn(InternalName.make(ArrayFormatColunm.Vertex.value), 3, Geom.NT_float32, Geom.C_point)
        array_format.addColumn(InternalName.make(ArrayFormatColunm.Color.value), 4, Geom.NT_uint8, Geom.C_color)
        array_format.addColumn(InternalName.make(ArrayFormatColunm.Normal.value), 3, Geom.NT_float32, Geom.C_normal)
        array_format.addColumn(InternalName.make(ArrayFormatColunm.Tangent.value), 3, Geom.NT_float32, Geom.C_vector)
        array_format.addColumn(InternalName.make(ArrayFormatColunm.Binormal.value), 3, Geom.NT_float32, Geom.C_vector)
        array_format.addColumn(InternalName.make(ArrayFormatColunm.UVMap.value), 2, Geom.NT_float32, Geom.C_texcoord)

        self.vertex_format = GeomVertexFormat()
        self.vertex_format.addArray(array_format)
        self.vertex_format = GeomVertexFormat.registerFormat(self.vertex_format)

    @staticmethod
    def get_column_name(column_name: ArrayFormatColunm) -> str:
        return column_name.value

    @staticmethod
    def get_writer(geom: Geom, column_name: ArrayFormatColunm) -> GeomVertexReader:
        vertex_data = geom.modifyVertexData()
        return GeomVertexReader(vertex_data, column_name.value)