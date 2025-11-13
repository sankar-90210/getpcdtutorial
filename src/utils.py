import numpy as np
import open3d as o3d
from pathlib import Path

# Project paths (root is one level above this file: .../getpcdtutorial)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "pointcloud"
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def get_intrinsic_matrix(frame, imwidth: int, imheight: int):
    """
    Build an Open3D PinholeCameraIntrinsic from a RealSense color frame.
    """
    intrinsics = frame.profile.as_video_stream_profile().intrinsics
    out = o3d.camera.PinholeCameraIntrinsic(
        imwidth,
        imheight,
        intrinsics.fx,
        intrinsics.fy,
        intrinsics.ppx,
        intrinsics.ppy,
    )
    return out


def createPointCloudO3D(color_frame, depth_frame, filename: str = "o3d.ply"):
    """
    Create an Open3D point cloud from aligned RealSense color/depth *raw frames*
    and save it as a PLY file in data/processed/pointcloud/.

    Returns:
        o3d.geometry.PointCloud
    """
    color_np = np.asanyarray(color_frame.get_data())
    imheight, imwidth, channel = color_np.shape  # note: Open3D expects (width, height)
    color_image = o3d.geometry.Image(color_np)

    depth_image = o3d.geometry.Image(np.asanyarray(depth_frame.get_data()))

    # convert_rgb_to_intensity=False would give colored pointcloud
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_image,
        depth_image,
        convert_rgb_to_intensity=True,
    )

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd_image, get_intrinsic_matrix(color_frame, imwidth, imheight)
    )

    # Flip so it's not upside-down
    pcd.transform([[1, 0, 0, 0],
                   [0, -1, 0, 0],
                   [0, 0, -1, 0],
                   [0, 0, 0, 1]])

    # Normals
    pcd.estimate_normals()

    # Save PLY
    ply_path = DATA_PROCESSED_DIR / filename
    o3d.io.write_point_cloud(str(ply_path), pcd)
    print(f"Saved point cloud to: {ply_path}")

    return pcd


def loadPointCloud(filename: str = "o3d.ply", visualize: bool = True):
    """
    Load a PLY from data/processed/pointcloud and optionally visualize it.
    """
    ply_path = DATA_PROCESSED_DIR / filename
    if not ply_path.exists():
        raise FileNotFoundError(f"Point cloud not found: {ply_path}")

    pcd = o3d.io.read_point_cloud(str(ply_path))
    if visualize:
        o3d.visualization.draw_geometries([pcd])
    return pcd
