from PIL import Image

size = 256
img = Image.new("RGB", (size,size), "white") # create a new 15x15 image
pixels = img.load() # create the pixel map

black_2 = []
for i in range(img.size[0]):
    if i % 2 == 0:
        black_2.append(i)

black_1 = [i-1 for i in black_2 if i > 0]
if img.size[0] % 2 == 0:
    black_1.append(img.size[0]-1)


for i in black_1:
    for j in range(0, size, 2):
        pixels[i,j] = (0,0,0)

for k in black_2:
    for l in range(1, size+1, 2):
        pixels[k,l] = (0,0,0)

img.save("img1.png")


from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

vertecies = [Vec3(1,0,1), Vec3(-1,0,1), Vec3(-1, 0, -1), Vec3(1,0,-1)]
texcoords = [Vec2(1, 1), Vec2(0, 1), Vec2(0,0), Vec2(1,0)]

class App (ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        format = GeomVertexFormat.getV3t2()
        g = GeomVertexData("box", format, Geom.UHStatic)
        vertex_w = GeomVertexWriter(g, "vertex")
        uv_w = GeomVertexWriter(g, "texcoord")
        for pos, tex in zip(vertecies, texcoords):
            vertex_w.add_data3f(pos)
            uv_w.add_data2f(tex)
        triangles = GeomTriangles(Geom.UHStatic)
        triangles.addVertices(0, 1, 2)
        triangles.closePrimitive()
        triangles.addVertices(2, 3, 0)
        triangles.closePrimitive()
        geom = Geom(g)
        geom.addPrimitive(triangles)
        node = GeomNode("box")
        node.addGeom(geom)
        box = self.render.attachNewNode(node)
        texture = self.loader.loadTexture("img1.png")
        box.setTexture(texture)
        self.cam.setPos(0, -5, 0)

app = App()
app.run()