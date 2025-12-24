"""
從 round1/secondtest/result_json/1 讀取所有密碼破解時間，
依照密碼長度（8~10位）與特殊字元數量（1~4個）繪製四分位距圖（Box Plot）
"""

import os
import json
import re
import matplotlib.pyplot as plt
import numpy as np
import itertools
from matplotlib.ticker import MaxNLocator

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Malgun Gothic', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 指向 round1 和 round3 的 secondtest/result_json/1
RESULT_JSON_DIRS = [
    
    os.path.join(BASE_DIR, "..", "..", "..", "round3", "secondtest", "result_json", "1")
]

def load_crack_times():
    """
    讀取所有 JSON 檔案，按密碼長度與特殊字元數量分類
    Returns: dict {length: {special_count: [times]}}
    """
    # 初始化資料結構: 8~10位，每位有 1~4 個特殊字元
    crack_times = {
        8: {1: [], 2: [], 3: [], 4: []},
        9: {1: [], 2: [], 3: [], 4: []},
        10: {1: [], 2: [], 3: [], 4: []}
    }
    
    # 正則表達式匹配資料夾名稱: convert_basic{Length}+{SpecialCount}
    folder_pattern = re.compile(r"convert_basic(\d+)\+(\d+)")

    for result_dir in RESULT_JSON_DIRS:
        if not os.path.exists(result_dir):
            print(f"錯誤: 目錄不存在 {result_dir}")
            continue

        print(f"Scanning directory: {result_dir}")
        for folder_name in os.listdir(result_dir):
            folder_path = os.path.join(result_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            match = folder_pattern.match(folder_name)
            if not match:
                continue
                
            length = int(match.group(1))
            special_count = int(match.group(2))
            
            # 只處理我們關心的範圍
            if length not in crack_times:
                continue
            if special_count not in crack_times[length]:
                continue
                
            # 讀取該資料夾內所有 JSON
            json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
            
            for json_file in json_files:
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

def plot_grouped_boxplot(crack_times):
    """
    繪製分組 Box Plot (每個長度一張子圖)
    """
    lengths = sorted(crack_times.keys()) # [8, 9, 10]
    
    # 計算全域最大值，以便統一 Y 軸範圍
    all_values = []
    for length in lengths:
        for sc in [1, 2, 3, 4]:
            all_values.extend(crack_times[length][sc])
    global_max = max(all_values) if all_values else 10

    # 建立 1x3 的子圖 (增加高度以容納底部資訊)
    # 修改: sharey=True 讓所有子圖共用 Y 軸刻度
    fig, axes = plt.subplots(1, 3, figsize=(18, 11), sharey=True)
    if len(lengths) == 1:
        axes = [axes]
    
    # 樣式設定
    boxprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    medianprops = dict(linestyle='-', linewidth=2, color='#D35400')
    whiskerprops = dict(linestyle='--', linewidth=1.5, color='#555555')
    capprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    flierprops = dict(marker='o', markerfacecolor='#777777', markersize=4, linestyle='none', alpha=0.6)
    
    colors = ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2'] # 對應 1~4 個特殊字元
    
    for idx, length in enumerate(lengths):
        ax = axes[idx]
        special_counts = [1, 2, 3, 4]
        data = [crack_times[length][sc] for sc in special_counts]
        
        # 繪製 Box Plot
        # whis=(0, 100) 強制鬚線延伸到最大最小值
        bp = ax.boxplot(data, labels=[str(sc) for sc in special_counts], patch_artist=True,
                        boxprops=boxprops, medianprops=medianprops,
                        whiskerprops=whiskerprops, capprops=capprops, flierprops=flierprops,
                        whis=(0, 100))
        
        # 上色
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
            
        # 設定標題與標籤
        ax.set_title(f'Password Length: {length} chars', fontsize=14, fontweight='bold')
        ax.set_xlabel('Special Char Count (特殊字元數量)', fontsize=11)
        if idx == 0:
            ax.set_ylabel('Crack Time (s)', fontsize=12)
            
        # 格線與刻度
        ax.grid(axis='y', linestyle='--', alpha=0.6, color='#cccccc')
        ax.set_axisbelow(True)
        
        # 統一設定 Y 軸上限 (使用全域最大值)
        ax.set_ylim(bottom=0, top=global_max * 1.1)
            
        # 加入統計資訊
        stats_text = []
        for i, sc in enumerate(special_counts):
            times = crack_times[length][sc]
            if times:
                stats_text.append(f"Spec={sc}: n={len(times)} "
                                f"min={min(times):.1f}s, max={max(times):.1f}s, "
                                f"med={np.median(times):.1f}s, avg={np.mean(times):.1f}s")
        
        if stats_text:
            textstr = '\n'.join(stats_text)
            props = dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', alpha=0.9, edgecolor='#dddddd')
            # 將統計資訊移至圖表下方，避免遮擋數據
            ax.text(0.5, -0.12, textstr, transform=ax.transAxes, fontsize=9,
                    verticalalignment='top', horizontalalignment='center', bbox=props, family='monospace')

    fig.suptitle('Crack Time by Special Character Count (Secondtest -  Round3)', fontsize=18, fontweight='bold', y=0.98)
    # 調整佈局，底部留出更多空間給統計資訊
    plt.tight_layout(rect=[0, 0.15, 1, 0.95])
    
    output_path = os.path.join(BASE_DIR, "round2_secondtest_token_num_time_accurate.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.show()

def main():
    print("=" * 60)
    print("特殊字元數量 vs 破解時間 分析 (Length 8-10)")
    print("資料來源:round３ / secondtest / result_json / 1")
    print("=" * 60)
    
    crack_times = load_crack_times()
    
    # 簡單文字輸出
    for length in sorted(crack_times.keys()):
        print(f"\n[Length {length}]")
        for sc in [1, 2, 3, 4]:
            times = crack_times[length][sc]
            if times:
                print(f"  Spec Chars {sc}: Count={len(times)}, "
                      f"Min={min(times):.2f}s, Max={max(times):.2f}s, "
                      f"Med={np.median(times):.2f}s, Avg={np.mean(times):.2f}s")
            else:
                print(f"  Spec Chars {sc}: No Data")
                
    plot_grouped_boxplot(crack_times)

if __name__ == "__main__":
    main()
