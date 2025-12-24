#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 data 目錄的 txt 檔案讀取密碼，轉換成 SHA-1 hash 和 mask，輸出為 CSV
"""

import os
import hashlib
import pandas as pd
import glob

# 特殊字元集合（包含所有實際使用的特殊字符）
SPECIAL_CHARS = "#@!^%$^&"

def generate_sha1(password):
    """生成密碼的 SHA-1 hash (hashcat mode 100)"""
    return hashlib.sha1(password.encode('utf-8')).hexdigest()

def generate_mask_for_password(password):
    """根據密碼生成對應的 mask"""
    mask = ""
    for char in password:
        if char.isupper():
            mask += "?u"
        elif char.islower():
            mask += "?l"
        elif char.isdigit():
            mask += "?d"
        elif char in SPECIAL_CHARS:
            mask += "?s"  # 使用標準特殊字符，由 run_m.py 負責替換為 ?1
        else:
            mask += "?a"  # 其他字元
    return mask

def read_passwords_from_txt(txt_file):
    """從 txt 檔案讀取密碼"""
    passwords = []
    with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            pwd = line.strip()
            if pwd:
                passwords.append(pwd)
    return passwords

def check_csv_valid(csv_file, expected_length, expected_special_count=None):
    """檢查 CSV 是否存在且內容符合條件"""
    if not os.path.exists(csv_file):
        return False
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        if df.empty or 'password' not in df.columns:
            return False
        
        # 檢查每個密碼的長度
        for pwd in df['password']:
            if len(pwd) != expected_length:
                return False
            
            # 如果指定了特殊字符數量，也要檢查
            if expected_special_count is not None:
                special_count = sum(1 for c in pwd if c in SPECIAL_CHARS)
                if special_count != expected_special_count:
                    return False
        
        return True
    except Exception as e:
        print(f"  [WARNING] 檢查 {os.path.basename(csv_file)} 時出錯: {e}")
        return False

def remove_existing_csvs(mask_data_dir):
    """刪除現有的 CSV 檔案並記錄檔名"""
    csv_files = glob.glob(os.path.join(mask_data_dir, "*.csv"))
    removed_files = []
    
    for csv_file in csv_files:
        basename = os.path.basename(csv_file)
        removed_files.append(basename)
        os.remove(csv_file)
    
    return removed_files


def main():
    # 取得腳本所在目錄（使用更健壯的方式）
    if __file__:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir = os.path.abspath(os.getcwd())
    
    print(f"[工作目錄] {script_dir}")
    
    # 建立輸出目錄
    firsttest_mask_dir = os.path.join(script_dir, "firsttest", "result", "mask_data")
    secondtest_mask_dir = os.path.join(script_dir, "secondtest", "result", "mask_data")
    os.makedirs(firsttest_mask_dir, exist_ok=True)
    os.makedirs(secondtest_mask_dir, exist_ok=True)
    
    print("="*60)
    print("開始處理密碼轉換")
    print("="*60)
    
    # 設定固定隨機種子，確保每次執行結果一致
    import random
    random.seed(42)
    print("\n[資料一致性保護] 已設定固定隨機種子 (seed=42)")
    
    # Part 1: firsttest - 從 data/ 目錄讀取 basic{8-12}.txt
    print("\n[Part 1] 處理 firsttest 密碼...")
    firsttest_data_dir = os.path.join(script_dir, "firsttest", "data")
    
    for length in [8, 9, 10, 11, 12]:
        txt_file = os.path.join(firsttest_data_dir, f"basic{length}.txt")
        
        if not os.path.exists(txt_file):
            print(f"  ⚠ 找不到: {os.path.basename(txt_file)}")
            continue
        
        # 讀取密碼
        passwords = read_passwords_from_txt(txt_file)
        
        # 長度 11 和 12 隨機抽取 5 個
        if length in [11, 12] and len(passwords) > 5:
            passwords = random.sample(passwords, 5)
            print(f"\n  處理: {os.path.basename(txt_file)} (隨機抽取 {len(passwords)}/10 個密碼)")
        else:
            print(f"\n  處理: {os.path.basename(txt_file)} ({len(passwords)} 個密碼)")
        
        # 轉換為 CSV 資料
        data = []
        for pwd in passwords:
            mask = generate_mask_for_password(pwd)
            hash_value = generate_sha1(pwd)
            data.append({
                'password': pwd,
                'hashvalue': hash_value,
                'mask': mask
            })
        
        # 寫入 CSV（智慧跳過）
        df = pd.DataFrame(data)
        csv_file = os.path.join(firsttest_mask_dir, f"convert_basic{length}.csv")
        
        if check_csv_valid(csv_file, length):
            print(f"  [SKIP] convert_basic{length}.csv 已存在且有效，跳過生成")
        else:
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"  ✓ 生成: convert_basic{length}.csv ({len(passwords)} 行)")
        # 顯示前3個樣本
        for i, pwd in enumerate(passwords[:3], 1):
            print(f"     {i}. {pwd} → {generate_mask_for_password(pwd)}")
    
    # Part 2: secondtest - 從 data/len8/ 和 data/len9/ 讀取
    print("\n[Part 3] 處理 secondtest 密碼...")
    secondtest_data_dir = os.path.join(script_dir, "secondtest", "data")
    
    # 處理長度 8 (len8 目錄)
    len8_dir = os.path.join(secondtest_data_dir, "len8")
    for special_count in [1, 2, 3, 4]:
        txt_file = os.path.join(len8_dir, f"basic8+{special_count}.txt")
        
        if not os.path.exists(txt_file):
            print(f"  ⚠ 找不到: basic8+{special_count}.txt")
            continue
        
        # 讀取密碼
        passwords = read_passwords_from_txt(txt_file)
        print(f"\n  處理: len8/basic8+{special_count}.txt ({len(passwords)} 個密碼)")
        
        # 轉換為 CSV 資料
        data = []
        for pwd in passwords:
            mask = generate_mask_for_password(pwd)
            hash_value = generate_sha1(pwd)
            data.append({
                'password': pwd,
                'hashvalue': hash_value,
                'mask': mask
            })
        
        # 寫入 CSV（智慧跳過）
        df = pd.DataFrame(data)
        csv_file = os.path.join(secondtest_mask_dir, f"convert_basic8+{special_count}.csv")
        
        if check_csv_valid(csv_file, 8, special_count):
            print(f"  [SKIP] convert_basic8+{special_count}.csv 已存在且有效，跳過生成")
        else:
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"  ✓ 生成: convert_basic8+{special_count}.csv ({len(passwords)} 行)")
        # 顯示前3個樣本
        for i, pwd in enumerate(passwords[:3], 1):
            print(f"     {i}. {pwd} → {generate_mask_for_password(pwd)}")
    
    # 處理長度 9 (len9 目錄)
    len9_dir = os.path.join(secondtest_data_dir, "len9")
    for special_count in [1, 2, 3, 4]:
        txt_file = os.path.join(len9_dir, f"basic9+{special_count}.txt")
        
        if not os.path.exists(txt_file):
            print(f"  ⚠ 找不到: basic9+{special_count}.txt")
            continue
        
        # 讀取密碼
        passwords = read_passwords_from_txt(txt_file)
        print(f"\n  處理: len9/basic9+{special_count}.txt ({len(passwords)} 個密碼)")
        
        # 轉換為 CSV 資料
        data = []
        for pwd in passwords:
            mask = generate_mask_for_password(pwd)
            hash_value = generate_sha1(pwd)
            data.append({
                'password': pwd,
                'hashvalue': hash_value,
                'mask': mask
            })
        
        # 寫入 CSV（智慧跳過）
        df = pd.DataFrame(data)
        csv_file = os.path.join(secondtest_mask_dir, f"convert_basic9+{special_count}.csv")
        
        if check_csv_valid(csv_file, 9, special_count):
            print(f"  [SKIP] convert_basic9+{special_count}.csv 已存在且有效，跳過生成")
        else:
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"  ✓ 生成: convert_basic9+{special_count}.csv ({len(passwords)} 行)")
        # 顯示前3個樣本
        for i, pwd in enumerate(passwords[:3], 1):
            print(f"     {i}. {pwd} → {generate_mask_for_password(pwd)}")

    # 處理長度 10 (len10 目錄)
    len10_dir = os.path.join(secondtest_data_dir, "len10")
    for special_count in [1, 2, 3, 4]:
        txt_file = os.path.join(len10_dir, f"basic10+{special_count}.txt")
        
        if not os.path.exists(txt_file):
            print(f"  ⚠ 找不到: basic10+{special_count}.txt")
            continue
        
        # 讀取密碼
        passwords = read_passwords_from_txt(txt_file)
        print(f"\n  處理: len10/basic10+{special_count}.txt ({len(passwords)} 個密碼)")
        
        # 轉換為 CSV 資料
        data = []
        for pwd in passwords:
            mask = generate_mask_for_password(pwd)
            hash_value = generate_sha1(pwd)
            data.append({
                'password': pwd,
                'hashvalue': hash_value,
                'mask': mask
            })
        
        # 寫入 CSV（智慧跳過）
        df = pd.DataFrame(data)
        csv_file = os.path.join(secondtest_mask_dir, f"convert_basic10+{special_count}.csv")
        
        if check_csv_valid(csv_file, 10, special_count):
            print(f"  [SKIP] convert_basic10+{special_count}.csv 已存在且有效，跳過生成")
        else:
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"  ✓ 生成: convert_basic10+{special_count}.csv ({len(passwords)} 行)")
        # 顯示前3個樣本
        for i, pwd in enumerate(passwords[:3], 1):
            print(f"     {i}. {pwd} → {generate_mask_for_password(pwd)}")
    
    print("\n" + "="*60)
    print("✓ 完成！所有密碼已轉換為 CSV")
    print(f"\n輸出位置:")
    print(f"  1. {firsttest_mask_dir}")
    print(f"  2. {secondtest_mask_dir}")
    print("="*60)

if __name__ == "__main__":
    main()
