#!/usr/bin/env python3
import os
import pandas as pd
import sys
import glob

def find_csv_without_info(directory):
    """Find the CSV file in the directory that doesn't have 'info' in its name."""
    csv_files = glob.glob(os.path.join(directory, "*.csv"))

    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        if "info" not in filename.lower():
            return csv_file

    return None

def process_csv_file(csv_path):
    """Process a single CSV file to find the best val_auroc and corresponding test_auroc."""
    try:
        df = pd.read_csv(csv_path)

        # Check if required columns exist
        if 'val_auroc' not in df.columns or 'test_auroc' not in df.columns:
            print(f"Warning: Required columns not found in {csv_path}")
            return None, None

        # Find the row with the highest val_auroc
        max_val_auroc_idx = df['val_auroc'].idxmax()
        best_val_auroc = df.loc[max_val_auroc_idx, 'val_auroc']
        corresponding_test_auroc = df.loc[max_val_auroc_idx, 'test_auroc']

        return best_val_auroc, corresponding_test_auroc

    except Exception as e:
        print(f"Error processing {csv_path}: {str(e)}")
        return None, None

def analyze_directory(root_directory):
    """Analyze all subdirectories and find the overall best val_auroc."""

    if not os.path.exists(root_directory):
        print(f"Error: Directory {root_directory} does not exist.")
        return

    overall_best_val_auroc = float('-inf')
    overall_best_test_auroc = None
    best_folder = None
    best_file = None

    results = []

    # Iterate through all subdirectories
    for folder_name in os.listdir(root_directory):
        folder_path = os.path.join(root_directory, folder_name)

        # Skip if not a directory
        if not os.path.isdir(folder_path):
            continue

        # Find the CSV file without "info" in its name
        csv_file = find_csv_without_info(folder_path)

        if csv_file is None:
            print(f"Warning: No CSV file without 'info' found in {folder_path}")
            continue

        # Process the CSV file
        val_auroc, test_auroc = process_csv_file(csv_file)

        if val_auroc is not None and test_auroc is not None:
            results.append({
                'folder': folder_name,
                'file': os.path.basename(csv_file),
                'val_auroc': val_auroc,
                'test_auroc': test_auroc
            })

            print(f"Folder: {folder_name}")
            print(f"  File: {os.path.basename(csv_file)}")
            print(f"  Best val_auroc: {val_auroc:.6f}")
            print(f"  Corresponding test_auroc: {test_auroc:.6f}")
            print()

            # Check if this is the overall best
            if val_auroc > overall_best_val_auroc:
                overall_best_val_auroc = val_auroc
                overall_best_test_auroc = test_auroc
                best_folder = folder_name
                best_file = os.path.basename(csv_file)

    # Print overall results
    print("="*50)
    print("OVERALL RESULTS")
    print("="*50)

    if overall_best_test_auroc is not None:
        print(f"Overall best val_auroc: {overall_best_val_auroc:.6f}")
        print(f"Corresponding test_auroc: {overall_best_test_auroc:.6f}")
        print(f"Found in folder: {best_folder}")
        print(f"From file: {best_file}")
    else:
        print("No valid results found.")

    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]
    analyze_directory(directory_path)

if __name__ == "__main__":
    main()
