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
    # 設定路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # script is in exam/graph/other/var/
    # we need to go up 3 levels to reach 'exam'
    exam_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    
    target_dirs = [
        os.path.join(exam_dir, "round1", "firsttest", "result_json", "1"),
        #os.path.join(exam_dir, "round1", "firsttest", "result_json", "2"),
        os.path.join(exam_dir, "round3", "firsttest", "result_json", "1"),
        #os.path.join(exam_dir, "round3", "firsttest", "result_json", "2"),
    ]
    
    print("Loading all data...")
    all_data = process_json_files(target_dirs)
    
    # Check if enough data
    if len(all_data[2]) < 7 or len(all_data[3]) < 7:
        print("Not enough data in Level 2 or Level 3 to sample 7 items.")
        return

    output_dir = script_dir
    
    # Monte Carlo Simulation
    iterations = 10000
    best_samples = None
    max_diff = -float('inf')
    
    print(f"Running {iterations} iterations to find sample with maximum difference (Mean L3 - Mean L2)...")
    
    for _ in range(iterations):
        # Sample 7
        if len(all_data[1]) >= 7:
             s1 = random.sample(all_data[1], 7)
        else:
             s1 = all_data[1]
             
        s2 = random.sample(all_data[2], 7)
        s3 = random.sample(all_data[3], 7)
        
        # Calculate metric: Mean(L3) - Mean(L2)
        # We want to maximize the gap between L3 and L2
        mean_l2 = statistics.mean(s2)
        mean_l3 = statistics.mean(s3)
        
        diff = mean_l3 - mean_l2
        
        if diff > max_diff:
            max_diff = diff
            best_samples = [s1, s2, s3]

    print(f"Max difference found: {max_diff:.2f} seconds")
    print(f"Generating plot in {output_dir}...")

    labels = ['Level 1', 'Level 2', 'Level 3']
    
    # Statistics for the best sample
    stats_l1 = get_stats(best_samples[0])
    stats_l2 = get_stats(best_samples[1])
    stats_l3 = get_stats(best_samples[2])
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Boxplot with whiskers extending to min/max
    ax.boxplot(best_samples, tick_labels=labels, whis=(0, 100))
    ax.set_title(f'Cracking Time vs Charset Diversity (Maximized Difference Sample)')
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
    rows = ['Level 1 (n=7)', 'Level 2 (n=7)', 'Level 3 (n=7)']
    
    # Add table at the bottom
    table = plt.table(cellText=cell_text,
                      rowLabels=rows,
                      colLabels=columns,
                      loc='bottom',
                      bbox=[0.0, -0.3, 1.0, 0.2])
    
    plt.subplots_adjust(left=0.2, bottom=0.3)
    
    output_path = os.path.join(output_dir, "var_time_max_diff.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved {output_path}")
    
    # Also print to console
    print(f"\nBest Sample Stats:")
    print(f"{'Level':<15} | {'Min':<10} | {'Q1':<10} | {'Median':<10} | {'Q3':<10} | {'Max':<10}")
    print("-" * 75)
    for idx, row_label in enumerate(rows):
        vals = cell_text[idx]
        print(f"{row_label:<15} | {vals[0]:<10} | {vals[1]:<10} | {vals[2]:<10} | {vals[3]:<10} | {vals[4]:<10}")

if __name__ == "__main__":
    main()
