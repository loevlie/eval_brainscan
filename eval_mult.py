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
        return None, None, []
    
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
            
            print(f"  Folder: {folder_name}")
            print(f"    File: {os.path.basename(csv_file)}")
            print(f"    Best val_auroc: {val_auroc:.6f}")
            print(f"    Corresponding test_auroc: {test_auroc:.6f}")
            
            # Check if this is the overall best for this directory
            if val_auroc > overall_best_val_auroc:
                overall_best_val_auroc = val_auroc
                overall_best_test_auroc = test_auroc
                best_folder = folder_name
                best_file = os.path.basename(csv_file)
    
    # Return the best results for this directory
    if overall_best_test_auroc is not None:
        return overall_best_val_auroc, overall_best_test_auroc, results
    else:
        return None, None, results

def analyze_multiple_directories(directory_list):
    """Analyze multiple directories and calculate average scores."""
    all_best_val_aurocs = []
    all_best_test_aurocs = []
    all_results = []
    
    print("Analyzing directories...")
    print("="*60)
    
    for i, directory in enumerate(directory_list, 1):
        print(f"\n[{i}/{len(directory_list)}] Analyzing directory: {directory}")
        print("-" * 40)
        
        best_val, best_test, results = analyze_directory(directory)
        
        if best_val is not None and best_test is not None:
            all_best_val_aurocs.append(best_val)
            all_best_test_aurocs.append(best_test)
            all_results.extend(results)
            
            print(f"  → Best val_auroc for this directory: {best_val:.6f}")
            print(f"  → Corresponding test_auroc: {best_test:.6f}")
        else:
            print(f"  → No valid results found in {directory}")
    
    # Calculate averages
    print("\n" + "="*60)
    print("OVERALL RESULTS ACROSS ALL DIRECTORIES")
    print("="*60)
    
    if all_best_val_aurocs:
        avg_val_auroc = sum(all_best_val_aurocs) / len(all_best_val_aurocs)
        avg_test_auroc = sum(all_best_test_aurocs) / len(all_best_test_aurocs)
        
        print(f"Number of directories processed: {len(directory_list)}")
        print(f"Number of directories with valid results: {len(all_best_val_aurocs)}")
        print(f"Average best val_auroc across directories: {avg_val_auroc:.6f}")
        print(f"Average corresponding test_auroc: {avg_test_auroc:.6f}")
        
        # Additional statistics
        print(f"\nDetailed statistics:")
        print(f"  Val AUROC - Min: {min(all_best_val_aurocs):.6f}, Max: {max(all_best_val_aurocs):.6f}")
        print(f"  Test AUROC - Min: {min(all_best_test_aurocs):.6f}, Max: {max(all_best_test_aurocs):.6f}")
        
        # Show individual directory results
        print(f"\nIndividual directory results:")
        for i, directory in enumerate(directory_list):
            if i < len(all_best_val_aurocs):
                print(f"  {directory}: val_auroc={all_best_val_aurocs[i]:.6f}, test_auroc={all_best_test_aurocs[i]:.6f}")
        
        return avg_val_auroc, avg_test_auroc, all_results
    else:
        print("No valid results found in any directory.")
        return None, None, []

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <directory_path1> [directory_path2] [directory_path3] ...")
        print("Example: python script.py /path/to/dir1 /path/to/dir2 /path/to/dir3")
        sys.exit(1)
    
    directory_paths = sys.argv[1:]
    
    # Verify all directories exist
    valid_directories = []
    for dir_path in directory_paths:
        if os.path.exists(dir_path):
            valid_directories.append(dir_path)
        else:
            print(f"Warning: Directory {dir_path} does not exist. Skipping.")
    
    if not valid_directories:
        print("Error: No valid directories provided.")
        sys.exit(1)
    
    avg_val, avg_test, all_results = analyze_multiple_directories(valid_directories)
    
    if avg_val is not None:
        print(f"\n🎯 FINAL AVERAGE SCORES:")
        print(f"   Average Val AUROC: {avg_val:.6f}")
        print(f"   Average Test AUROC: {avg_test:.6f}")

if __name__ == "__main__":
    main()
