import os
import random

def add_all(file1_path, file2_path, output_path="dictionary.txt"):
    """
    將兩個字典檔案完全合併，打亂順序，並寫入 output_path。
    """
    all_words = []
    # 讀取第一個檔案
    if os.path.exists(file1_path):
        print(f"讀取 {file1_path} ...")
        with open(file1_path, 'r', encoding='utf-8', errors='ignore') as f1:
            for line in f1:
                word = line.strip()
                if word:
                    all_words.append(word)
    else:
        print(f"警告: 找不到檔案 {file1_path}")
    # 讀取第二個檔案
    if os.path.exists(file2_path):
        print(f"讀取 {file2_path} ...")
        with open(file2_path, 'r', encoding='utf-8', errors='ignore') as f2:
            for line in f2:
                word = line.strip()
                if word:
                    all_words.append(word)
    else:
        print(f"警告: 找不到檔案 {file2_path}")
    # 打亂順序
    print("正在打亂所有單字順序 ...")
    random.shuffle(all_words)
    # 寫入輸出檔案
    print(f"正在寫入 {output_path} ...")
    with open(output_path, 'w', encoding='utf-8') as out:
        for word in all_words:
            out.write(word + '\n')
    print(f"✅ 成功建立 {output_path}")
    print(f"   - 總字數: {len(all_words)}")
    print(f"   - 來自 {file1_path}: {os.path.basename(file1_path)}")
    print(f"   - 來自 {file2_path}: {os.path.basename(file2_path)}")

if __name__ == "__main__":
    first_file = r"hashmob.net.user.found.txt"
    second_file = r"hashmob.net.medium.found.txt"
    add_all(first_file, second_file)
