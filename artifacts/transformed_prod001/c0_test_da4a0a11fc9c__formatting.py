from fiona import FionaWarning, Error, Collection
from pyproj import CRS, Transformer
from osgeo import osr


class MyGeometeryClass:
    def __init__(self):
        self.geometry = None

    def set_geometry(self, geometry):
        self.geometry = geometry

    def reproject_spatial_reference(self, spatial_reference, transformation_name=None):
        spatial_ref_os = osr.SpatialReference()
        if isinstance(spatial_reference, CRS) or isinstance(spatial_reference, str):
            transformation_name = transformation_name or None
            if isinstance(spatial_reference, str):
                spatial_ref_os.ImportFromProj4(spatial_reference)
            else:
                spatial_ref_os.ImportFromEPSG(spatial_reference.to_epsg())

                self.set_geometry(spatial_ref_os.ExportToWkt())
                return True

        elif isinstance(spatial_reference, SpatialReference):
            self.set_geometry(spatial_reference.ExportToWkt())
            return True

        else:
            self.set_geometry(None)
            return True
