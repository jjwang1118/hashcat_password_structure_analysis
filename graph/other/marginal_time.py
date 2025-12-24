"""
分析 secondtest 中基礎長度與附加長度對破解時間的影響
資料來源: round1 和 round3 的 secondtest/result_json/1
檔案夾命名格式: convert_basic{BaseLength}+{AddedLength}
"""

import json
import os
import glob
import re
import statistics
import matplotlib.pyplot as plt
import numpy as np

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Malgun Gothic', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

def process_json_files(base_dirs):
    """
    讀取所有 JSON 檔案，按基礎長度和附加長度分類
    Returns: dict {base_length: {added_length: [times]}}
    """
    results = {}
    folder_pattern = re.compile(r"convert_basic(\d+)\+(\d+)")
    
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            print(f"警告: 目錄不存在 {base_dir}")
            continue
            
        print(f"正在掃描: {base_dir}")
        
        # 遍歷所有資料夾
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            match = folder_pattern.match(folder_name)
            if not match:
                continue
            
            base_length = int(match.group(1))
            added_length = int(match.group(2))
            
            # 初始化結構
            if base_length not in results:
                results[base_length] = {}
            if added_length not in results[base_length]:
                results[base_length][added_length] = []
            
            # 讀取該資料夾內所有 JSON
            for json_file in os.listdir(folder_path):
                if not json_file.endswith(".json"):
                    continue
                
                json_path = os.path.join(folder_path, json_file)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    if data.get("Status") == "Cracked":
                        runtime = data.get("Actual_Runtime_Seconds", 0)
                        results[base_length][added_length].append(runtime)
                except Exception as e:
                    print(f"讀取 {json_path} 失敗: {e}")
    
    return results

def plot_fixed_added_length(results):
    """
    圖表1: 固定附加長度，比較不同基礎長度的時間差異
    """
    # 找出所有存在的附加長度
    all_added_lengths = set()
    for base_data in results.values():
        all_added_lengths.update(base_data.keys())
    
    added_lengths = sorted(all_added_lengths)
    base_lengths = sorted(results.keys())
    
    # 為每個附加長度創建一個子圖
    n_plots = len(added_lengths)
    fig, axes = plt.subplots(1, n_plots, figsize=(5*n_plots, 8), sharey=False)
    if n_plots == 1:
        axes = [axes]
    
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#FFE66D']
    
    for idx, added_len in enumerate(added_lengths):
        ax = axes[idx]
        
        # 準備數據
        plot_data = []
        labels = []
        valid_colors = []
        
        for base_len in base_lengths:
            if added_len in results[base_len] and results[base_len][added_len]:
                plot_data.append(results[base_len][added_len])
                labels.append(f"Base {base_len}")
                valid_colors.append(colors[base_len % len(colors)])
        
        if plot_data:
            bp = ax.boxplot(plot_data, tick_labels=labels, patch_artist=True, whis=(0, 100))
            for patch, color in zip(bp['boxes'], valid_colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        
        ax.set_title(f'Added Length: +{added_len}', fontsize=12, fontweight='bold')
        ax.set_ylabel('Time (Seconds)', fontsize=10)
        ax.set_xlabel('Base Length', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        # 添加統計資訊
        stats_text = []
        for i, base_len in enumerate(base_lengths):
            if added_len in results[base_len] and results[base_len][added_len]:
                times = results[base_len][added_len]
                stats_text.append(f"Base{base_len}: n={len(times)}, med={statistics.median(times):.1f}s")
        
        if stats_text:
            textstr = '\n'.join(stats_text)
            props = dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.7)
            ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=8,
                    verticalalignment='top', bbox=props, family='monospace')
    
    fig.suptitle('Fixed Added Length: Compare Base Lengths', fontsize=16, fontweight='bold', y=0.96)
    
    # 添加統計表格到圖表底部
    table_data = []
    for added_len in added_lengths:
        row = [f"+{added_len}"]
        for base_len in base_lengths:
            if added_len in results[base_len] and results[base_len][added_len]:
                times = results[base_len][added_len]
                row.append(f"n={len(times)}, med={statistics.median(times):.1f}s")
            else:
                row.append("N/A")
        table_data.append(row)
    
    col_labels = ['Added'] + [f'Base {bl}' for bl in base_lengths]
    
    # 在圖表底部創建表格
    table_ax = fig.add_axes([0.15, -0.1, 0.7, 0.10])  # [left, bottom, width, height]
    table_ax.axis('off')
    
    the_table = table_ax.table(cellText=table_data,
                         colLabels=col_labels,
                         loc='center',
                         cellLoc='center',
                         colWidths=[0.15] + [0.28]*len(base_lengths))
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(9)
    the_table.scale(1, 2)
    
    for i in range(len(col_labels)):
        the_table[(0, i)].set_facecolor('#E8E8E8')
        the_table[(0, i)].set_text_props(weight='bold')
    
    plt.subplots_adjust(bottom=0.12, top=0.92, left=0.05, right=0.98)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "marginal_time_fixed_added.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.close()

def plot_fixed_base_length(results):
    """
    圖表2: 固定基礎長度，比較不同附加長度的時間增長
    """
    base_lengths = sorted(results.keys())
    
    fig, axes = plt.subplots(1, len(base_lengths), figsize=(6*len(base_lengths), 7), sharey=False)
    if len(base_lengths) == 1:
        axes = [axes]
    
    colors = ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2']
    
    for idx, base_len in enumerate(base_lengths):
        ax = axes[idx]
        
        # 準備數據
        added_lengths = sorted(results[base_len].keys())
        plot_data = []
        labels = []
        valid_colors = []
        
        for added_len in added_lengths:
            if results[base_len][added_len]:
                plot_data.append(results[base_len][added_len])
                labels.append(f"+{added_len}")
                valid_colors.append(colors[(added_len-1) % len(colors)])
        
        if plot_data:
            bp = ax.boxplot(plot_data, tick_labels=labels, patch_artist=True, whis=(0, 100))
            for patch, color in zip(bp['boxes'], valid_colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.85)
        
        ax.set_title(f'Base Length: {base_len}', fontsize=12, fontweight='bold')
        ax.set_ylabel('Time (Seconds)', fontsize=10)
        ax.set_xlabel('Added Length', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        # 添加統計表格
        cell_text = []
        for added_len in added_lengths:
            if results[base_len][added_len]:
                times = results[base_len][added_len]
                cell_text.append([
                    f"+{added_len}",
                    f"{len(times)}",
                    f"{min(times):.1f}s",
                    f"{statistics.median(times):.1f}s",
                    f"{max(times):.1f}s",
                    f"{statistics.mean(times):.1f}s"
                ])
        
        if cell_text:
            columns = ['Add', 'n', 'Min', 'Med', 'Max', 'Avg']
            table = ax.table(cellText=cell_text,
                            colLabels=columns,
                            loc='bottom',
                            bbox=[0.0, -0.35, 1.0, 0.25],
                            cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            
            for i in range(len(columns)):
                table[(0, i)].set_facecolor('#E8E8E8')
                table[(0, i)].set_text_props(weight='bold')
            
            plt.subplots_adjust(bottom=0.35)
    
    fig.suptitle('Fixed Base Length: Compare Added Lengths', fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "marginal_time_fixed_base.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.close()

def plot_base_length_marginal(results):
    """
    圖表3: 基礎長度邊際效應（增加一個一般字符的效應）
    固定附加長度，分析基礎長度增加的邊際效應
    合併成單一圖表，不同顏色代表不同附加長度
    """
    # 找出所有存在的附加長度
    all_added_lengths = set()
    for base_data in results.values():
        all_added_lengths.update(base_data.keys())
    
    added_lengths = sorted(all_added_lengths)
    base_lengths = sorted(results.keys())
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    markers = ['o', 's', '^', 'D']
    
    # 收集所有數據並繪製在同一張圖上
    all_marginal_data = []
    
    for idx, added_len in enumerate(added_lengths):
        # 收集該附加長度下所有基礎長度的平均時間
        base_avg_times = []
        valid_base_lengths = []
        
        for base_len in base_lengths:
            if added_len in results[base_len] and results[base_len][added_len]:
                avg_time = statistics.mean(results[base_len][added_len])
                base_avg_times.append(avg_time)
                valid_base_lengths.append(base_len)
        
        if len(valid_base_lengths) > 1:
            # 繪製折線圖
            line = ax.plot(valid_base_lengths, base_avg_times, 
                          marker=markers[idx % len(markers)], linewidth=2.5, 
                          markersize=10, color=colors[idx % len(colors)], 
                          label=f'Special Chars: +{added_len}', alpha=0.85)
            
            # 添加數值標籤
            for x, y in zip(valid_base_lengths, base_avg_times):
                ax.annotate(f'{y:.1f}s', xy=(x, y), xytext=(0, 8), 
                           textcoords='offset points', ha='center', fontsize=8,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                   edgecolor=colors[idx % len(colors)], alpha=0.8))
            
            # 計算邊際增長率用於表格
            for i in range(1, len(valid_base_lengths)):
                prev_time = base_avg_times[i-1]
                curr_time = base_avg_times[i]
                growth_rate = ((curr_time - prev_time) / prev_time) * 100
                time_diff = curr_time - prev_time
                all_marginal_data.append({
                    'added': added_len,
                    'transition': f"{valid_base_lengths[i-1]}→{valid_base_lengths[i]}",
                    'diff': time_diff,
                    'rate': growth_rate
                })
    
    ax.set_xlabel('Base Length (一般字符數量)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Average Cracking Time (Seconds)', fontsize=13, fontweight='bold')
    ax.set_title('Marginal Effect of Adding One Normal Character\n增加一個一般字符的邊際時間效應', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(base_lengths)
    ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加邊際增長率表格
    if all_marginal_data:
        table_data = []
        for data in all_marginal_data:
            table_data.append([
                f"+{data['added']}",
                data['transition'],
                f"+{data['diff']:.1f}s",
                f"{data['rate']:.1f}%"
            ])
        
        col_labels = ['Special\nChars', 'Base Length\nTransition', 'Time\nDifference', 'Growth\nRate']
        
        table_ax = fig.add_axes([0.15, -0.35, 0.7, 0.15])
        table_ax.axis('off')
        
        the_table = table_ax.table(cellText=table_data,
                             colLabels=col_labels,
                             loc='center',
                             cellLoc='center',
                             colWidths=[0.15, 0.25, 0.25, 0.2])
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(9)
        the_table.scale(1, 2)
        
        for i in range(len(col_labels)):
            the_table[(0, i)].set_facecolor('#E8E8E8')
            the_table[(0, i)].set_text_props(weight='bold')
        
        # 為不同特殊字符數量設置不同顏色
        for i, row_data in enumerate(table_data):
            added_idx = int(row_data[0].replace('+', '')) - 1
            for j in range(len(col_labels)):
                the_table[(i+1, j)].set_facecolor(colors[added_idx % len(colors)])
                the_table[(i+1, j)].set_alpha(0.15)
    
    # 添加說明文字
    formula_text = 'Growth Rate (%) = ((Avg Time at Base N) - (Avg Time at Base N-1)) / (Avg Time at Base N-1) × 100%'
    fig.text(0.5, 0.01, formula_text, ha='center', fontsize=9, 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='gray', alpha=0.8),
             family='monospace')
    
    plt.subplots_adjust(bottom=0.24, top=0.92, left=0.08, right=0.96)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "marginal_base_length_effect.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.close()

def plot_growth_rate(results):
    """
    圖表4: 時間增長率分析（折線圖）- 附加長度效應
    """
    base_lengths = sorted(results.keys())
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 左圖：平均時間隨附加長度變化
    for base_len in base_lengths:
        added_lengths = sorted(results[base_len].keys())
        avg_times = []
        
        for added_len in added_lengths:
            if results[base_len][added_len]:
                avg_times.append(statistics.mean(results[base_len][added_len]))
            else:
                avg_times.append(None)
        
        # 過濾 None 值
        valid_points = [(x, y) for x, y in zip(added_lengths, avg_times) if y is not None]
        if valid_points:
            x_vals, y_vals = zip(*valid_points)
            ax1.plot(x_vals, y_vals, marker='o', linewidth=2, markersize=8, label=f'Base {base_len}')
            
            # 添加數值標籤
            for x, y in zip(x_vals, y_vals):
                ax1.annotate(f'{y:.1f}', xy=(x, y), xytext=(0, 8), 
                            textcoords='offset points', ha='center', fontsize=8,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.7))
    
    ax1.set_xlabel('Added Length', fontsize=12)
    ax1.set_ylabel('Average Time (Seconds)', fontsize=12)
    ax1.set_title('Average Time vs Added Length', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 右圖：時間增長率（相對於 +1）
    for base_len in base_lengths:
        added_lengths = sorted(results[base_len].keys())
        if 1 not in results[base_len] or not results[base_len][1]:
            continue
        
        base_time = statistics.mean(results[base_len][1])
        growth_rates = []
        valid_added = []
        
        for added_len in added_lengths:
            if results[base_len][added_len]:
                avg_time = statistics.mean(results[base_len][added_len])
                growth_rate = ((avg_time - base_time) / base_time) * 100
                growth_rates.append(growth_rate)
                valid_added.append(added_len)
        
        if growth_rates:
            ax2.plot(valid_added, growth_rates, marker='s', linewidth=2, markersize=8, label=f'Base {base_len}')
            
            # 添加數值標籤
            for x, y in zip(valid_added, growth_rates):
                ax2.annotate(f'{y:.1f}%', xy=(x, y), xytext=(0, 8), 
                            textcoords='offset points', ha='center', fontsize=8,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.7))
    
    ax2.set_xlabel('Added Length', fontsize=12)
    ax2.set_ylabel('Growth Rate (%)', fontsize=12)
    ax2.set_title('Time Growth Rate (Relative to +1)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # 添加計算公式說明
    formula_text = (
        'Left: Avg Time = mean(all cracked times for each (base, added) pair)\n'
        'Right: Growth Rate (%) = ((Avg Time at +N) - (Avg Time at +1)) / (Avg Time at +1) × 100%'
    )
    fig.text(0.5, 0.01, formula_text, ha='center', fontsize=9, 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='gray', alpha=0.8),
             family='monospace')
    
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "marginal_time_growth_rate.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.close()

def plot_added_length_marginal(results):
    """
    圖表5: 附加長度邊際效應（增加一個特殊字符的效應）
    固定基礎長度，分析附加長度增加的邊際效應
    合併成單一圖表，不同顏色代表不同基礎長度
    """
    base_lengths = sorted(results.keys())
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3', '#FFE66D']
    markers = ['o', 's', '^', 'D']
    
    # 收集所有數據並繪製在同一張圖上
    all_marginal_data = []
    
    for idx, base_len in enumerate(base_lengths):
        # 收集該基礎長度下所有附加長度的平均時間
        added_avg_times = []
        valid_added_lengths = []
        
        added_lengths = sorted(results[base_len].keys())
        
        for added_len in added_lengths:
            if results[base_len][added_len]:
                avg_time = statistics.mean(results[base_len][added_len])
                added_avg_times.append(avg_time)
                valid_added_lengths.append(added_len)
        
        if len(valid_added_lengths) > 1:
            # 繪製折線圖
            line = ax.plot(valid_added_lengths, added_avg_times, 
                          marker=markers[idx % len(markers)], linewidth=2.5, 
                          markersize=10, color=colors[idx % len(colors)], 
                          label=f'Base Length: {base_len}', alpha=0.85)
            
            # 添加數值標籤
            for x, y in zip(valid_added_lengths, added_avg_times):
                ax.annotate(f'{y:.1f}s', xy=(x, y), xytext=(0, 8), 
                           textcoords='offset points', ha='center', fontsize=8,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                   edgecolor=colors[idx % len(colors)], alpha=0.8))
            
            # 計算邊際增長率用於表格
            for i in range(1, len(valid_added_lengths)):
                prev_time = added_avg_times[i-1]
                curr_time = added_avg_times[i]
                growth_rate = ((curr_time - prev_time) / prev_time) * 100
                time_diff = curr_time - prev_time
                all_marginal_data.append({
                    'base': base_len,
                    'transition': f"+{valid_added_lengths[i-1]}→+{valid_added_lengths[i]}",
                    'diff': time_diff,
                    'rate': growth_rate
                })
    
    ax.set_xlabel('Added Length (特殊字符數量)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Average Cracking Time (Seconds)', fontsize=13, fontweight='bold')
    ax.set_title('Marginal Effect of Adding One Special Character\n增加一個特殊字符的邊際時間效應', 
                fontsize=15, fontweight='bold', pad=20)
    
    # 設定 x 軸刻度
    all_added_lengths = set()
    for base_data in results.values():
        all_added_lengths.update(base_data.keys())
    ax.set_xticks(sorted(all_added_lengths))
    
    ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加邊際增長率表格
    if all_marginal_data:
        table_data = []
        for data in all_marginal_data:
            table_data.append([
                f"Base {data['base']}",
                data['transition'],
                f"+{data['diff']:.1f}s",
                f"{data['rate']:.1f}%"
            ])
        
        col_labels = ['Base\nLength', 'Added Length\nTransition', 'Time\nDifference', 'Growth\nRate']
        
        table_ax = fig.add_axes([0.15, -0.35, 0.7, 0.15])
        table_ax.axis('off')
        
        the_table = table_ax.table(cellText=table_data,
                             colLabels=col_labels,
                             loc='center',
                             cellLoc='center',
                             colWidths=[0.15, 0.25, 0.25, 0.2])
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(9)
        the_table.scale(1, 2)
        
        for i in range(len(col_labels)):
            the_table[(0, i)].set_facecolor('#E8E8E8')
            the_table[(0, i)].set_text_props(weight='bold')
        
        # 為不同基礎長度設置不同顏色
        for i, row_data in enumerate(table_data):
            base_idx = int(row_data[0].replace('Base ', '')) - min(base_lengths)
            for j in range(len(col_labels)):
                the_table[(i+1, j)].set_facecolor(colors[base_idx % len(colors)])
                the_table[(i+1, j)].set_alpha(0.15)
    
    # 添加說明文字
    formula_text = 'Growth Rate (%) = ((Avg Time at +N) - (Avg Time at +N-1)) / (Avg Time at +N-1) × 100%'
    fig.text(0.5, 0.01, formula_text, ha='center', fontsize=9, 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='gray', alpha=0.8),
             family='monospace')
    
    plt.subplots_adjust(bottom=0.24, top=0.92, left=0.08, right=0.96)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "marginal_added_length_effect.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"圖片已儲存至: {output_path}")
    plt.close()

def print_summary(results):
    """輸出詳細統計摘要"""
    print("\n" + "="*80)
    print("邊際效應分析摘要")
    print("="*80)
    
    for base_len in sorted(results.keys()):
        print(f"\n[基礎長度: {base_len}]")
        for added_len in sorted(results[base_len].keys()):
            times = results[base_len][added_len]
            if times:
                print(f"  +{added_len}: n={len(times)}, "
                      f"min={min(times):.2f}s, max={max(times):.2f}s, "
                      f"avg={statistics.mean(times):.2f}s, med={statistics.median(times):.2f}s")
            else:
                print(f"  +{added_len}: 無資料")

def main():
    print("="*80)
    print("邊際長度效應分析 (Base Length vs Added Length)")
    print("資料來源: round1 & round3 / secondtest / result_json / 1")
    print("="*80)
    
    # 設定路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exam_dir = os.path.dirname(os.path.dirname(script_dir))
    
    target_dirs = [
        os.path.join(exam_dir, "round1", "secondtest", "result_json", "1"),
        os.path.join(exam_dir, "round3", "secondtest", "result_json", "1"),
    ]
    
    # 處理資料
    results = process_json_files(target_dirs)
    
    # 輸出統計摘要
    print_summary(results)
    
    # 生成圖表
    print("\n" + "="*80)
    print("正在生成圖表...")
    print("="*80)
    
    plot_fixed_added_length(results)
    plot_fixed_base_length(results)
    plot_base_length_marginal(results)
    plot_added_length_marginal(results)
    plot_growth_rate(results)
    
    print("\n所有圖表已生成完成！")

if __name__ == "__main__":
    main()
