from enum import Enum

from panda3d.core import NodePath, SamplerState, Texture, TextureStage


class TextureMode(Enum):
    """
    Enum, representing the texture which is applied to a hexagon
    """
    """Water Tile, Refinement level 1, basic"""
    TILE_TEX_WATER_BASIC = 0

    """Grass hill with stony texture on top, Refinement level 3, splatted"""
    TILE_TEX_HILL_STONY_SPL = 1

class WorldTexturer:
    def __init__(self, loader):
        self.loader = loader

        # load textures
        self.tile_tex_water_basic = self.__load_texture("textures/water_tex_1.png", mipmap=False, mirror=False)
        self.tile_tex_grass_basic = self.__load_texture("textures/grass_tex_1.png")
        self.tile_tex_sand_basic = self.__load_texture("textures/sand_tex_1.png")
        # load normal (bump) maps
        pass
        # load stencil maps for splatted textures
        self.tile_stencil_1 = self.__load_texture("textures/stencil_tex_1.png")


    def texture_tile(self, tile: NodePath, texture_mode: TextureMode):
        if texture_mode is TextureMode.TILE_TEX_WATER_BASIC:
            tile.setTexture(self.tile_tex_water_basic)
        elif texture_mode is TextureMode.TILE_TEX_HILL_STONY_SPL:
            first = self.tile_tex_sand_basic
            second = self.tile_tex_grass_basic
            stencil = self.tile_stencil_1
            self.apply_splatted_textures(tile, first, second, stencil)


    def apply_splatted_textures(self, tile: NodePath, first_tex, second_tex, stencil_tex):
        # first = self.load("textures/sand_tex_1.png")
        # second = self.load("textures/grass_tex_1.png")
        # third = self.load("textures/water_tex_1.png")
        # stencil = self.load("textures/stencil_tex_1.png")
        # stencil_2 = self.load("textures/stencil_tex_2.png")
        # # normal = self.load("textures/sea-normal.jpg")
        # normal = self.loader.load_texture("textures/layingrock-n.jpg")

        # Apply the first texture.
        ts1 = TextureStage("stage-first")
        ts1.setSort(0)
        ts1.setMode(TextureStage.MReplace)
        ts1.setSavedResult(True)
        tile.setTexture(ts1, first_tex)
        # Apply the second texture.
        ts2 = TextureStage("stage-second")
        ts2.setSort(1)
        ts2.setMode(TextureStage.MReplace)
        tile.setTexture(ts2, second_tex)
        ts3 = TextureStage("stage-stencil")
        ts3.setSort(2)
        ts3.setCombineRgb(TextureStage.CMInterpolate, TextureStage.CSPrevious,
                          TextureStage.COSrcColor, TextureStage.CSLastSavedResult,
                          TextureStage.COSrcColor, TextureStage.CSTexture,
                          TextureStage.COSrcColor)
        ts3.setSavedResult(True)
        tile.setTexture(ts3, stencil_tex)

        # ts4 = TextureStage("normal")
        # ts4.setSort(3)
        # ts4.setMode(TextureStage.MNormal)
        # map.setTexture(ts4, normal)

        # ts4 = TextureStage("stage-third")
        # ts4.setSort(3)
        # ts4.setMode(TextureStage.MReplace)
        # map.setTexture(ts4, third)
        # ts5 = TextureStage("stage-stencil-2")
        # ts5.setSort(4)
        # ts5.setCombineRgb(TextureStage.CMInterpolate, TextureStage.CSPrevious,
        #                   TextureStage.COSrcColor, TextureStage.CSLastSavedResult,
        #                   TextureStage.COSrcColor, TextureStage.CSTexture,
        #                   TextureStage.COSrcColor)
        # map.setTexture(ts5, stencil_2)

    def __load_texture(self, path, anisotropic=None, mipmap=None, mirror=None) -> Texture:
        """
        Load a texture and apply some rendering uv properties.
        """
        if anisotropic is None: anisotropic = 4
        if mipmap is None: mipmap = True
        if mirror is None: mirror = False

        texture = self.loader.loadTexture(path)
        texture.setAnisotropicDegree(anisotropic)
        if mipmap:
            texture.setMagfilter(SamplerState.FT_linear)
            texture.setMinfilter(SamplerState.FT_linear_mipmap_linear)
        if mirror:
            texture.setWrapU(Texture.WM_mirror)
            texture.setWrapV(Texture.WM_mirror)
        return texture