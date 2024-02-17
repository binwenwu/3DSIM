import math
from base.type import RangeMode

class RangeConverter:
    @staticmethod
    def convert(value: float, mode_from: RangeMode, mode_to: RangeMode, bv_radius: float=0) -> float:
        if mode_from == RangeMode.DISTANCE_FROM_EYE_POINT and mode_to == RangeMode.PIXEL_SIZE_ON_SCREEN:
            if bv_radius != 0:
                return RangeConverter.distance_to_pixel(value)
            else:
                raise(Exception("bv_radiu is 0"))
        elif mode_from == RangeMode.PIXEL_SIZE_ON_SCREEN and mode_to == RangeMode.DISTANCE_FROM_EYE_POINT:
            if bv_radius !=0:
                return RangeConverter.pixel_to_distance(value)
            else:
                raise(Exception("bv_radiu is 0"))
        elif mode_from == RangeMode.DISTANCE_FROM_EYE_POINT and mode_to == RangeMode.GEOMETRIC_ERROR:
            return RangeConverter.distance_to_geometric_error(value)
        elif mode_from == RangeMode.GEOMETRIC_ERROR and mode_to == RangeMode.DISTANCE_FROM_EYE_POINT:
            return RangeConverter.geometric_error_to_distance(value)
        elif mode_from == RangeMode.PIXEL_SIZE_ON_SCREEN and mode_to == RangeMode.GEOMETRIC_ERROR:
            return RangeConverter.pixel_to_geometric_error(value)
        elif mode_from == RangeMode.GEOMETRIC_ERROR and mode_to == RangeMode.PIXEL_SIZE_ON_SCREEN:
            return RangeConverter.geometric_error_to_pixel(value)
        else:
            return value  # Return the input value if no conversion is needed

    @staticmethod
    def distance_to_pixel(distance: float, boundvolume_radius:float) -> float:
        fov = 45
        viewPortHeight = 1080
        return RangeConverter._distance_to_pixel_size(distance=distance, boundvolume_radius= boundvolume_radius, fov=fov, viewPortHeight=viewPortHeight)

    @staticmethod
    def pixel_to_distance(pixel: float, boundvolume_radius:float) -> float:
        fov = 45
        viewPortHeight = 1080
        return RangeConverter._pixel_size_to_distance(pixelSize=pixel, boundvolume_radius= boundvolume_radius, fov=fov, viewPortHeight=viewPortHeight)

    @staticmethod
    def distance_to_geometric_error(distance: float) -> float:
        """
        Notes:
            An empricial method that convert geometric_error to distance
            assumption: Screen height = 1080; maximumScreenSpaceError = 16
        """
        return distance*0.56291651245*16/936

    @staticmethod
    def geometric_error_to_distance(geometric_error: float) -> float:
        """
        Notes:
            An empricial method that convert geometric_error to distance
            assumption: Screen height = 1080; maximumScreenSpaceError = 16
        """
        return geometric_error*936/16/0.56291651245

    @staticmethod
    def pixel_to_geometric_error(pixel: float) -> float:
        # TODO: Implement pixel to geometric error conversion logic
        return pixel

    @staticmethod
    def geometric_error_to_pixel(geometric_error: float) -> float:
        # TODO: Implement geometric error to pixel conversion logic
        return geometric_error
    
    @staticmethod
    def _distance_to_pixel_size(distance: float, boundvolume_radius: float, fov: float, viewPortHeight: int):
            """
            Args:
                distance (float): The distance of viewpoint.
                fov (float): The vertical field of view angle in degrees.
                viewPortHeight (int): The height of the viewport in pixels.
                
                1080p -> fov = 45, viewport_height = 1080
                2160p -> fov = 60, viewport_height = 2160
                720p -> fov = 45, viewport_height = 720
            Return:
                PIXEL_SIZE_ON_SCREEN
            Notes:
              Refer to the OpenSceneGraph source codes
            """
            angularSize = math.degrees(2.0 * math.atan(boundvolume_radius/distance))
            dpp = max(fov, 1.0e-17) / viewPortHeight 
            pixelSize = angularSize / dpp
            return pixelSize
    
    @staticmethod
    def _pixel_size_to_distance(pixelSize: float, boundvolume_radius: float, fov: float, viewPortHeight: int):
            """
            Args:
                distance (float): The distance of viewpoint.
                fov (float): The vertical field of view angle in degrees.
                viewPortHeight (int): The height of the viewport in pixels.
                
                1080p -> fov = 45, viewport_height = 1080
                2160p -> fov = 60, viewport_height = 2160
                720p -> fov = 45, viewport_height = 720
            Return:
                DISTANCE_FROM_EYE_POINT
            """
            dpp = max(fov, 1.0e-17) / viewPortHeight 
            distance = math.tan(math.radians(pixelSize*dpp)/2)*boundvolume_radius
            return distance