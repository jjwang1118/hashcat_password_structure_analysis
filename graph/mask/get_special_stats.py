"""
從 round1 和 round3 的 secondtest/result_json/1 讀取所有密碼破解時間，
依照密碼長度（8~10位）與特殊字元數量（1~4個）計算統計數據
"""

import os
import json
import re
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_percentile(data, percentile):
    """計算百分位數"""
    if not data:
        return 0
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (n - 1) * percentile / 100
    f = int(k)
    c = k - f
    if f + 1 < n:
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    return sorted_data[f]

def load_crack_times(result_dirs):
    """
    讀取所有 JSON 檔案，按密碼長度與特殊字元數量分類
    Returns: dict {length: {special_count: [times]}}
    """
    crack_times = {
        8: {1: [], 2: [], 3: [], 4: []},
        9: {1: [], 2: [], 3: [], 4: []},
        10: {1: [], 2: [], 3: [], 4: []}
    }
    
    folder_pattern = re.compile(r"convert_basic(\d+)\+(\d+)")

    for result_dir in result_dirs:
        if not os.path.exists(result_dir):
            print(f"警告: 目錄不存在 {result_dir}")
            continue
            
        print(f"正在讀取目錄: {result_dir}")

        for folder_name in os.listdir(result_dir):
            folder_path = os.path.join(result_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            match = folder_pattern.match(folder_name)
            if not match:
                continue
                
            length = int(match.group(1))
            special_count = int(match.group(2))
            
            if length not in crack_times or special_count not in crack_times[length]:
                continue
                
            for json_file in os.listdir(folder_path):
                if not json_file.endswith(".json"):
                    continue
                
                json_path = os.path.join(folder_path, json_file)
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    if data.get("Status") == "Cracked":
                        runtime = data.get("Actual_Runtime_Seconds", 0)
                        crack_times[length][special_count].append(runtime)
                except Exception as e:
                    print(f"讀取 {json_path} 失敗: {e}")
    
    return crack_times

def calculate_stats(times):
    """計算統計數據"""
    if not times:
        return {
            'n': 0,
            'min': 0,
            'q1': 0,
            'med': 0,
            'q3': 0,
            'max': 0,
            'avg': 0
        }
    
    return {
        'n': len(times),
        'min': round(min(times), 2),
        'q1': round(get_percentile(times, 25), 2),
        'med': round(get_percentile(times, 50), 2),
        'q3': round(get_percentile(times, 75), 2),
        'max': round(max(times), 2),
        'avg': round(np.mean(times), 2)
    }

def main():
    print("=" * 80)
    print("特殊字元數量 vs 破解時間 統計分析")
    print("=" * 80)
    
    # Round 1
    round1_dirs = [os.path.join(BASE_DIR, "..", "..", "round1", "secondtest", "result_json", "1")]
    print("\n[Round 1]")
    crack_times_r1 = load_crack_times(round1_dirs)
    
    print("\nRound 1 統計結果:")
    for length in [8, 9, 10]:
        print(f"\n  Length {length}:")
        for sc in [1, 2, 3, 4]:
            times = crack_times_r1[length][sc]
            stats = calculate_stats(times)
            print(f"    +{sc} special: n={stats['n']}, min={stats['min']}, q1={stats['q1']}, "
                  f"med={stats['med']}, q3={stats['q3']}, max={stats['max']}, avg={stats['avg']}")
    
    # Round 2
    round2_dirs = [os.path.join(BASE_DIR, "..", "..", "round2", "secondtest", "result_json", "1")]
    print("\n" + "=" * 80)
    print("[Round 2]")
    crack_times_r2 = load_crack_times(round2_dirs)
    
    print("\nRound 2 統計結果:")
    for length in [8, 9, 10]:
        print(f"\n  Length {length}:")
        for sc in [1, 2, 3, 4]:
            times = crack_times_r2[length][sc]
            stats = calculate_stats(times)
            print(f"    +{sc} special: n={stats['n']}, min={stats['min']}, q1={stats['q1']}, "
                  f"med={stats['med']}, q3={stats['q3']}, max={stats['max']}, avg={stats['avg']}")
    
    # Total (combined)
    total_dirs = [
        os.path.join(BASE_DIR, "..", "..", "round1", "secondtest", "result_json", "1"),
        os.path.join(BASE_DIR, "..", "..", "round2", "secondtest", "result_json", "1")
    ]
    print("\n" + "=" * 80)
    print("[Total (Round 1 + Round 2)]")
    crack_times_total = load_crack_times(total_dirs)
    
    print("\nTotal 統計結果:")
    for length in [8, 9, 10]:
        print(f"\n  Length {length}:")
        for sc in [1, 2, 3, 4]:
            times = crack_times_total[length][sc]
            stats = calculate_stats(times)
            print(f"    +{sc} special: n={stats['n']}, min={stats['min']}, q1={stats['q1']}, "
                  f"med={stats['med']}, q3={stats['q3']}, max={stats['max']}, avg={stats['avg']}")

if __name__ == "__main__":
    main()
