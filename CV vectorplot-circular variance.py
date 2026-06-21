# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:24:51 2026

@author: leewi
"""

# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os


matplotlib.rcParams['svg.fonttype'] = 'none' 
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False 

def analyze_mea_conduction(file_path):
    """
  
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_lines = [line.strip().split(';') for line in f.readlines()]

        v_idx, a_idx = -1, -1
        for i, line in enumerate(raw_lines):
            if len(line) > 0:
                if "Velocity" in line[0]: v_idx = i + 1
                if "Angle" in line[0]: a_idx = i + 1

        if v_idx == -1 or a_idx == -1: return None

        def extract_matrix(start_idx, data_source):
            matrix = []
            for row in data_source[start_idx:]:
                if not row or (len(row) > 0 and row[0] in ["Angle", "Velocity"]): break
                cleaned_row = []
                for x in row[:23]:
                    try: cleaned_row.append(float(x))
                    except: cleaned_row.append(np.nan)
                if not all(np.isnan(cleaned_row)): matrix.append(cleaned_row)
            return np.array(matrix)

        v_mat = extract_matrix(v_idx, raw_lines)
        a_mat = extract_matrix(a_idx, raw_lines)
        
        min_rows = min(v_mat.shape[0], a_mat.shape[0])
        v_vals = v_mat[:min_rows].flatten()
        a_vals = a_mat[:min_rows].flatten()

        v_vals = v_vals / 10.0 # cm/s
        mask = ~np.isnan(v_vals) & ~np.isnan(a_vals)
        v_clean, a_clean = v_vals[mask], a_vals[mask]

    
        if len(v_clean) > 0:
            ll, ul = np.percentile(v_clean, 5), np.percentile(v_clean, 95)
            valid_mask = (v_clean >= ll) & (v_clean <= ul)
            v_f, a_f_deg = v_clean[valid_mask], a_clean[valid_mask]
        else: return None

        median_cv = np.median(v_f)
     
        a_f_rad = np.deg2rad(-a_f_deg)

        R = np.sqrt(np.sum(np.cos(a_f_rad))**2 + np.sum(np.sin(a_f_rad))**2) / len(a_f_rad)
        circ_var = 1 - R

     
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, polar=True)
        
        # 增大角度数字字体 (0, 45, 90...)
        ax.tick_params(axis='x', labelsize=18, pad=10) 
     
        ax.tick_params(axis='y', labelsize=12)
        
      
        for label in ax.get_xticklabels():
            label.set_fontname('Arial')

        bins = np.linspace(-np.pi, np.pi, 37)
        
     
        counts, _ = np.histogram(a_f_rad, bins=bins)
        
        ax.bar(bins[:-1], counts, width=np.diff(bins), color='#008080', alpha=0.8, edgecolor='white')
        ax.set_theta_zero_location("E") 
        
        file_name_short = os.path.basename(file_path).replace('.csv', '')
    
        ax.set_title(f"Wavefront: {file_name_short}\nMedian CV: {median_cv:.2f} cm/s | Circ Var: {circ_var:.4f}", 
                     pad=25, fontsize=14, fontweight='bold', fontname='Arial')

  
        output_name = f"{file_name_short}_calibrated_rose.svg"
        plt.savefig(output_name, format='svg', bbox_inches='tight')
        plt.close()

        return median_cv, circ_var

    except Exception as e:
        print(f"出错: {file_path} -> {e}")
        return None

if __name__ == "__main__":
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    for file in csv_files:
        print(f"处理中: {file}")
        analyze_mea_conduction(file)
    print("\n✅ 已全部完成。SVG 导出已适配 Affinity，且数值保持老版本逻辑。")