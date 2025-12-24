"""
讀取 round1, round2, total 的破解時間數據，
計算完整的箱型圖統計數據 (min, Q1, median, Q3, max, mean)
"""

import os
import json
import sys

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
    else:
        return sorted_data[f]

def load_crack_times(result_dir):
    """
    讀取指定目錄下的 JSON 檔案，按密碼長度分類
    Returns: dict {長度: [破解時間列表]}
    """
    crack_times = {8: [], 9: [], 10: [], 11: [], 12: []}
    
    if not os.path.exists(result_dir):
        print(f"目錄不存在: {result_dir}")
        return crack_times
    
    # 遍歷各長度資料夾
    for folder_name in os.listdir(result_dir):
        folder_path = os.path.join(result_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue
        
        # 從資料夾名稱提取長度
        try:
            length = int(folder_name.replace("convert_basic", ""))
        except ValueError:
            continue
        
        if length not in crack_times:
            continue
        
        # 讀取該資料夾內所有 JSON
        for json_file in os.listdir(folder_path):
            if not json_file.endswith(".json"):
                continue
            
            json_path = os.path.join(folder_path, json_file)
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if data.get("Status") == "Cracked":
                    runtime = data.get("Actual_Runtime_Seconds", 0)
                    crack_times[length].append(runtime)
            except Exception as e:
                print(f"讀取失敗 {json_path}: {e}")
    
    return crack_times

def calculate_stats(times):
    """計算完整統計數據"""
    if not times:
        return None
    
    sorted_times = sorted(times)
    n = len(sorted_times)
    
    return {
        'n': n,
        'min': min(times),
        'q1': get_percentile(times, 25),
        'median': get_percentile(times, 50),
        'q3': get_percentile(times, 75),
        'max': max(times),
        'mean': sum(times) / n
    }

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exam_dir = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
    
    # 三個數據源
    round1_dir = os.path.join(exam_dir, "exam", "round1", "firsttest", "result_json", "1")
    round2_dir = os.path.join(exam_dir, "exam", "round2", "firsttest", "result_json", "1")
    
    print("=" * 70)
    print("密碼長度破解時間完整統計數據")
    print("=" * 70)
    
    # Round 1
    print("\n[Round 1]")
    round1_times = load_crack_times(round1_dir)
    for length in sorted(round1_times.keys()):
        stats = calculate_stats(round1_times[length])
        if stats:
            print(f"{length}bit: n={stats['n']:<3} "
                  f"min={stats['min']:.2f}s, Q1={stats['q1']:.2f}s, "
                  f"med={stats['median']:.2f}s, Q3={stats['q3']:.2f}s, "
                  f"max={stats['max']:.2f}s, avg={stats['mean']:.2f}s")
    
    # Round 2
    print("\n[Round 2]")
    round2_times = load_crack_times(round2_dir)
    for length in sorted(round2_times.keys()):
        stats = calculate_stats(round2_times[length])
        if stats:
            print(f"{length}bit: n={stats['n']:<3} "
                  f"min={stats['min']:.2f}s, Q1={stats['q1']:.2f}s, "
                  f"med={stats['median']:.2f}s, Q3={stats['q3']:.2f}s, "
                  f"max={stats['max']:.2f}s, avg={stats['mean']:.2f}s")
    
    # Total (合併)
    print("\n[Total - Round 1 & 2 合併]")
    total_times = {8: [], 9: [], 10: [], 11: [], 12: []}
    for length in total_times.keys():
        total_times[length] = round1_times[length] + round2_times[length]
    
    for length in sorted(total_times.keys()):
        stats = calculate_stats(total_times[length])
        if stats:
            print(f"{length}bit: n={stats['n']:<3} "
                  f"min={stats['min']:.2f}s, Q1={stats['q1']:.2f}s, "
                  f"med={stats['median']:.2f}s, Q3={stats['q3']:.2f}s, "
                  f"max={stats['max']:.2f}s, avg={stats['mean']:.2f}s")
    
    print("\n" + "=" * 70)
    print("完成！")

if __name__ == "__main__":
    main()
