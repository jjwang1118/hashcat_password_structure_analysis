#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - 自動執行所有測試流程
按順序執行：gen_mask.py → run_m.py
"""

import subprocess
import sys
import os
import glob
from datetime import datetime

def check_csv_files_exist():
    """檢查 CSV 檔案是否已存在"""
    if __file__:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir = os.path.abspath(os.getcwd())
    
    # 檢查 mask_data 目錄
    firsttest_mask = os.path.join(script_dir, "firsttest", "result", "mask_data")
    secondtest_mask = os.path.join(script_dir, "secondtest", "result", "mask_data")
    
    # 檢查 dict_data 目錄
    firsttest_dict = os.path.join(script_dir, "firsttest", "result", "dict_data")
    secondtest_dict = os.path.join(script_dir, "secondtest", "result", "dict_data")
    
    # 預期的 CSV 檔案數量：firsttest 5個 + secondtest 4個 = 9個
    expected_mask_count = 9  # convert_basic8-12.csv (5) + convert_basic8+1-4.csv (4)
    expected_dict_count = 9  # basic8-12_d.csv (5) + basic8+1-4_d.csv (4)
    
    mask_files = []
    dict_files = []
    
    if os.path.exists(firsttest_mask):
        mask_files.extend(glob.glob(os.path.join(firsttest_mask, "*.csv")))
    if os.path.exists(secondtest_mask):
        mask_files.extend(glob.glob(os.path.join(secondtest_mask, "*.csv")))
    
    if os.path.exists(firsttest_dict):
        dict_files.extend(glob.glob(os.path.join(firsttest_dict, "*.csv")))
    if os.path.exists(secondtest_dict):
        dict_files.extend(glob.glob(os.path.join(secondtest_dict, "*.csv")))
    
    has_mask = len(mask_files) >= expected_mask_count
    has_dict = len(dict_files) >= expected_dict_count
    
    return has_mask, has_dict, len(mask_files), len(dict_files)

def print_header(message):
    """列印標題"""
    print("\n" + "="*70)
    print(f"  {message}")
    print("="*70 + "\n")

def print_step(step_num, total_steps, script_name):
    """列印步驟資訊"""
    print(f"\n{'='*70}")
    print(f"  步驟 [{step_num}/{total_steps}]: 執行 {script_name}")
    print(f"  時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

def run_script(script_name, description):
    """執行指定的 Python 腳本"""
    if __file__:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        base_dir = os.path.abspath(os.getcwd())
    script_path = os.path.join(base_dir, script_name)
    
    if not os.path.exists(script_path):
        print(f"[ERROR] 找不到腳案：{script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            cwd=base_dir
        )
        
        print(f"\n{'─'*70}")
        print(f"✓ {script_name} 執行完成")
        print(f"{'─'*70}\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n{'─'*70}")
        print(f"✗ {script_name} 執行失敗")
        print(f"  返回碼：{e.returncode}")
        print(f"{'─'*70}\n")
        return False
    except Exception as e:
        print(f"\n{'─'*70}")
        print(f"✗ {script_name} 發生錯誤：{str(e)}")
        print(f"{'─'*70}\n")
        return False

def main():
    """主執行流程"""
    start_time = datetime.now()
    
    print_header("開始執行完整測試流程")
    if __file__:
        exec_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        exec_dir = os.path.abspath(os.getcwd())
    print(f"執行目錄: {exec_dir}")
    print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查 CSV 檔案是否已存在
    has_mask, has_dict, mask_count, dict_count = check_csv_files_exist()
    
    print(f"\n[檢查] Mask CSV 檔案: {mask_count} 個 {'(已存在)' if has_mask else '(需要生成)'}")
    print(f"[檢查] Dict CSV 檔案: {dict_count} 個 {'(已存在)' if has_dict else '(需要生成)'}")
    
    # 定義執行順序
    scripts = []
    
    # 如果 Mask CSV 不存在，需要執行 gen_mask.py
    if not has_mask:
        scripts.append(("gen_mask.py", "生成 Mask Attack 的 CSV 資料"))
    else:
        print(f"\n[跳過] gen_mask.py - Mask CSV 檔案已存在")
    
    # 始終執行驗證和測試
    scripts.extend([
        ("run_all.py", "執行所有 Hashcat 測試 (Mask Attack)")
    ])
    
    total_steps = len(scripts)
    success_count = 0
    
    # 按順序執行每個腳本
    for i, (script, description) in enumerate(scripts, 1):
        print_step(i, total_steps, script)
        print(f"說明: {description}\n")
        
        if run_script(script, description):
            success_count += 1
        else:
            print(f"\n[ERROR] {script} 執行失敗，停止後續執行")
            print(f"[INFO] 已成功完成 {success_count}/{total_steps} 個步驟")
            sys.exit(1)
    
    # 執行完成
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    
    print_header("所有測試流程執行完成！")
    print(f"成功執行: {success_count}/{total_steps} 個腳本")
    print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"總耗時: {elapsed_time}")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] 使用者中斷執行")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERROR] 發生未預期的錯誤：{str(e)}")
        sys.exit(1)
