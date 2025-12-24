
import os
import random

first_file = r"hashmob.net.user.found.txt"
second_file = r"hashmob.net.medium.found.txt"


def create_dictionary(file1_path, file2_path, output_path=r"dictionary_prew.txt"):
    """
    讀取兩個 txt 檔案。
    從第一個檔案中篩選出長度為 11 或 12 的單字。
    將這些篩選出的單字與第二個檔案的內容結合。
    產生一個名為 dictionary.txt 的檔案。
    """
    try:
        filtered_words = []
        
        # 處理第一個檔案：篩選長度 11 或 12
        if os.path.exists(file1_path):
            print(f"正在讀取並篩選 {file1_path} ...")
            with open(file1_path, 'r', encoding='utf-8', errors='ignore') as f1:
                for line in f1:
                    word = line.strip()
                    if len(word) == 11 or len(word) == 12:
                        filtered_words.append(word)
        else:
            print(f"警告: 找不到檔案 {file1_path}")

        file2_words = []
        # 處理第二個檔案：讀取所有內容
        if os.path.exists(file2_path):
            print(f"正在讀取 {file2_path} ...")
            with open(file2_path, 'r', encoding='utf-8', errors='ignore') as f2:
                for line in f2:
                    word = line.strip()
                    if word: # 排除空行
                        file2_words.append(word)
        else:
            print(f"警告: 找不到檔案 {file2_path}")


        # 合併並打亂列表
        all_words = filtered_words + file2_words
        print("正在打亂所有單字順序 ...")
        random.shuffle(all_words)

        # 寫入輸出檔案
        print(f"正在寫入 {output_path} ...")
        with open(output_path, 'a', encoding='utf-8') as out:
            for word in all_words:
                out.write(word + '\n')
        
        print(f"✅ 成功建立 {output_path}")
        print(f"   - 總字數: {len(all_words)}")
        print(f"   - 來自 {file1_path} (長度11,12): {len(filtered_words)}")
        print(f"   - 來自 {file2_path}: {len(file2_words)}")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    # 範例用法
    # 請將這裡的檔名換成您實際的檔案路徑
    first_file = r"hashmob.net.user.found.txt"
    second_file = r"hashmob.net.medium.found.txt"
    
    # 檢查是否在正確的目錄下執行，或者使用絕對路徑
    create_dictionary(first_file, second_file)
