from panda3d.core import TypedWritable


class GeoToBam:

    @staticmethod
    def geo_to_bam(geo: TypedWritable):
        return geo.encodeToBamStream()