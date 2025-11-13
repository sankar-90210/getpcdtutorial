import pyrealsense2 as rs
import numpy as np

class DepthCamera:
    """
    Wrapper around Intel RealSense D435 providing aligned depth + color frames.
    """

    def __init__(self, resolution_width: int, resolution_height: int):
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Resolve the pipeline to get the device
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()

        depth_sensor = device.first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        # Align depth to color
        align_to = rs.stream.color
        self.align = rs.align(align_to)

        device_product_line = str(device.get_info(rs.camera_info.product_line))
        print("Device product line:", device_product_line)

        # Streams
        config.enable_stream(
            rs.stream.depth,
            resolution_width,
            resolution_height,
            rs.format.z16,
            6,  # depth FPS
        )
        config.enable_stream(
            rs.stream.color,
            resolution_width,
            resolution_height,
            rs.format.bgr8,
            30,  # color FPS
        )

        # Start streaming
        self.pipeline.start(config)

    def get_frame(self):
        """
        Returns aligned depth and color as numpy arrays.
        """
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return False, None, None

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        return True, depth_image, color_image

    def get_raw_frame(self):
        """
        Returns aligned depth and color *raw rs.frame objects*.
        Useful when you need intrinsics from frame.profile.
        """
        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            return False, None, None

        return True, depth_frame, color_frame

    def get_depth_scale(self) -> float:
        """
        Conversion from depth units to meters.
        """
        return self.depth_scale

    def release(self):
        """
        Stop the pipeline.
        """
        self.pipeline.stop()
