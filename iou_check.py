#!/usr/bin/env python3
import argparse
import os
import yaml
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from itertools import combinations
from collections import defaultdict
import gc

# Configuration
DISTANCES = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50)]
MIOU_THRESHOLD = 0.5  # Adjusted for mIoU
MAX_ANOMALIES = 1000

def calculate_miou_by_distance(scan, sem_label, class1, class2):
    """
    Enhanced mIoU calculation that combines:
    1. Spatial distribution (original distance-bin approach)
    2. Remission (intensity) histograms per bin
    3. Height (z-coordinate) histograms per bin
    """
    distances = np.sqrt(np.sum(scan[:, :3]**2, axis=1))
    remission = scan[:, 3]  # Intensity values
    z = scan[:, 2]  # Height values
    distance_bins = np.digitize(distances, bins=[d[1] for d in DISTANCES[:-1]]) - 1
    
    # Initialize results
    spatial_ious = []
    remission_ious = []
    height_ious = []
    
    for dist_bin in range(len(DISTANCES)):
        bin_mask = (distance_bins == dist_bin)
        mask1 = bin_mask & (sem_label == class1)
        mask2 = bin_mask & (sem_label == class2)
        
        # Skip bins with insufficient points
        if np.sum(mask1) < 10 or np.sum(mask2) < 10:
            continue
            
        # --- 1. Spatial IoU (original method) ---
        tp = np.sum(mask1)  # Class1 points in bin
        fp = np.sum(mask2)  # Class2 points in bin
        spatial_iou = tp / (tp + fp + 1e-10)
        spatial_ious.append(spatial_iou)
        
        # --- 2. Remission IoU ---
        hist1_rem, _ = np.histogram(remission[mask1], bins=20, range=(0, 1), density=True)
        hist2_rem, _ = np.histogram(remission[mask2], bins=20, range=(0, 1), density=True)
        rem_iou = np.sum(np.minimum(hist1_rem, hist2_rem)) / (np.sum(np.maximum(hist1_rem, hist2_rem)) + 1e-10)
        remission_ious.append(rem_iou)
        
        # --- 3. Height IoU ---
        hist1_z, _ = np.histogram(z[mask1], bins=20, density=True)
        hist2_z, _ = np.histogram(z[mask2], bins=20, density=True)
        z_iou = np.sum(np.minimum(hist1_z, hist2_z)) / (np.sum(np.maximum(hist1_z, hist2_z)) + 1e-10)
        height_ious.append(z_iou)
    
    # Compute mean IoUs (default to 0 if no valid bins)
    mean_spatial = np.mean(spatial_ious) if spatial_ious else 0.0
    mean_rem = np.mean(remission_ious) if remission_ious else 0.0
    mean_height = np.mean(height_ious) if height_ious else 0.0
    
    # Weighted combination (adjust weights based on your use case)
    return 0.4 * mean_spatial + 0.3 * mean_rem + 0.3 * mean_height

def analyze_sequence(scan_dir, label_dir, class_names, color_map, seqstr, output_dir):
    """Analyze sequence with mIoU-by-distance"""
    scan_files = sorted([f for f in os.listdir(scan_dir) if f.endswith('.bin')])
    label_files = sorted([f for f in os.listdir(label_dir) if f.endswith('.label')])
    
    valid_classes = {k:v for k,v in class_names.items() if v not in ['unlabeled', 'outlier']}
    class_pairs = list(combinations(valid_classes.keys(), 2))
    
    results = {
        'anomalies': defaultdict(list),
        'miou_data': defaultdict(list)  # Stores mIoU per frame
    }
    
    sample_frame = None
    
    for frame_idx, (scan_file, label_file) in enumerate(zip(scan_files, label_files)):
        try:
            scan_path = os.path.join(scan_dir, scan_file)
            label_path = os.path.join(label_dir, label_file)
            
            scan = np.fromfile(scan_path, dtype=np.float32).reshape(-1, 4)
            label = np.fromfile(label_path, dtype=np.uint32)
            sem_label = label & 0xFFFF
            
            if len(scan) != len(sem_label):
                continue
                
            if sample_frame is None:
                sample_frame = (scan.copy(), sem_label.copy())
            
            for class1, class2 in class_pairs:
                mask1 = (sem_label == class1)
                mask2 = (sem_label == class2)
                
                if np.sum(mask1) == 0 or np.sum(mask2) == 0:
                    continue
                
                # Calculate mIoU across distance bins
                miou = calculate_miou_by_distance(scan, sem_label, class1, class2)
                results['miou_data'][(class1, class2)].append(miou)
                
                if miou > MIOU_THRESHOLD:
                    anomaly_indices = np.where(mask1 | mask2)[0]
                    current = results['anomalies'][(class1, class2)]
                    remaining = MAX_ANOMALIES - len(current)
                    
                    if remaining > 0:
                        results['anomalies'][(class1, class2)].extend(
                            anomaly_indices[:remaining].tolist()
                        )
            
            if frame_idx % 50 == 0:
                gc.collect()
                
        except Exception as e:
            print(f"Error processing frame {scan_file}: {str(e)[:100]}", flush=True)
            continue
    
    return results, sample_frame

def visualize_anomalies(results, sample_frame, class_names, color_map, seqstr, output_dir):
    """Visualize mIoU-based anomalies (same structure as before)"""
    if sample_frame is None:
        return
        
    scan, sem_label = sample_frame
    base_dir = os.path.join(output_dir, f"sequence_{seqstr}")
    os.makedirs(base_dir, exist_ok=True)
    
    for (class1, class2), indices in results['anomalies'].items():
        if not indices:
            continue
            
        pair_dir = os.path.join(base_dir, f"{class_names[class1]}_vs_{class_names[class2]}")
        os.makedirs(pair_dir, exist_ok=True)
        
        # Plot anomalies (unchanged)
        fig, ax = plt.subplots(figsize=(10, 10))
        plot_step = max(1, len(scan) // 50000)
        ax.scatter(scan[::plot_step, 0], scan[::plot_step, 1], 
                  c='lightgray', s=1, alpha=0.3)
        
        valid_indices = [i for i in indices if i < len(scan)]
        points = scan[valid_indices]
        labels = sem_label[valid_indices]
        
        for class_id, color in [(class1, color_map[class1]), (class2, color_map[class2])]:
            mask = labels == class_id
            if np.any(mask):
                color = np.array(color) / 255.0
                ax.scatter(points[mask, 0], points[mask, 1], 
                          color=color, s=5, 
                          label=f'{class_names[class_id]}')
        
        ax.set_title(f"{class_names[class1]} vs {class_names[class2]} Anomalies\n(mIoU > {MIOU_THRESHOLD})")
        ax.legend()
        ax.set_aspect('equal')
        plt.savefig(os.path.join(pair_dir, "anomalies.png"), 
                   dpi=150, bbox_inches='tight')
        plt.close()
        
        # Plot mIoU distribution (renamed from IoU)
        mious = results['miou_data'][(class1, class2)]
        if len(mious) > 1:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(mious, bins=20, range=(0, 1), alpha=0.7)
            ax.axvline(MIOU_THRESHOLD, color='red', linestyle='--', label='Threshold')
            ax.set_xlabel('mIoU Score')
            ax.set_ylabel('Frequency')
            ax.set_title(f"mIoU Distribution: {class_names[class1]} vs {class_names[class2]}")
            ax.legend()
            plt.savefig(os.path.join(pair_dir, "miou_distribution.png"), 
                       dpi=150, bbox_inches='tight')
            plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser("./interclass_anomaly_detection.py")
    parser.add_argument(
        '--dataset', '-d',
        type=str,
        required=True,
        help='Dataset directory path',
    )
    parser.add_argument(
        '--labels', '-l',
        type=str,
        required=True,
        help='Path to semantic-kitti.yaml',
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default="anomaly_results",
        help='Output directory',
    )
    FLAGS = parser.parse_args()

    try:
        CFG = yaml.safe_load(open(FLAGS.labels, 'r'))
    except Exception as e:
        print(f"Error loading config: {e}")
        exit(1)

    sequences = CFG["split"]["train"]
    
    for seq in sequences:
        seqstr = '{0:02d}'.format(int(seq))
        print(f"\nAnalyzing sequence {seqstr}")
        
        scan_dir = os.path.join(FLAGS.dataset, "sequences", seqstr, "velodyne")
        label_dir = os.path.join(FLAGS.dataset, "sequences", seqstr, "labels")
        
        if not os.path.isdir(scan_dir) or not os.path.isdir(label_dir):
            print(f"Skipping sequence {seqstr} - missing data")
            continue
        
        results, sample_frame = analyze_sequence(
            scan_dir, label_dir, 
            CFG["labels"], CFG["color_map"],
            seqstr, FLAGS.output
        )

        visualize_anomalies(
            results, sample_frame,
            CFG["labels"], CFG["color_map"],
            seqstr, FLAGS.output
        )
        
        print(f"Finished sequence {seqstr}")