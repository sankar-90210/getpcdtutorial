import cv2
import numpy as np
from pathlib import Path

from .real_sense_depth import DepthCamera
from .utils import createPointCloudO3D

# Resolution
RESOLUTION_WIDTH, RESOLUTION_HEIGHT = 640, 480

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)


def main():
    camera = DepthCamera(RESOLUTION_WIDTH, RESOLUTION_HEIGHT)

    print("Press 'q' in the window to capture and exit.")

    try:
        while True:
            ret, depth_raw_frame, color_raw_frame = camera.get_raw_frame()
            if not ret:
                print("Unable to get a frame")
                continue

            # For display
            color_frame = np.asanyarray(color_raw_frame.get_data())
            cv2.imshow("Color Frame", color_frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                # Save raw images
                color_path = DATA_RAW_DIR / "frame_color.png"
                depth_path = DATA_RAW_DIR / "frame_depth.png"

                cv2.imwrite(str(color_path), color_frame)
                depth_image = np.asanyarray(depth_raw_frame.get_data())
                cv2.imwrite(str(depth_path), depth_image)

                print(f"Saved color frame to: {color_path}")
                print(f"Saved depth frame to: {depth_path}")

                # Create and save point cloud
                createPointCloudO3D(color_raw_frame, depth_raw_frame, filename="o3d.ply")

                break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
