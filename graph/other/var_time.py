import json
import os
import string
import glob
import statistics
import random
import matplotlib.pyplot as plt
import numpy as np

# 定義字符集
LOWER_CHARS = set(string.ascii_lowercase)
UPPER_CHARS = set(string.ascii_uppercase)
DIGIT_CHARS = set(string.digits)

def get_charset_diversity_level(password):
    """
    計算密碼的字符集多樣性 Level
    Level 1: 只有一種 (e.g., ?l only)
    Level 2: 兩種混和 (e.g., ?l + ?d)
    Level 3: 三種以上
    """
    has_lower = any(c in LOWER_CHARS for c in password)
    has_upper = any(c in UPPER_CHARS for c in password)
    has_digit = any(c in DIGIT_CHARS for c in password)
    has_special = any(c not in LOWER_CHARS and c not in UPPER_CHARS and c not in DIGIT_CHARS for c in password)
    
    diversity_count = sum([has_lower, has_upper, has_digit, has_special])
    
    if diversity_count >= 3:
        return 3
    return diversity_count

def process_json_files(base_dirs):
    results = {
        1: [],
        2: [],
        3: []
    }
    
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            continue
            
        search_pattern = os.path.join(base_dir, "**", "*.json")
        json_files = glob.glob(search_pattern, recursive=True)
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if data.get("Status") == "Cracked":
                    cracked_pwd = data.get("Cracked_Password")
                    runtime = data.get("Actual_Runtime_Seconds", 0)
                    
                    if cracked_pwd is not None:
                        level = get_charset_diversity_level(cracked_pwd)
                        results[level].append(runtime)
            except Exception:
                pass

    return results

def get_stats(data):
    if not data:
        return ["N/A"] * 5
    quantiles = statistics.quantiles(data, n=4)
    return [
        min(data),
        quantiles[0],
        statistics.median(data),
        quantiles[2],
        max(data)
    ]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exam_dir = os.path.dirname(os.path.dirname(script_dir))
    
    # 創建統一的輸出目錄
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    target_dirs = [
        os.path.join(exam_dir, "round1", "firsttest", "result_json", "1"),
        #os.path.join(exam_dir, "round1", "firsttest", "result_json", "2"),
        os.path.join(exam_dir, "round3", "firsttest", "result_json", "1"),
        #os.path.join(exam_dir, "round3", "firsttest", "result_json", "2"),
    ]
    
    print("Loading data...")
    all_data = process_json_files(target_dirs)
    
    # Ensure we have enough data
    if len(all_data[2]) < 7 or len(all_data[3]) < 7:
        print("Not enough data in Level 2 or Level 3 to sample 7 items.")
        print(f"Level 2 count: {len(all_data[2])}")
        print(f"Level 3 count: {len(all_data[3])}")
        return

    output_dir = r"C:\Users\$TMK000-1A7EC9ECGV29\Documents\hashcat-7.1.2\exam\graph\other\var"
    print(f"Generating 5 plots in {output_dir}...")

    for i in range(10):
        # Sampling
        if len(all_data[1]) >= 7:
             sample_l1 = random.sample(all_data[1], 7)
        else:
             sample_l1 = all_data[1] # Use all if less than 7

        sample_l2 = random.sample(all_data[2], 7)
        sample_l3 = random.sample(all_data[3], 7)
        
        plot_data = [sample_l1, sample_l2, sample_l3]
        labels = ['Level 1', 'Level 2', 'Level 3']
        
        # Statistics
        stats_l1 = get_stats(sample_l1)
        stats_l2 = get_stats(sample_l2)
        stats_l3 = get_stats(sample_l3)
        
        # Plotting
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Boxplot with whiskers extending to min/max (whis=(0, 100))
        ax.boxplot(plot_data, tick_labels=labels, whis=(0, 100))
        ax.set_title(f'Iteration {i+1}: Cracking Time vs Charset Diversity (Sampled 7)')
        ax.set_ylabel('Time (Seconds)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add Level Description
        desc_text = (
            "Level Definitions:\n"
            "Level 1: Single Charset (e.g., ?l)\n"
            "Level 2: Two Charsets (e.g., ?l + ?d)\n"
            "Level 3: Three+ Charsets (e.g., ?l + ?d + ?s)"
        )
        ax.text(0.02, 0.95, desc_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Prepare table text
        cell_text = []
        cell_text.append([f"{x:.2f}" for x in stats_l1])
        cell_text.append([f"{x:.2f}" for x in stats_l2])
        cell_text.append([f"{x:.2f}" for x in stats_l3])
        
        columns = ['Min', 'Q1', 'Median', 'Q3', 'Max']
        rows = ['Level 1', 'Level 2', 'Level 3']
        
        # Add table at the bottom
        table = plt.table(cellText=cell_text,
                          rowLabels=rows,
                          colLabels=columns,
                          loc='bottom',
                          bbox=[0.0, -0.3, 1.0, 0.2]) # Adjust bbox to fit
        
        plt.subplots_adjust(left=0.2, bottom=0.3) # Make room for table
        
        output_path = os.path.join(output_dir, f"var_time_boxplot_iter_{i+1}.png")
        plt.savefig(output_path)
        plt.close()
        print(f"Saved {output_path}")
        
        # Also print to console
        print(f"\nIteration {i+1} Stats:")
        print(f"{'Level':<10} | {'Min':<10} | {'Q1':<10} | {'Median':<10} | {'Q3':<10} | {'Max':<10}")
        print("-" * 70)
        for idx, row_label in enumerate(rows):
            vals = cell_text[idx]
            print(f"{row_label:<10} | {vals[0]:<10} | {vals[1]:<10} | {vals[2]:<10} | {vals[3]:<10} | {vals[4]:<10}")

if __name__ == "__main__":
    main()
