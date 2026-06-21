import os
import glob
import pandas as pd
import numpy as np

def analyze_cx40_fragmentation(folder_path, threshold=0.4, output_filename="Cx40_Advanced_Fragmentation_Results.xlsx"):
    """
    Advanced analysis of Cx40 spatial distribution to account for variable line lengths.
    Calculates absolute gap lengths and normalized length-independent metrics (fractions).
    """
    
    if not os.path.exists(folder_path):
        print(f"Error: Directory '{folder_path}' not found.")
        return

    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}'.")
        return
    
    print(f"Processing {len(csv_files)} profiles for length-independent metrics...")
    
    results = []
    error_count = 0

    for file in csv_files:
        try:
            # Use latin1 encoding to bypass the 'μm' character issue from Fiji
            df = pd.read_csv(file, encoding='latin1')
            
            x_values = df.iloc[:, 0].values
            y_values = df.iloc[:, 1].values
            
            # 1. Calculate Total Line Length
            total_line_length = x_values[-1] - x_values[0]
            if total_line_length <= 0:
                continue
                
            # Normalize Y values
            y_min = np.min(y_values)
            y_max = np.max(y_values)
            y_norm = np.zeros_like(y_values) if y_max == y_min else (y_values - y_min) / (y_max - y_min)
            
            # Find Gaps
            below_threshold = y_norm <= threshold
            padded = np.concatenate(([False], below_threshold, [False]))
            diff = np.diff(padded.astype(int))
            
            starts = np.where(diff == 1)[0]
            ends = np.where(diff == -1)[0]
            
            step_size = x_values[1] - x_values[0]
            gap_lengths = (ends - starts) * step_size
            
            # 2. Extract Absolute & Normalized Parameters
            if len(gap_lengths) > 0:
                max_gap_length = np.max(gap_lengths)
                total_gap_length = np.sum(gap_lengths)
                gap_count = len(gap_lengths)
            else:
                max_gap_length = 0.0
                total_gap_length = 0.0
                gap_count = 0
                
            # Calculate percentages (Length-independent variables)
            max_gap_fraction_pct = (max_gap_length / total_line_length) * 100
            total_fragmentation_idx = (total_gap_length / total_line_length) * 100
            
            results.append({
                "File_Name": os.path.basename(file),
                "Total_Line_Length_um": round(total_line_length, 2),
                "Absolute_Max_Gap_um": round(max_gap_length, 3),
                "Gap_Count": gap_count,
                "Max_Gap_Fraction_Percent": round(max_gap_fraction_pct, 2),
                "Total_Fragmentation_Index_Percent": round(total_fragmentation_idx, 2)
            })
            
        except Exception as e:
            error_count += 1
            print(f"Failed to process {os.path.basename(file)}. Reason: {e}")

    if not results:
        print("\nAnalysis failed completely. No valid data extracted.")
        return

    results_df = pd.DataFrame(results)
    output_path = os.path.join(folder_path, output_filename)
    
    try:
        results_df.to_excel(output_path, index=False)
        print(f"\nSUCCESS: {len(results)} files processed. ({error_count} skipped).")
        print(f"Saved length-independent results to: {output_path}")
    except Exception as e:
        print(f"Error saving Excel: {e}")


if __name__ == "__main__":
    # Update this path to where your actual CSVs are stored
    target_directory = r"C:\Users\leewi\OneDrive\Desktop\Cx40 Gap Quantification"
    
    analyze_cx40_fragmentation(folder_path=target_directory, threshold=0.4)