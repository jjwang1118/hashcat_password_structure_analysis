"""
分析 secondtest 中特殊字符位置（前綴 vs 後綴）對破解時間的影響
資料來源: round1 和 round3 的 secondtest/result_json/1
每個類別隨機取樣 77 個
"""

import json
import os
import glob
import string
import statistics
import random
import matplotlib.pyplot as plt
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Malgun Gothic', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 定義字符集
LOWER_CHARS = set(string.ascii_lowercase)
UPPER_CHARS = set(string.ascii_uppercase)
DIGIT_CHARS = set(string.digits)

# 設定隨機種子以確保可重現性
RANDOM_SEED = 42
SAMPLE_SIZE = 77

def is_special_char(char):
    """判斷字符是否為特殊字符（非字母、非數字）"""
    return char not in LOWER_CHARS and char not in UPPER_CHARS and char not in DIGIT_CHARS

def classify_position(password):
    """
    分類密碼中特殊字符的位置
    Returns: 'prefix', 'suffix', 'mixed', 'none'
    """
    if not password:
        return 'none'
    
    # 找出所有特殊字符的位置
    special_positions = [i for i, char in enumerate(password) if is_special_char(char)]
    
    if not special_positions:
        return 'none'
    
    # 檢查特殊字符是否都在開頭
    # 前綴：所有特殊字符都在前面，且是連續的
    if special_positions[0] == 0:
        # 檢查是否連續
        expected = list(range(len(special_positions)))
        if special_positions == expected:
            return 'prefix'
    
    # 檢查特殊字符是否都在結尾
    # 後綴：所有特殊字符都在後面，且是連續的
    if special_positions[-1] == len(password) - 1:
        # 檢查是否連續
        expected = list(range(len(password) - len(special_positions), len(password)))
        if special_positions == expected:
            return 'suffix'
    
    # 其他情況視為混合
    return 'mixed'

def process_json_files(base_dirs):
    """
    讀取所有 JSON 檔案，按特殊字符位置分類
    Returns: dict {position: [times]}
    """
    results = {
        'prefix': [],
        'suffix': [],
        'mixed': []
    }
    
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            print(f"警告: 目錄不存在 {base_dir}")
            continue
            
        print(f"正在掃描: {base_dir}")
        
        # 搜尋所有 .json 檔案 (遞迴)
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
                        position = classify_position(cracked_pwd)
                        if position in results:
                            results[position].append({
                                'password': cracked_pwd,
                                'time': runtime,
                                'file': os.path.basename(json_file)
                            })
            except Exception as e:
                print(f"讀取 {json_file} 失敗: {e}")
    
    return results

def random_sample_results(results, sample_size=SAMPLE_SIZE, seed=RANDOM_SEED):
    """
    從每個類別隨機取樣指定數量
    """
    random.seed(seed)
    sampled_results = {}
    
    print(f"\n開始隨機取樣（每類 {sample_size} 個）...")
    print("="*80)
    
    for position, data in results.items():
        available = len(data)
        if available == 0:
            sampled_results[position] = []
            print(f"{position.upper()}: 無資料")
        elif available <= sample_size:
            sampled_results[position] = data
            print(f"{position.upper()}: 資料不足 {sample_size} 個，使用全部 {available} 個")
        else:
            sampled_results[position] = random.sample(data, sample_size)
            print(f"{position.upper()}: 從 {available} 個中隨機取樣 {sample_size} 個")
    
    return sampled_results

def get_stats(data):
    """計算統計數據"""
    if not data:
        return None
    times = [item['time'] for item in data]
    return {
        'count': len(times),
        'min': min(times),
        'max': max(times),
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'q1': statistics.quantiles(times, n=4)[0] if len(times) >= 4 else min(times),
        'q3': statistics.quantiles(times, n=4)[2] if len(times) >= 4 else max(times)
    }

def plot_comparison(results):
    """繪製比較圖表"""
    # 準備數據
    positions = ['Prefix', 'Suffix', 'Mixed']
    data_keys = ['prefix', 'suffix', 'mixed']
    plot_data = []
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
    
    for key in data_keys:
        times = [item['time'] for item in results[key]]
        plot_data.append(times)
    
    # 建立圖表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    
    # 左圖：Box Plot
    bp = ax1.boxplot(plot_data, labels=positions, patch_artist=True, whis=(0, 100))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_title(f'Crack Time by Special Character Position\n(Random Sample: n={SAMPLE_SIZE} per category)', 
                 fontsize=14, fontweight='bold')
    ax1.set_ylabel('Time (Seconds)', fontsize=12)
    ax1.set_xlabel('Position Type', fontsize=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    # 右圖：Bar Chart (平均時間比較)
    stats_list = [get_stats(results[key]) for key in data_keys]
    means = [s['mean'] if s else 0 for s in stats_list]
    
    bars = ax2.bar(positions, means, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.set_title(f'Average Crack Time Comparison\n(Random Sample: n={SAMPLE_SIZE} per category)', 
                 fontsize=14, fontweight='bold')
    ax2.set_ylabel('Average Time (Seconds)', fontsize=12)
    ax2.set_xlabel('Position Type', fontsize=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    
    # 在柱狀圖上標註數值
    for bar, mean, stat in zip(bars, means, stats_list):
        height = bar.get_height()
        if stat:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{mean:.1f}s\n(n={stat["count"]})',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 建立統計資訊表格
    cell_text = []
    for stat in stats_list:
        if stat:
            cell_text.append([
                f"{stat['count']}",
                f"{stat['min']:.2f}s",
                f"{stat['q1']:.2f}s",
                f"{stat['median']:.2f}s",
                f"{stat['q3']:.2f}s",
                f"{stat['max']:.2f}s",
                f"{stat['mean']:.2f}s"
            ])
        else:
            cell_text.append(['N/A'] * 7)
    
    columns = ['Count', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean']
    
    # 在圖表下方添加表格
    table = plt.table(cellText=cell_text,
                      rowLabels=positions,
                      colLabels=columns,
                      loc='bottom',
                      bbox=[0.0, -0.25, 1.0, 0.15],
                      cellLoc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)
    
    # 設置表格樣式
    for i in range(len(columns)):
        table[(0, i)].set_facecolor('#E8E8E8')
        table[(0, i)].set_text_props(weight='bold')
    
    for i in range(len(positions)):
        table[(i+1, -1)].set_facecolor('#F5F5F5')
        table[(i+1, -1)].set_text_props(weight='bold')
    
    # 添加取樣資訊說明
    sample_info = f'Random Seed: {RANDOM_SEED} | Sample Size: {SAMPLE_SIZE} per category'
    fig.text(0.5, 0.02, sample_info, ha='center', fontsize=9, style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='gray', alpha=0.8))
    
    plt.subplots_adjust(bottom=0.28)
    
    # 儲存圖表
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "prefix_postfix_time_random.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n圖片已儲存至: {output_path}")
    plt.show()

def print_detailed_stats(results, original_counts=None):
    """輸出詳細統計資訊"""
    print("\n" + "="*80)
    print("特殊字符位置 vs 破解時間 詳細統計（隨機取樣）")
    print("="*80)
    
    for position in ['prefix', 'suffix', 'mixed']:
        stats = get_stats(results[position])
        if stats:
            print(f"\n[{position.upper()}]")
            if original_counts:
                print(f"  原始資料數量: {original_counts[position]}")
            print(f"  取樣數量: {stats['count']}")
            print(f"  最小時間: {stats['min']:.2f}s")
            print(f"  第一四分位 (Q1): {stats['q1']:.2f}s")
            print(f"  中位數: {stats['median']:.2f}s")
            print(f"  第三四分位 (Q3): {stats['q3']:.2f}s")
            print(f"  最大時間: {stats['max']:.2f}s")
            print(f"  平均時間: {stats['mean']:.2f}s")
            
            # 顯示前 3 個最耗時的案例
            sorted_items = sorted(results[position], key=lambda x: x['time'], reverse=True)[:3]
            print(f"  最耗時案例:")
            for item in sorted_items:
                print(f"    - {item['password']} ({item['time']:.2f}s)")
        else:
            print(f"\n[{position.upper()}]")
            print(f"  無資料")

def main():
    print("="*80)
    print("特殊字符位置分析 (Prefix vs Suffix vs Mixed) - 隨機取樣版本")
    print("資料來源: round1 & round3 / secondtest / result_json / 1")
    print(f"取樣方式: 每個類別隨機取 {SAMPLE_SIZE} 個")
    print(f"隨機種子: {RANDOM_SEED}")
    print("="*80)
    
    # 設定路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exam_dir = os.path.dirname(os.path.dirname(script_dir))
    
    target_dirs = [
        os.path.join(exam_dir, "round1", "secondtest", "result_json", "1"),
        os.path.join(exam_dir, "round3", "secondtest", "result_json", "1"),
    ]
    
    # 處理資料
    results_all = process_json_files(target_dirs)
    
    # 記錄原始數量
    original_counts = {k: len(v) for k, v in results_all.items()}
    
    # 隨機取樣
    results_sampled = random_sample_results(results_all, SAMPLE_SIZE, RANDOM_SEED)
    
    # 輸出統計
    print_detailed_stats(results_sampled, original_counts)
    
    # 繪製圖表
    plot_comparison(results_sampled)
    
    # 額外分析：按長度細分
    print("\n" + "="*80)
    print("額外洞察：按密碼長度細分（取樣後）")
    print("="*80)
    
    for position in ['prefix', 'suffix', 'mixed']:
        if results_sampled[position]:
            by_length = {}
            for item in results_sampled[position]:
                pwd_len = len(item['password'])
                if pwd_len not in by_length:
                    by_length[pwd_len] = []
                by_length[pwd_len].append(item['time'])
            
            print(f"\n[{position.upper()}]")
            for length in sorted(by_length.keys()):
                times = by_length[length]
                avg_time = statistics.mean(times)
                print(f"  長度 {length}: {len(times)} 筆, 平均 {avg_time:.2f}s")

if __name__ == "__main__":
    main()
