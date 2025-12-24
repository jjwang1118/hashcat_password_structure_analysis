"""
統計 round1/firsttest 和 round3/firsttest 下的已破解密碼的字元構成類型數量：
1. 純字母 (Pure Letters)
2. 字母+數字 (Letters + Numbers)
3. 字母+數字+特殊符號 (Letters + Numbers + Special Characters)
"""

import os
import json
import re
import matplotlib.pyplot as plt

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Malgun Gothic', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 指向 exam/round1/firsttest/result_json 和 exam/round3/firsttest/result_json
DATA_DIRS = [
    os.path.join(BASE_DIR, "..", "..", "..", "round1", "firsttest", "result_json"),
    os.path.join(BASE_DIR, "..", "..", "..", "round3", "firsttest", "result_json")
]

def get_char_type(password):
    """
    判斷密碼類型
    """
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[^a-zA-Z0-9]', password))

    if has_letter and not has_digit and not has_special:
        return "Pure Letters"
    elif has_letter and has_digit and not has_special:
        return "Letters + Numbers"
    elif has_letter and has_digit and has_special:
        return "Letters + Numbers + Special"
    else:
        return "Others"

def count_password_types():
    """
    遍歷目錄統計密碼類型
    """
    counts = {
        "Pure Letters": 0,
        "Letters + Numbers": 0,
        "Letters + Numbers + Special": 0,
        "Others": 0
    }
    
    total_cracked = 0

    for result_dir in DATA_DIRS:
        if not os.path.exists(result_dir):
            print(f"警告: 目錄不存在 {result_dir}")
            continue
            
        print(f"正在掃描目錄: {result_dir}")
        
        # 遞迴遍歷所有子目錄
        for root, dirs, files in os.walk(result_dir):
            for file in files:
                if not file.endswith(".json"):
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    if data.get("Status") == "Cracked":
                        password = data.get("Cracked_Password")
                        if password:
                            char_type = get_char_type(password)
                            counts[char_type] += 1
                            total_cracked += 1
                            
                except Exception as e:
                    # print(f"讀取 {file_path} 失敗: {e}")
                    pass
    
    return counts, total_cracked

def plot_counts(counts):
    """
    繪製長條圖
    """
    # 過濾掉 "Others" 如果不需要顯示，或者保留
    # 這裡只顯示使用者要求的 3 類
    target_categories = ["Pure Letters", "Letters + Numbers", "Letters + Numbers + Special"]
    values = [counts[cat] for cat in target_categories]
    labels = ["純字母", "字母+數字", "字母+數字+特殊符號"]
    
    print("\n統計結果:")
    for label, val in zip(labels, values):
        print(f"  {label}: {val}")
    print(f"  其他 (Others): {counts['Others']}")
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=['#A8D8EA', '#AA96DA', '#FCBAD3'], edgecolor='grey', alpha=0.8)
    
    plt.title('Password Composition Types (Round1 & Round3 - Firsttest)', fontsize=16, fontweight='bold')
    plt.xlabel('Composition Type', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # 標示數值
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{val}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    output_path = os.path.join(BASE_DIR, "char_type_counts.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n圖片已儲存至: {output_path}")
    plt.show()

def main():
    print("=" * 60)
    print("密碼字元構成類型統計")
    print("資料來源: round1 & round3 / firsttest / result_json")
    print("=" * 60)
    
    counts, total = count_password_types()
    print(f"\n總共分析了 {total} 個已破解密碼。")
    
    plot_counts(counts)

if __name__ == "__main__":
    main()
