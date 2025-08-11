import argparse
import os
import yaml
import numpy as np
import matplotlib
matplotlib.use('Agg') 
from matplotlib import pyplot as plt

if __name__ == '__main__':
    parser = argparse.ArgumentParser("./visualize.py")
    parser.add_argument(
        '--dataset', '-d',
        type=str,
        required=True,
        help='Dataset to visualize. No Default',
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        required=False,
        default="config/semantic-kitti.yaml",
        help='Dataset config file. Defaults to %(default)s',
    )
    parser.add_argument(
        '--sequence', '-s',
        type=str,
        default="00",
        required=False,
        help='Sequence to visualize. Defaults to %(default)s',
    )
    parser.add_argument(
        '--predictions', '-p',
        type=str,
        default=None,
        required=False,
        help='Alternate location for labels, to use predictions folder. '
        'Must point to directory containing the predictions in the proper format '
        ' (see readme)'
        'Defaults to %(default)s',
    )
    parser.add_argument(
        '--ignore_semantics', '-i',
        dest='ignore_semantics',
        default=False,
        action='store_true',
        help='Ignore semantics. Visualizes uncolored pointclouds.'
        'Defaults to %(default)s',
    )
    parser.add_argument(
        '--do_instances', '-o',
        dest='do_instances',
        default=False,
        required=False,
        action='store_true',
        help='Visualize instances too. Defaults to %(default)s',
    )
    parser.add_argument(
        '--ignore_images', '-r',
        dest='ignore_images',
        default=False,
        required=False,
        action='store_true',
        help='Visualize range image projections too. Defaults to %(default)s',
    )
    parser.add_argument(
        '--link', '-l',
        dest='link',
        default=False,
        required=False,
        action='store_true',
        help='Link viewpoint changes across windows. Defaults to %(default)s',
    )
    parser.add_argument(
        '--offset',
        type=int,
        default=0,
        required=False,
        help='Sequence to start. Defaults to %(default)s',
    )
    parser.add_argument(
        '--ignore_safety',
        dest='ignore_safety',
        default=False,
        required=False,
        action='store_true',
        help='Normally you want the number of labels and ptcls to be the same,'
        ', but if you are not done inferring this is not the case, so this disables'
        ' that safety.'
        'Defaults to %(default)s',
    )
    parser.add_argument(
        '--color_learning_map',
        dest='color_learning_map',
        default=False,
        required=False,
        action='store_true',
        help='Apply learning map to color map: visualize only classes that were trained on',
    )
    FLAGS, unparsed = parser.parse_known_args()

    # Load config
    try:
        print("Opening config file %s" % FLAGS.config)
        CFG = yaml.safe_load(open(FLAGS.config, 'r'))
    except Exception as e:
        print(e)
        print("Error opening yaml file.")
        quit()

    color_map = CFG["color_map"]
    class_names = CFG["labels"]
    sequences = CFG["split"]["train"]

    # where to save
    save_dir = os.path.join("intensity_curves")
    os.makedirs(save_dir, exist_ok=True)

    for seq in sequences:
        seqstr = '{0:02d}'.format(int(seq))
        print(f"Processing sequence {seqstr}")

        scan_paths = os.path.join(FLAGS.dataset, "sequences", seqstr, "velodyne")
        label_paths = os.path.join(FLAGS.dataset, "sequences", seqstr, "labels")

        if not os.path.isdir(scan_paths) or not os.path.isdir(label_paths):
            print("Missing scan or label folder.")
            continue

        scan_names = sorted([os.path.join(scan_paths, f) for f in os.listdir(scan_paths) if f.endswith(".bin")])
        label_names = sorted([os.path.join(label_paths, f) for f in os.listdir(label_paths) if f.endswith(".label")])

        # Initialize histograms
        histograms = {class_id: np.zeros(100) for class_id in class_names}
        bin_edges = np.linspace(0, 1, 101)  # Assuming remission is in [0, 1]

        for scan_file, label_file in zip(scan_names, label_names):
            scan = np.fromfile(scan_file, dtype=np.float32).reshape((-1, 4))
            remission = scan[:, 3]
            label = np.fromfile(label_file, dtype=np.uint32).reshape((-1))
            sem_label = label & 0xFFFF

            for class_id in class_names:
                mask = sem_label == class_id
                if np.any(mask):
                    hist, _ = np.histogram(remission[mask], bins=bin_edges)
                    histograms[class_id] += hist

        # Plotting
        num_classes = len(class_names)
        cols = 4
        rows = (num_classes + cols - 1) // cols

        fig, axs = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3))
        axs = axs.flatten()

        for idx, class_id in enumerate(class_names):
            ax = axs[idx]
            data = histograms[class_id]
            if np.sum(data) > 0:
                color = np.array(color_map[class_id]) / 255.0
                ax.bar(
                    bin_edges[:-1], data,
                    width=np.diff(bin_edges),
                    color=color,
                    alpha=0.8
                )
            ax.set_title(class_names[class_id])
            ax.set_xlabel("Remission")
            ax.set_ylabel("Frequency")

        for idx in range(len(class_names), len(axs)):
            axs[idx].axis('off')

        plt.tight_layout()
        fig_path = os.path.join(save_dir, f"{seqstr}.png")
        plt.savefig(fig_path)
        plt.close()
        print(f"Saved plot: {fig_path}")