#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 dictionary.txt 隨機抽取密碼，生成約 100MB 的字典檔
"""

import random
import os

def create_100mb_dictionary(source_file, output_file, target_size_mb=100):
    """
    從來源字典隨機抽取密碼，生成指定大小的新字典
    使用串流方式處理，避免記憶體問題
    """
    print(f"讀取來源字典: {source_file}")
    
    # 計算目標大小（字節）
    target_size = target_size_mb * 1024 * 1024
    
    # 第一步：計算總行數和平均行大小
    print("計算檔案資訊...")
    total_lines = 0
    sample_size = 0
    sample_lines = 0
    
    with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            total_lines += 1
            if i < 10000:
                sample_size += len(line.encode('utf-8'))
                sample_lines += 1
            if i % 1000000 == 0 and i > 0:
                print(f"  已處理 {i:,} 行...")
    
    avg_line_size = sample_size / sample_lines
    estimated_lines = int(target_size / avg_line_size)
    sample_rate = estimated_lines / total_lines
    
    print(f"來源字典總行數: {total_lines:,}")
    print(f"平均行大小: {avg_line_size:.2f} bytes")
    print(f"目標大小: {target_size_mb} MB")
    print(f"預估需要行數: {estimated_lines:,}")
    print(f"抽取比例: {sample_rate*100:.2f}%")
    
    # 第二步：使用隨機抽樣寫入新檔案
    print("正在隨機抽取並寫入...")
    
    current_size = 0
    written_lines = 0
    
    with open(source_file, 'r', encoding='utf-8', errors='ignore') as f_in:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for i, line in enumerate(f_in):
                # 使用隨機決定是否選擇此行
                if random.random() < sample_rate:
                    line = line.strip()
                    if line:
                        line_size = len(line.encode('utf-8')) + 1
                        
                        if current_size + line_size > target_size:
                            break
                        
                        f_out.write(line + '\n')
                        current_size += line_size
                        written_lines += 1
                
                if i % 1000000 == 0 and i > 0:
                    print(f"  已處理 {i:,} 行，已寫入 {written_lines:,} 行...")
    
    # 顯示結果
    actual_size = os.path.getsize(output_file)
    print(f"\n✓ 完成！")
    print(f"  - 檔案: {output_file}")
    print(f"  - 大小: {actual_size / 1024 / 1024:.2f} MB")
    print(f"  - 行數: {written_lines:,}")
    print(f"  - 實際抽取比例: {written_lines/total_lines*100:.2f}%")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(script_dir, "dictionary.txt")
    output = os.path.join(script_dir, "dictionary-100mb.txt")
    
    create_100mb_dictionary(source, output, target_size_mb=100)
