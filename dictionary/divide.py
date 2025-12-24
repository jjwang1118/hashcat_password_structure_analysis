import os

def divide_dictionary(input_path, output_prefix="dictionary", output_count=3):
    """
    將 input_path 檔案平均分成 output_count 份，分別輸出為 dictionary1.txt, dictionary2.txt, dictionary3.txt。
    """
    if not os.path.exists(input_path):
        print(f"找不到檔案: {input_path}")
        return
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]
    total = len(lines)
    chunk_size = (total + output_count - 1) // output_count  # 平均分配，多的分到前面
    for i in range(output_count):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, total)
        chunk = lines[start:end]
        out_path = f"{output_prefix}{i+1}.txt"
        with open(out_path, 'w', encoding='utf-8') as out:
            for word in chunk:
                out.write(word + '\n')
        print(f"已寫入 {out_path}，共 {len(chunk)} 行")

if __name__ == "__main__":
    divide_dictionary("dictionary_prew.txt")
