"""
從 round1/firsttest/result_json/1 讀取所有密碼破解時間，
依照密碼長度（8~12位）繪製四分位距圖（Box Plot）
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
import itertools
from matplotlib.ticker import MaxNLocator

# 設定中文字體 (使用 Windows 內建的微軟正黑體)
# 嘗試多種常見中文字體，確保能正確顯示
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Malgun Gothic', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_JSON_DIR = os.path.join(BASE_DIR, "..", "..", "..", "round3", "firsttest", "result_json", "1")

def load_crack_times():
    """
    讀取所有 JSON 檔案，按密碼長度分類破解時間
    Returns: dict {長度: [破解時間列表]}
    """
    crack_times = {8: [], 9: [], 10: [], 11: [], 12: []}
    
    # 遍歷各長度資料夾
    for folder_name in os.listdir(RESULT_JSON_DIR):
        folder_path = os.path.join(RESULT_JSON_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
        
        # 從資料夾名稱提取長度 (如 convert_basic8 -> 8)
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
                
                # 只取成功破解的密碼
                if data.get("Status") == "Cracked":
                    runtime = data.get("Actual_Runtime_Seconds", 0)
                    crack_times[length].append(runtime)
            except Exception as e:
                print(f"讀取 {json_path} 失敗: {e}")
    
    return crack_times


def plot_boxplot(crack_times):
    """
    繪製四分位距圖（Box Plot）
    """
    # 準備資料
    lengths = sorted(crack_times.keys())
    data = [crack_times[length] for length in lengths]
    
    # 建立圖表 (放大尺寸)
    fig, ax = plt.subplots(figsize=(21, 12))
    
    # 設定樣式參數
    boxprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    medianprops = dict(linestyle='-', linewidth=2, color='#D35400') # 深橘色中位數線
    whiskerprops = dict(linestyle='--', linewidth=1.5, color='#555555')
    capprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    flierprops = dict(marker='o', markerfacecolor='#777777', markersize=4, linestyle='none', alpha=0.6)

    # 繪製 Box Plot
    # whis=(0, 100) 表示鬚線延伸到最小值和最大值，不顯示離群值點
    bp = ax.boxplot(data, labels=[f"{l} chars" for l in lengths], patch_artist=True,
                    boxprops=boxprops, medianprops=medianprops,
                    whiskerprops=whiskerprops, capprops=capprops, flierprops=flierprops,
                    whis=(0, 100))
    
    # 美化設定 - 使用更柔和且專業的配色
    colors = ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2', '#95E1D3']
    color_cycle = itertools.cycle(colors)
    
    for patch in bp['boxes']:
        patch.set_facecolor(next(color_cycle))
        patch.set_alpha(0.85) # 稍微增加不透明度
    
    # 設定標題和標籤
    ax.set_title('Password Crack Time by Length (Mask Attack)\nFirsttest - Round2', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Password Length (密碼長度)', fontsize=13, labelpad=10)
    ax.set_ylabel('Crack Time in Seconds (破解時間/秒)', fontsize=13, labelpad=10)
    
    # 格線設定 - 讓格線在圖形下方
    ax.grid(axis='y', linestyle='--', alpha=0.6, color='#cccccc')
    ax.set_axisbelow(True)
    
    # 設定 Y 軸刻度 - 使用 MaxNLocator 自動選擇合適的整數刻度
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
    
    # 自動設定 Y 軸範圍，留一點空間
    all_times = [t for times in data for t in times]
    if all_times:
        max_time = max(all_times)
        # 設定上限為最大值的 1.05 倍，確保上方有空間但不要太多
        # 如果需要手動限制上限，可以修改這裡，例如: ax.set_ylim(bottom=0, top=5000)
        ax.set_ylim(bottom=0, top=74000)
    
    # 加入統計資訊 (右上角)
    stats_text = []
    for length in lengths:
        times = crack_times[length]
        if times:
            stats_text.append(f"{length}bit: n={len(times):<3} "
                            f"min={min(times):.1f}s, max={max(times):.1f}s, "
                            f"med={np.median(times):.1f}s, avg={np.mean(times):.1f}s")
    
    # 在圖上顯示統計 - 優化外觀
    if stats_text:
        textstr = '\n'.join(stats_text)
        # 使用等寬字體 (monospace) 讓數字對齊
        props = dict(boxstyle='round,pad=0.8', facecolor='#f8f9fa', alpha=0.9, edgecolor='#dddddd')
        ax.text(1.02, 1.0, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props, family='monospace')
    
    plt.tight_layout()
    
    # 儲存圖片
    output_path = os.path.join(BASE_DIR, "round2_firsttest_boxplot.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    
    plt.show()


def main():
    print("=" * 50)
    print("密碼長度 vs 破解時間 四分位距圖")
    print("資料來源: round3/firsttest/result_json/1")
    print("=" * 50)
    
    # 載入資料
    crack_times = load_crack_times()
    
    # 顯示統計
    print("\n各長度密碼破解時間統計:")
    for length in sorted(crack_times.keys()):
        times = crack_times[length]
        if times:
            print(f"  {length}位: 數量={len(times)}, "
                  f"最小={min(times):.2f}s, 最大={max(times):.2f}s, "
                  f"中位數={np.median(times):.2f}s, 平均={np.mean(times):.2f}s")
        else:
            print(f"  {length}位: 無資料")
    
    # 繪製圖表
    plot_boxplot(crack_times)


if __name__ == "__main__":
    main()
