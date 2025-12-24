#!/usr/bin/env python3
"""
最終驗證：測試包含 [ ] 的密碼是否能成功破解
"""
import subprocess
import hashlib
import os
import sys

# 新的完整字符集
SPECIAL_CHARS = "!#$%&()*+-/:;<=>?@[]^_`{|}~"
SPECIAL_CHARS_HEX = "212324252628292a2b2d2f3a3b3c3d3e3f405b5d5e5f607b7c7d7e"

# 測試密碼：包含方括號
test_password = "passw=[-"  # 來自 basic8.txt
hash_val = hashlib.sha1(test_password.encode()).hexdigest()

print("="*70)
print("最終驗證測試 - 包含方括號的密碼")
print("="*70)
print(f"\n字符集: {SPECIAL_CHARS}")
print(f"字符數: {len(SPECIAL_CHARS)}")
print(f"Hex 格式: {SPECIAL_CHARS_HEX}")
print(f"\n測試密碼: {test_password}")
print(f"特殊字符: =, [, -")
print(f"SHA-1 Hash: {hash_val}")

# Mask: ?l?l?l?l?l?1?1?1
mask = "?l?l?l?l?l?1?1?1"
print(f"Mask: {mask}")

# 寫入 hash
with open("final_test_hash.txt", "w") as f:
    f.write(hash_val)

# Hashcat 路徑 (使用相對路徑)
script_dir = os.path.dirname(os.path.abspath(__file__))
exam_dir = os.path.dirname(script_dir)
hashcat_root = os.path.dirname(exam_dir)
hashcat_exe = os.path.join(hashcat_root, "hashcat.exe")
hashcat_dir = hashcat_root

cmd = [
    hashcat_exe,
    "-m", "100",
    "-a", "3",
    "--hex-charset",
    "-1", SPECIAL_CHARS_HEX,
    "-d", "1",
    "--force",
    "final_test_hash.txt",
    mask
]

print(f"\n執行命令:")
print(" ".join(cmd))
print("\n" + "="*70)
print("開始破解...")
print("="*70 + "\n")

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    cwd=hashcat_dir,
    timeout=120
)

# 檢查輸出中是否有錯誤
if "Syntax error" in result.stdout or "Syntax error" in result.stderr:
    print("❌ 語法錯誤！")
    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    sys.exit(1)

# 檢查 potfile
potfile = os.path.join(hashcat_dir, "hashcat.potfile")
cracked = None
if os.path.exists(potfile):
    with open(potfile, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if hash_val in line:
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    cracked = parts[1]
                break

print("\n" + "="*70)
print("結果")
print("="*70)

if cracked:
    print(f"✅ 破解成功！")
    print(f"\n原始密碼: {test_password}")
    print(f"破解結果: {cracked}")
    
    if cracked == test_password:
        print(f"\n🎉 完美匹配！所有特殊字符都正確處理！")
        print(f"\n包含的特殊字符:")
        for char in cracked:
            if char in SPECIAL_CHARS:
                print(f"  '{char}' (ASCII {ord(char)})")
    else:
        print(f"\n⚠️ 密碼不匹配")
    
    # 清空 potfile
    with open(potfile, 'w') as f:
        f.write("")
    print(f"\n✅ 已清空 potfile")
else:
    print(f"❌ 破解失敗")
    print(f"返回碼: {result.returncode}")
    print(f"\n最後 500 字符的輸出:")
    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)

# 清理
if os.path.exists("final_test_hash.txt"):
    os.remove("final_test_hash.txt")

print("="*70)
