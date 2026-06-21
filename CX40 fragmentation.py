import os
import glob
import pandas as pd
import numpy as np

def analyze_cx40_gaps(folder_path, threshold=0.4, output_filename="Cx40_Gap_Analysis_Results.xlsx"):
    """
    Analyzes Cx40 spatial distribution profiles from Fiji/ImageJ CSV outputs.
    Calculates the maximum gap length where signal intensity falls below the specified threshold.
    """
    
    if not os.path.exists(folder_path):
        print(f"Error: The directory '{folder_path}' does not exist.")
        return

    search_pattern = os.path.join(folder_path, "*.csv")
    csv_files = glob.glob(search_pattern)
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}'. Please check the directory.")
        return
    
    print(f"Found {len(csv_files)} CSV files. Starting analysis...")
    
    results = []
    error_count = 0

    for file in csv_files:
        try:
            # 【核心修复点】：加入 encoding='latin1'，强制绕过 Fiji 的 "μm" 乱码报错
            df = pd.read_csv(file, encoding='latin1')
            
            x_values = df.iloc[:, 0].values
            y_values = df.iloc[:, 1].values
            
            y_min = np.min(y_values)
            y_max = np.max(y_values)
            
            if y_max == y_min:
                y_norm = np.zeros_like(y_values)
            else:
                y_norm = (y_values - y_min) / (y_max - y_min)
            
            below_threshold = y_norm <= threshold
            
            padded = np.concatenate(([False], below_threshold, [False]))
            diff = np.diff(padded.astype(int))
            
            starts = np.where(diff == 1)[0]
            ends = np.where(diff == -1)[0]
            
            step_size = x_values[1] - x_values[0]
            gap_lengths = (ends - starts) * step_size
            
            if len(gap_lengths) > 0:
                max_gap_length = np.max(gap_lengths)
                mean_gap_length = np.mean(gap_lengths)
                gap_count = len(gap_lengths)
            else:
                max_gap_length = 0.0
                mean_gap_length = 0.0
                gap_count = 0
            
            filename_only = os.path.basename(file)
            results.append({
                "File_Name": filename_only,
                "Max_Gap_Length_um": round(max_gap_length, 3),
                "Mean_Gap_Length_um": round(mean_gap_length, 3),
                "Gap_Count": gap_count
            })
            
        except Exception as e:
            error_count += 1
            print(f"Warning: Could not process file '{os.path.basename(file)}'. Reason: {e}")

    # 结果检查
    if len(results) == 0:
        print("\n[FAILED] Analysis failed for all files! Check the 'Reason' above to see what went wrong.")
        return

    results_df = pd.DataFrame(results)
    output_path = os.path.join(folder_path, output_filename)
    
    try:
        results_df.to_excel(output_path, index=False)
        print(f"\n[SUCCESS] Analyzed {len(results)} files. ({error_count} files failed).")
        print(f"Results successfully saved to: {output_path}")
    except Exception as e:
        print(f"Error: Could not save Excel file. Reason: {e}")
        fallback_path = os.path.join(folder_path, "Cx40_Gap_Analysis_Results.csv")
        results_df.to_csv(fallback_path, index=False)
        print(f"Results saved as CSV instead: {fallback_path}")


if __name__ == "__main__":
    target_directory = r"C:\Users\leewi\OneDrive\Desktop\Cx40 Gap Quantification"
    
    analyze_cx40_gaps(folder_path=target_directory, threshold=0.4)