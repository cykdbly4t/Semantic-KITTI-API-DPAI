# API for SemanticKITTI

This repository contains original Semantic-KITTI API files, with modified changes to [laserscan.py](auxiliary/laserscan.py), and new scripts ([class_counts.py](class_counts.py), [intensity_curves.py](intensity_curves.py), [iou_check.py](iou_check.py)) that will help aid in better statistic visualization and detection of falsely annotated points. 

- Link to original [Semantic-KITTI API](https://github.com/PRBonn/semantic-kitti-api/tree/master)

## Data organization

The data is organized in the following format:

```
/kitti/dataset/
          └── sequences/
          │       ├── 00/
          │       │   ├── poses.txt
          │       │   ├── image_2/
          │       │   ├── image_3/
          │       │   ├── labels/
          │       │   │     ├ 000000.label
          │       │   │     └ 000001.label
          │       |   ├── voxels/
          │       |   |     ├ 000000.bin
          │       |   |     ├ 000000.label
          │       |   |     ├ 000000.occluded
          │       |   |     ├ 000000.invalid
          │       |   |     ├ 000001.bin
          │       |   |     ├ 000001.label
          │       |   |     ├ 000001.occluded
          │       |   |     ├ 000001.invalid
          │       │   └── velodyne/
          │       │         ├ 000000.bin
          │       │         └ 000001.bin
          │       ├── 01/
          │       ├── 02/
          │       .
          │       .
          │       .
          │       └── 21/
          │
          └── stats/
                  ├── Semantic-KITTI-API-DPAI/

```

## Scripts:

**ALL OF THE SCRIPTS CAN BE INVOKED WITH THE --help (-h) FLAG, FOR EXTRA INFORMATION AND OPTIONS.**

The scripts that we will go through in the README file would only be the modified 
files from the original Semantic-KITTI API repository. Further information can be
found at [Semantic-KITTI API](https://github.com/PRBonn/semantic-kitti-api/tree/master).

#### Statistics


##### Points Distribution By Class

The algorithm for calculating the distribution of points by class in each sequence
already exists in [content.py](content.py). This script returns the results in the
terminal. [class_counts.py](class_counts.py) returns the values of all the sequences in a CSV file instead,
together with the name of the classes as a reference.

```sh
$ ./class_counts.py --dataset /path/to/kitti/dataset/ --labels /path/to/config/file/
```
Where the config file is [semantic-kitti.yaml](config/semantic-kitti.yaml).

#### Visualization 


##### Point Clouds

To visualize the data, use the `visualize.py` script. It will open an interactive
opengl visualization of the pointclouds along with a spherical projection of
each scan into a 64 x 1024 image. In this version of the 'visualize.py' script,
the point clouds that are visualized will only be point clouds within 20-metre range
of the LiDAR origin.

```sh
$ ./visualize.py --sequence 00 --dataset /path/to/kitti/dataset/
```

where:
- `sequence` is the sequence to be accessed.
- `dataset` is the path to the kitti dataset where the `sequences` directory is.

Navigation:
- `n` is next scan,
- `b` is previous scan,
- `esc` or `q` exits.

##### 
