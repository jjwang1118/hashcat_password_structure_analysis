"""
讀取 round1/firsttest/result_json/2_dplus 和 round3/firsttest/result_json/2_dplus
計算密碼長度 8, 9, 10 的破解機率 (Cracked Percentage)
並繪製長條圖
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Malgun Gothic', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 指向 exam/round1/firsttest/result_json/2_dplus 和 exam/round3/firsttest/result_json/2_dplus
DATA_DIRS = [
    os.path.join(BASE_DIR, "..", "..", "..", "round1", "firsttest", "result_json", "2_dplus"),
    os.path.join(BASE_DIR, "..", "..", "..", "round3", "firsttest", "result_json", "2_dplus")
]

TARGET_LENGTHS = [8, 9, 10]

def calculate_crack_rates():
    """
    統計每個長度的總檔案數與破解數
    Returns: dict {length: {'total': int, 'cracked': int}}
    """
    stats = {length: {'total': 0, 'cracked': 0} for length in TARGET_LENGTHS}
    
    for result_dir in DATA_DIRS:
        if not os.path.exists(result_dir):
            print(f"警告: 目錄不存在 {result_dir}")
            continue
            
        print(f"正在讀取目錄: {result_dir}")
        
        # 遍歷目標長度資料夾 basic{Length}_d
        for length in TARGET_LENGTHS:
            folder_name = f"basic{length}_d"
            folder_path = os.path.join(result_dir, folder_name)
            
            if not os.path.exists(folder_path):
                print(f"  找不到資料夾: {folder_name}")
                continue
                
            # 讀取該資料夾內所有 JSON
            for json_file in os.listdir(folder_path):
                if not json_file.endswith(".json"):
                    continue
                
                json_path = os.path.join(folder_path, json_file)
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    stats[length]['total'] += 1
                    if data.get("Status") == "Cracked":
                        stats[length]['cracked'] += 1
                        
                except Exception as e:
                    print(f"讀取 {json_path} 失敗: {e}")
    
    return stats

def plot_crack_rates(stats):
    """
    繪製破解率長條圖
    """
    lengths = sorted(stats.keys())
    rates = []
    labels = []
    
    print("\n統計結果:")
    for length in lengths:
        total = stats[length]['total']
        cracked = stats[length]['cracked']
        rate = (cracked / total * 100) if total > 0 else 0
        rates.append(rate)
        labels.append(f"{length} chars")
        print(f"  Length {length}: {cracked}/{total} ({rate:.2f}%)")
    
    # 繪圖
    plt.figure(figsize=(10, 6))
    bars = plt.bar(lengths, rates, color=['#A8D8EA', '#AA96DA', '#FCBAD3'], edgecolor='grey', alpha=0.8)
    
    plt.title('Crack Rate by Password Length (2_dplus)', fontsize=16, fontweight='bold')
    plt.xlabel('Password Length', fontsize=12)
    plt.ylabel('Crack Rate (%)', fontsize=12)
    plt.xticks(lengths, labels)
    plt.ylim(0, 100) # 百分比 0-100
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # 在柱狀圖上方標示數值
    for bar, rate, length in zip(bars, rates, lengths):
        height = bar.get_height()
        total = stats[length]['total']
        cracked = stats[length]['cracked']
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%\n({cracked}/{total})',
                ha='center', va='bottom', fontsize=10)
    
    output_path = os.path.join(BASE_DIR, "len_pcracked_d.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n圖片已儲存至: {output_path}")
    plt.show()

def main():
    print("=" * 60)
    print("密碼長度 vs 破解機率 分析 (2_dplus)")
    print("資料來源: round1 & round3 / firsttest / result_json / 2_dplus")
    print("=" * 60)
    
    stats = calculate_crack_rates()
    plot_crack_rates(stats)

if __name__ == "__main__":
    main()
