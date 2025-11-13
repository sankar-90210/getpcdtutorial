#Visualize point cloud using Open3D
from .utils import loadPointCloud

def main():
    # Loads data/processed/pointcloud/o3d.ply and shows it
    loadPointCloud("o3d.ply", visualize=True)


if __name__ == "__main__":
    main()
