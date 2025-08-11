# Modified SemanticKITTI API For Visualization and Detection Of Falsely Annotated Points

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
terminal. [class_counts.py](class_counts.py) returns the values of all the sequences
in a CSV file ('scenes_overview.csv') instead, together with the name of the classes as a reference.

```sh
$ ./class_counts.py --dataset /path/to/kitti/dataset/ --labels /path/to/config/file/
```
Where the dataset is the sequence folder, and the config file is [semantic-kitti.yaml](config/semantic-kitti.yaml).

#### Visualization 


##### Point Clouds

To visualize the data, use the `visualize.py` script. It will open an interactive
opengl visualization of the pointclouds along with a spherical projection of
each scan into a 64 x 1024 image. In this version of the `visualize.py` script,
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

##### Remission Distribution By Class

[intensity_curves.py](intensity_curves.py) produces an image, containing all the 
histogram plots of remission value frequency per class. Running this script creates
an `intensity_curves` folder, which contains folders of all the sequences (numbered
in numerical order), each of which contains its image (named `XX.png`, where `XX` is
the sequence number).

```sh
$ ./intensity_curves.py --dataset /path/to/kitti/dataset/ --labels /path/to/config/file/
```
Where the dataset is the sequence folder, and the config file is [semantic-kitti.yaml](config/semantic-kitti.yaml).

##### Check Potential Annotation Faults

[iou_check.py](iou_check.py) uses a mean Intersection over Union algorithm that takes the area,
remission and height into consideration. Running this script creates an `anomaly_results` folder.
Inside the folder contains folders named after each sequence number (named `sequence_XX`, where
`XX` is the sequence number), and within each of these folders contain folders of every comparision
of two classes that exists in the sequence (named `Class-1_vs_Class-2`, where `Class-1` and `Class-2`
are two different classes that exists in the sequence annotation). In each of these folders, there
will be a top view image of the scene (`anomalies.png`), with point labels of points with high IoU 
scores (which determines a likely chance that the annotated point should be labelled as the other 
compared class), and an image containing a histogram of IoU scores (`miou_distribution.png`) that
were detected in the calculations.

## Citations

1. **SemanticKITTI Dataset**  
   J. Behley, M. Garbade, A. Milioto, J. Quenzel, S. Behnke, C. Stachniss, and J. Gall.  
   "SemanticKITTI: A Dataset for Semantic Scene Understanding of LiDAR Sequences."  
   In *IEEE/CVF International Conference on Computer Vision (ICCV)*, 2019.

2. **KITTI Benchmark Suite**  
   A. Geiger, P. Lenz, and R. Urtasun.  
   "Are we ready for Autonomous Driving? The KITTI Vision Benchmark Suite."  
   In *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*,  
   pages 3354–3361, 2012.

```sh
$ ./iou_check.py --dataset /path/to/kitti/dataset/ --labels /path/to/config/file/
```
Where the dataset is the sequence folder, and the config file is [semantic-kitti.yaml](config/semantic-kitti.yaml).
