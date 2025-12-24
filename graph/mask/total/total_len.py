import os
import json
import matplotlib.pyplot as plt
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Malgun Gothic', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", ".."))

# 資料來源路徑
ROUND1_DIR = os.path.join(PROJECT_ROOT, "exam", "round1", "firsttest", "result_json", "1")
ROUND3_DIR = os.path.join(PROJECT_ROOT, "exam", "round3", "firsttest", "result_json", "1")

def load_crack_times(source_dirs):
    """
    讀取指定目錄下的所有 JSON 檔案，按密碼長度分類
    Returns: dict {length: [times]}
    """
    crack_times = {}
    
    for data_dir in source_dirs:
        if not os.path.exists(data_dir):
            print(f"警告: 目錄不存在 {data_dir}")
            continue
            
        print(f"正在讀取目錄: {data_dir}")
        
        # 遍歷所有資料夾 (例如 convert_basic8, convert_basic9...)
        for folder_name in os.listdir(data_dir):
            folder_path = os.path.join(data_dir, folder_name)
            if not os.path.isdir(folder_path):
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
                        mask = data.get("Guess.Mask", "")
                        
                        # 計算長度 (計算 ? 的數量)
                        length = mask.count('?')
                        
                        if length == 0:
                            continue

                        if length not in crack_times:
                            crack_times[length] = []
                        
                        crack_times[length].append(runtime)
                        
                except Exception as e:
                    print(f"讀取 {json_path} 失敗: {e}")
    
    return crack_times

def plot_boxplot(crack_times):
    """
    繪製 Box Plot
    """
    lengths = sorted(crack_times.keys())
    if not lengths:
        print("沒有資料可繪圖")
        return

    data = [crack_times[length] for length in lengths]
    
    plt.figure(figsize=(12, 8))
    
    # 樣式設定
    boxprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    medianprops = dict(linestyle='-', linewidth=2, color='#D35400')
    whiskerprops = dict(linestyle='--', linewidth=1.5, color='#555555')
    capprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    flierprops = dict(marker='o', markerfacecolor='#777777', markersize=4, linestyle='none', alpha=0.6)
    
    # 繪製 Box Plot
    # whis=(0, 100) 強制鬚線延伸到最大最小值
    bp = plt.boxplot(data, tick_labels=[str(l) for l in lengths], patch_artist=True,
                     boxprops=boxprops, medianprops=medianprops,
                     whiskerprops=whiskerprops, capprops=capprops, flierprops=flierprops,
                     whis=(0, 100))
    
    # 上色
    colors = ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2', '#F3E5F5']
    for patch, color in zip(bp['boxes'], colors * (len(lengths) // len(colors) + 1)):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
        
    plt.title('Crack Time by Password Length (Round 1 & Round 2 - FirstTest)', fontsize=16, fontweight='bold')
    plt.xlabel('Password Length (密碼長度)', fontsize=12)
    plt.ylabel('Crack Time (s)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # 自動調整 Y 軸上限
    all_times = [t for times in data for t in times]
    if all_times:
        max_time = max(all_times)
        plt.ylim(bottom=0, top=max_time * 1.1)
        
    # 加入統計資訊
    stats_text = []
    for i, length in enumerate(lengths):
        times = crack_times[length]
        stats_text.append(f"Len={length}: n={len(times)}, "
                          f"min={min(times):.2f}s, max={max(times):.2f}s, "
                          f"avg={np.mean(times):.2f}s")
    
    # 將統計資訊顯示在圖表下方
    plt.figtext(0.5, 0.02, '\n'.join(stats_text), ha='center', fontsize=10, 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', alpha=0.9, edgecolor='#dddddd'),
                family='monospace')
    
    plt.tight_layout(rect=[0, 0.15, 1, 1]) # 留出底部空間給文字
    
    output_path = os.path.join(BASE_DIR, "total_firsttest_len_time.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.show()

def main():
    print("=" * 60)
    print("密碼長度 vs 破解時間 分析 (Round 1 & Round 2 Total)")
    print("=" * 60)
    
    source_dirs = [ROUND1_DIR, ROUND3_DIR]
    crack_times = load_crack_times(source_dirs)
    
    # 簡單文字輸出
    for length in sorted(crack_times.keys()):
        times = crack_times[length]
        print(f"\n[Length {length}] Count={len(times)}")
        print(f"  Min={min(times):.2f}s, Max={max(times):.2f}s, "
              f"Med={np.median(times):.2f}s, Avg={np.mean(times):.2f}s")
                
    plot_boxplot(crack_times)

if __name__ == "__main__":
    main()
