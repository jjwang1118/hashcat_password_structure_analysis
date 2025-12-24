"""
從 round1/firsttest/result_json/1 讀取所有密碼破解時間，
依照密碼結構類型分類並繪製 Box Plot
分類：
1. 純小寫 (Pure Lowercase)
2. 純大寫 (Pure Uppercase)
3. 混合大小寫 (Mixed Case)
4. 含數字 (With Digits) - 僅含字母與數字
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
import itertools
from matplotlib.ticker import MaxNLocator
import matplotlib.font_manager as fm

# 設定中文字體 - 自動偵測可用字體
def set_chinese_font():
    # 優先順序：微軟正黑體, 微軟雅黑, 黑體, 新細明體, Arial Unicode MS
    font_candidates = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'PMingLiU', 'MingLiU', 'Arial Unicode MS', 'Malgun Gothic']
    
    system_fonts = set(f.name for f in fm.fontManager.ttflist)
    
    for font in font_candidates:
        if font in system_fonts:
            plt.rcParams['font.sans-serif'] = [font] + plt.rcParams['font.sans-serif']
            print(f"使用字體: {font}")
            break
    else:
        # 如果沒找到，強制設定列表
        plt.rcParams['font.sans-serif'] = font_candidates + plt.rcParams['font.sans-serif']

    plt.rcParams['axes.unicode_minus'] = False

set_chinese_font()

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 包含 round1 和 round3 的資料來源
RESULT_JSON_DIRS = [
    os.path.join(BASE_DIR, "..", "..", "round1", "firsttest", "result_json", "1"),
    os.path.join(BASE_DIR, "..", "..", "round3", "firsttest", "result_json", "1")
]

def get_password_type(password):
    """
    判斷密碼類型
    Returns: str or None
    """
    if not password:
        return None
        
    # 1. 純小寫: 全是字母且全是小寫
    if password.isalpha() and password.islower():
        return "Pure Lowercase"
    
    # 2. 純大寫: 全是字母且全是大寫
    if password.isalpha() and password.isupper():
        return "Pure Uppercase"
        
    # 3. 混合大小寫: 全是字母，非純小寫也非純大寫
    if password.isalpha():
        return "Mixed Case"
        
    # 4. 含數字: 僅含字母和數字 (排除特殊符號)，且必須包含數字
    if password.isalnum() and any(c.isdigit() for c in password):
        return "With Digits"
        
    return None

def load_crack_times():
    """
    讀取所有 JSON 檔案，按密碼長度與類型分類破解時間
    Returns: dict {length: {type: [times]}}
    """
    # 定義分類順序
    categories = ["Pure Lowercase", "Pure Uppercase", "Mixed Case", "With Digits"]
    # 初始化結構
    crack_times = {} 
    
    # 遍歷所有來源目錄
    for result_dir in RESULT_JSON_DIRS:
        if not os.path.exists(result_dir):
            print(f"警告: 目錄不存在 {result_dir}")
            continue

        # 遍歷所有資料夾 (basic8 ~ basic12)
        for folder_name in os.listdir(result_dir):
            folder_path = os.path.join(result_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
                
            # 從資料夾名稱提取長度 (如 convert_basic8 -> 8)
            try:
                length = int(folder_name.replace("convert_basic", ""))
            except ValueError:
                continue
                
            if length not in crack_times:
                crack_times[length] = {cat: [] for cat in categories}
                
            # 讀取該資料夾內所有 JSON
            for json_file in os.listdir(folder_path):
                if not json_file.endswith(".json"):
                    continue
                
                json_path = os.path.join(folder_path, json_file)
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    if data.get("Status") == "Cracked":
                        password = data.get("Cracked_Password")
                        runtime = data.get("Actual_Runtime_Seconds", 0)
                        
                        pwd_type = get_password_type(password)
                        if pwd_type in categories:
                            crack_times[length][pwd_type].append(runtime)
                            
                except Exception as e:
                    print(f"讀取 {json_path} 失敗: {e}")
    
    return crack_times

def plot_boxplot(crack_times):
    """
    繪製 Box Plot (分長度)
    """
    categories = ["Pure Lowercase", "Pure Uppercase", "Mixed Case", "With Digits"]
    labels_map = {
        "Pure Lowercase": "\n(Pure Lower)",
        "Pure Uppercase": "\n(Pure Upper)",
        "Mixed Case": "\n(Mixed Case)",
        "With Digits": "\n(With Digits)"
    }
    
    lengths = sorted(crack_times.keys())
    if not lengths:
        print("無資料可繪圖")
        return

    # 準備繪圖資料列表：先加入各長度的資料
    plot_items = [(length, crack_times[length]) for length in lengths]
    
    # 計算並加入「全部混合」的資料
    combined_data = {cat: [] for cat in categories}
    for length in lengths:
        for cat in categories:
            combined_data[cat].extend(crack_times[length][cat])
    plot_items.append(("All Lengths (Combined)", combined_data))

    # 建立子圖 (每行最多 3 個)
    cols = 3
    total_plots = len(plot_items)
    rows = (total_plots + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 6 * rows + 2), sharey=False)
    
    # 確保 axes 是列表
    if rows == 1 and cols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    # 樣式設定
    boxprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    medianprops = dict(linestyle='-', linewidth=2, color='#D35400')
    whiskerprops = dict(linestyle='--', linewidth=1.5, color='#555555')
    capprops = dict(linestyle='-', linewidth=1.5, color='#555555')
    flierprops = dict(marker='o', markerfacecolor='#777777', markersize=4, linestyle='none', alpha=0.6)
    colors = ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2']
    
    for idx, (title_key, data_source) in enumerate(plot_items):
        ax = axes[idx]
        data = [data_source[cat] for cat in categories]
        labels = [labels_map[cat] for cat in categories]
        
        # 繪製 Box Plot
        bp = ax.boxplot(data, labels=labels, patch_artist=True,
                        boxprops=boxprops, medianprops=medianprops,
                        whiskerprops=whiskerprops, capprops=capprops, flierprops=flierprops,
                        whis=(0, 100))
        
        # 上色
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
            
        # 設定標題與標籤
        if isinstance(title_key, int):
            ax.set_title(f'Password Length: {title_key} chars', fontsize=14, fontweight='bold')
        else:
            ax.set_title(title_key, fontsize=14, fontweight='bold', color='#2c3e50')

        if idx % cols == 0:
            ax.set_ylabel('Crack Time (s)', fontsize=12)
        
        # 格線與刻度
        ax.grid(axis='y', linestyle='--', alpha=0.6, color='#cccccc')
        ax.set_axisbelow(True)
        
        # 自動調整 Y 軸上限
        all_times = [t for times in data for t in times]
        if all_times:
            max_time = max(all_times)
            ax.set_ylim(bottom=0, top=max_time * 1.1)
            
        # 加入統計資訊 (移至下方)
        stats_text = []
        for cat in categories:
            times = data_source[cat]
            cat_name = labels_map[cat].replace('\n', ' ')
            if times:
                stats_text.append(f"{cat_name}: n={len(times)} "
                                f"min={min(times):.1f}s, max={max(times):.1f}s, "
                                f"med={np.median(times):.1f}s, avg={np.mean(times):.1f}s")
            else:
                # stats_text.append(f"{cat_name}: No Data")
                pass
                
        if stats_text:
            textstr = '\n'.join(stats_text)
            props = dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', alpha=0.9, edgecolor='#dddddd')
            # 調整文字位置
            ax.text(0.5, -0.15, textstr, transform=ax.transAxes, fontsize=9,
                    verticalalignment='top', horizontalalignment='center', bbox=props, family='monospace')

    # 隱藏多餘的子圖
    for i in range(total_plots, len(axes)):
        axes[i].axis('off')

    fig.suptitle('Crack Time by Password Complexity Structure (Round1 & Round3)', fontsize=18, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    
    # 創建統一的輸出目錄
    output_dir = os.path.join(BASE_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "complexity_time.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.show()

def main():
    print("=" * 60)
    print("密碼結構複雜度 vs 破解時間 分析")
    print("資料來源: round1 & round3 / firsttest / result_json / 1")
    print("=" * 60)
    
    crack_times = load_crack_times()
    
    # 文字輸出
    categories = ["Pure Lowercase", "Pure Uppercase", "Mixed Case", "With Digits"]
    for length in sorted(crack_times.keys()):
        print(f"\n[Length {length}]")
        for cat in categories:
            times = crack_times[length][cat]
            if times:
                print(f"  {cat}: Count={len(times)}, "
                      f"Min={min(times):.2f}s, Max={max(times):.2f}s, "
                      f"Med={np.median(times):.2f}s, Avg={np.mean(times):.2f}s")
            else:
                print(f"  {cat}: No Data")
            
    plot_boxplot(crack_times)

if __name__ == "__main__":
    main()
