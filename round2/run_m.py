import subprocess
import json
import time
import datetime
import os
import pandas as pd

# 自定義特殊字符集（與 gen_mask.py 和 eval.py 保持一致）
SPECIAL_CHARS = "#@!^%$^&"
SPECIAL_CHARS_HEX = "2340215e25245e26"

# secondtest 使用的完整特殊字符集（去除可能引發錯誤的字符）
# 原始 ?s 包含：空格!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
# 去除可能引發錯誤的字符：\ ` [ ] (這些字符在命令行可能有特殊意義)
SPECIAL_CHARS_FULL = " !\"#$%&'()*+,-./:;<=>?@^_{}|~"
SPECIAL_CHARS_FULL_HEX = "202122232425262728292a2b2c2d2e2f3a3b3c3d3e3f405e5f7b7d7c7e"


def run_hashcat_task(
    hashcat_base_cmd,
    mode,
    attack_payload,
    max_seconds,
    output_json_path,
    hybrid_mask=None,  # 新增：混合模式的 mask
    test_folder=None   # 新增：用於判斷是 firsttest 還是 secondtest
):

    cmd = list(hashcat_base_cmd)
    
    # 將 -w 3 改為 -w 4 (Nightmare mode)
    cmd = [c for c in cmd if not c.startswith("-w")]
    cmd.extend(["-w", "4"])  # Nightmare mode: 最高性能

    # 根據 test_folder 選擇特殊字符集
    if test_folder == "secondtest":
        # secondtest: 使用完整的特殊字符集（去除可能引發錯誤的字符）
        special_chars_hex = SPECIAL_CHARS_FULL_HEX
        special_chars_display = SPECIAL_CHARS_FULL
    else:
        # firsttest: 使用原本的自定義字符集
        special_chars_hex = SPECIAL_CHARS_HEX
        special_chars_display = SPECIAL_CHARS

    # 如果 mask 中包含 ?s，則替換為自定義字符集 -1 (使用 hex 格式避免 [] 等特殊字符問題)
    if mode == 3 and "?s" in attack_payload:
        # 將 ?s 替換為 ?1
        custom_mask = attack_payload.replace("?s", "?1")
        # 添加 hex 格式的自定義字符集
        cmd.extend(["--hex-charset", "-1", special_chars_hex])
        print(f"[INFO] 測試類型: {test_folder}")
        print(f"[INFO] 使用自定義特殊字符集 (hex): {special_chars_hex}")
        print(f"[INFO] 字符集內容: {special_chars_display}")
        print(f"[INFO] Mask 轉換: {attack_payload} → {custom_mask}")
        attack_payload = custom_mask
    elif mode in [6, 7] and hybrid_mask and "?s" in hybrid_mask:
        # Hybrid 模式的 mask 也需要處理
        custom_mask = hybrid_mask.replace("?s", "?1")
        cmd.extend(["--hex-charset", "-1", special_chars_hex])
        print(f"[INFO] 測試類型: {test_folder}")
        print(f"[INFO] 使用自定義特殊字符集 (hex): {special_chars_hex}")
        print(f"[INFO] 字符集內容: {special_chars_display}")
        print(f"[INFO] Hybrid Mask 轉換: {hybrid_mask} → {custom_mask}")
        hybrid_mask = custom_mask

    # 攻擊模式
    if mode == 3:
        cmd.extend(["-a", "3", attack_payload])
    elif mode == 0:
        cmd.extend(["-a", "0", attack_payload])
    elif mode == 6:
        # Hybrid mode: dictionary + mask
        cmd.extend(["-a", "6", attack_payload, hybrid_mask])
    elif mode == 7:
        # Hybrid mode: mask + dictionary
        cmd.extend(["-a", "7", hybrid_mask, attack_payload])

    # 狀態監控參數
    cmd = [c for c in cmd if not c.startswith("--status-timer")]
    if "--status" not in cmd:
        cmd.append("--status")
    if "--status-json" not in cmd:
        cmd.append("--status-json")
    cmd.append("--status-timer=60")  # 每 60 秒更新一次，減少 I/O 開銷
    
    # GPU 性能優化參數
    cmd.append("-O")               # 啟用優a化核心
    
    # 強制執行
    if "--force" not in cmd:
        cmd.append("--force")

    print("\n[RUN] Hashcat Command:", " ".join(cmd))

    mode_names = {
        3: "Mask Attack (3)",
        0: "Dictionary Attack (0)",
        6: "Hybrid Attack: Dict+Mask (6)",
        7: "Hybrid Attack: Mask+Dict (7)"
    }
    
    final_status = {
        "Attack_Mode": mode_names.get(mode, f"Unknown Mode ({mode})"),
        "Attack_Payload": attack_payload,
        "Hybrid_Mask": hybrid_mask if mode in [6, 7] else None,
        "Status": "Initializing",
        "Max_Time_Limit_Seconds": max_seconds,
    }

    # 取得 hashcat 所在目錄
    hashcat_dir = os.path.dirname(cmd[0])
    print(f"[INFO] Hashcat 工作目錄: {hashcat_dir}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8',
        errors='replace',
        cwd=hashcat_dir  # 在 hashcat 目錄下執行
    )

    # ======= Start time 記錄 =======
    run_start_time = datetime.datetime.now()

    for line in process.stdout:
        line = line.strip()
        
        # 顯示所有非空行訊息（方便除錯）
        if line:
            print(f"[Hashcat] {line}")

        if not (line.startswith("{") and '"status"' in line):
            continue

        try:
            data = json.loads(line)
        except:
            continue

        # hashcat 內部狀態
        # 1. Status: 嘗試讀取 status_string，若無則讀取 status 代碼並轉換
        status_code = data.get("status", -1)
        status_str = data.get("status_string")
        
        if not status_str:
            # 定義狀態代碼對照表 (參考 Hashcat 文件)
            status_map = {
                1: "Initializing",
                2: "Autotuning",
                3: "Running",
                4: "Paused",
                5: "Exhausted",
                6: "Cracked",
                7: "Aborted",
                8: "Quit",
                9: "Bypass",
                10: "Checkpoint",
                11: "Error"
            }
            status_str = status_map.get(status_code, "Unknown")

        # 2. Guess Mask: 嘗試讀取 guess_mask，若無則讀取 guess_base
        guess_data = data.get("guess", {})
        guess_mask = guess_data.get("guess_mask")
        if not guess_mask:
            guess_mask = guess_data.get("guess_base", "Unknown")

        progress = data.get("progress", [])
        time_elapsed = data.get("time_elapsed", 0)
        time_estimated = data.get("time_estimated", 0)

        # 計算實際執行時間
        current_time = datetime.datetime.now()
        actual_elapsed = (current_time - run_start_time).total_seconds()
        
        # 更新目前狀態
        final_status.update({
            "Status": status_str,
            "Guess.Mask": guess_mask,
            "Progress": progress,
            "Hashcat_Reported_Time_Seconds": time_elapsed,
            "Actual_Runtime_Seconds": round(actual_elapsed, 2),
            "Estimated_Left_Seconds": time_estimated,
            "Last_Update": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        # 顯示目前狀態（減少顯示頻率）
        if time_elapsed % 60 < 5:  # 每分鐘只顯示一次
            progress_str = f"{progress[0]}/{progress[1]}" if len(progress) >= 2 else "N/A"
            print(f"\n >> [Status] {status_str} | Time: {time_elapsed}s | Progress: {progress_str}")

        # ======= 超過上限時間立即中斷（使用實際執行時間） =======
        if actual_elapsed > max_seconds:
            print(f"\n[STOP] 超過上限時間 ({max_seconds}s)，實際執行: {actual_elapsed:.1f}s，立即終止 Hashcat")
            process.terminate()
            break

        # 寫出目前狀態
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_status, f, indent=4, ensure_ascii=False)

    process.wait()
    print()  # 換行，結束狀態列
    print(f"[INFO] Hashcat 程序已結束，返回碼: {process.returncode}")

    # ======= 結束時間：真正程式結束的時間 =======
    run_end_time = datetime.datetime.now()
    actual_runtime = (run_end_time - run_start_time).total_seconds()

    mode_names = {
        3: "Mask Attack (3)",
        0: "Dictionary Attack (0)",
        6: "Hybrid Attack: Dict+Mask (6)",
        7: "Hybrid Attack: Mask+Dict (7)"
    }
    
    final_status["Started"] = run_start_time.strftime("%Y-%m-%d %H:%M:%S")
    final_status["Finished"] = run_end_time.strftime("%Y-%m-%d %H:%M:%S")
    final_status["Actual_Runtime_Seconds"] = round(actual_runtime, 2)
    final_status["Attack_Mode"] = mode_names.get(mode, f"Unknown Mode ({mode})")
    final_status["Attack_Payload"] = attack_payload
    if mode in [6, 7]:
        final_status["Hybrid_Mask"] = hybrid_mask
    final_status["Command"] = " ".join(cmd)
    final_status["Process_Exit_Code"] = process.returncode
    final_status["Max_Time_Limit_Seconds"] = max_seconds

    # ======= 讀取 hashcat.potfile 取得破解結果 =======
    # 假設 hashcat 預設會將結果寫入 hashcat.potfile (或指定的 potfile)
    # 這裡我們嘗試讀取 hashcat.potfile，並尋找與目前 hash.txt 中 hash 值對應的密碼
    
    cracked_password = "Na"
    # 使用相對路徑找到 hashcat.potfile
    # __file__ 是當前腳本 (exam/round2/run_m.py)
    # 需要上兩層到達 hashcat-7.1.2
    if __file__:
        script_dir_here = os.path.dirname(os.path.abspath(__file__))
    else:
        script_dir_here = os.path.abspath(os.getcwd())
    exam_dir_here = os.path.dirname(script_dir_here)
    hashcat_root_here = os.path.dirname(exam_dir_here)
    potfile_path = os.path.join(hashcat_root_here, "hashcat.potfile")
    
    # 讀取目前的 hash 值
    current_hash = ""
    hash_file_path = os.path.join(script_dir_here, "hash.txt")
    if os.path.exists(hash_file_path):
        with open(hash_file_path, "r", encoding="utf-8") as f:
            current_hash = f.read().strip()

    if os.path.exists(potfile_path) and current_hash:
        try:
            with open(potfile_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    # potfile 格式通常是 hash:password
                    if line.startswith(current_hash + ":"):
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            cracked_password = parts[1]
                        break
        except Exception as e:
            print(f"[WARN] 讀取 potfile 失敗: {e}")

    final_status["Cracked_Password"] = cracked_password

    # 顯示最終清楚的結果
    print("\n" + "="*50)
    print(f" RESULT SUMMARY")
    print(f" Mode          : {final_status.get('Attack_Mode', 'Unknown')}")
    print(f" Payload       : {attack_payload}")
    print(f" Status        : {final_status.get('Status', 'Unknown')}")
    print(f" Password      : {final_status.get('Cracked_Password', 'Na')}")
    print(f" Actual Time   : {final_status.get('Actual_Runtime_Seconds', 0)}s")
    print(f" Hashcat Time  : {final_status.get('Hashcat_Reported_Time_Seconds', 0)}s")
    print(f" Exit Code     : {process.returncode}")
    print("="*50 + "\n")

    # 寫入 final JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_status, f, indent=4, ensure_ascii=False)

    # ======= 清空 potfile =======
    if os.path.exists(potfile_path):
        try:
            with open(potfile_path, 'w', encoding='utf-8') as f:
                f.write("")  # 清空內容
            print(f"[CLEAN] 已清空 potfile: {potfile_path}")
        except Exception as e:
            print(f"[WARN] 清空 potfile 失敗: {e}")
    
    return final_status


# ===============================
# 主程式
# ===============================
if __name__ == "__main__":

    folders = ["firsttest", "secondtest"]
    
    # 取得目前腳本所在的目錄 (exam/round1)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # hashcat 執行檔路徑 (假設在 exam/round1 的上兩層)
    hashcat_root = os.path.dirname(os.path.dirname(script_dir))
    hashcat_exe_path = os.path.join(hashcat_root, "hashcat.exe")

    # 字典檔路徑 (使用相對路徑)
    exam_dir = os.path.dirname(script_dir)
    dictionary_path = os.path.join(exam_dir, "dictionary", "dictionary.txt")

    for test_folder in folders:

        print(f"\n========== Now Processing: {test_folder} ==========\n")

        # 使用絕對路徑來避免找不到檔案的問題 (Mask 攻擊使用 mask_data)
        csv_root_path = os.path.join(script_dir, test_folder, "result", "mask_data")
        json_root_path = os.path.join(script_dir, test_folder, "result_json")

        # 根據 test_folder 設定 CSV 檔案列表
        if test_folder == "firsttest":
            csv_files = [f"convert_basic{i}.csv" for i in range(8, 13)]  # 8~12
        else:  # secondtest
            csv_files = (
                [f"convert_basic8+{i}.csv" for i in range(1, 5)] +
                [f"convert_basic9+{i}.csv" for i in range(1, 5)] +
                [f"convert_basic10+{i}.csv" for i in range(1, 5)]
            )

        # 處理所有 CSV 檔案
        for csv_name in csv_files:
            csv_path = os.path.join(csv_root_path, csv_name)

            if not os.path.exists(csv_path):
                print(f"[SKIP] 找不到：{csv_path}")
                continue

            print(f"[LOAD] {csv_path}")

            df = pd.read_csv(csv_path, encoding="utf-8-sig")
            csv_basename = csv_name.replace(".csv", "")

            for row_index, row in df.iterrows():

                mask = row["mask"]
                hashvalue = row["hashvalue"]
                password = row["password"]
                password_length = len(password)

                # 使用絕對路徑建立 hash.txt
                hash_file_path = os.path.join(script_dir, "hash.txt")
                with open(hash_file_path, "w", encoding="utf-8") as f:
                    f.write(hashvalue)

                HASHCAT_BASE_CMD = [
                    hashcat_exe_path,
                    "-m", "100",
                    "-d", "1",     # 僅使用 NVIDIA RTX 5070
                    hash_file_path
                ]

                # 根據密碼長度設定時間上限
                if password_length <= 10:
                    mask_timeout = 54000
                    dict_timeout = 54000
                elif password_length == 11:
                    mask_timeout = 72000
                    dict_timeout = 72000
                else:  # password_length >= 12
                    mask_timeout = 86400
                    dict_timeout = 86400
                
                print(f"[INFO] 密碼長度: {password_length}, Mask時間: {mask_timeout}s, Dict時間: {dict_timeout}s")

                # 1. 執行 Mask Attack
                mask_subdir = os.path.join(json_root_path, "1", csv_basename)
                os.makedirs(mask_subdir, exist_ok=True)
                output_json_mask = os.path.join(mask_subdir, f"{csv_basename}-{row_index+1}.json")
                
                # 檢查 JSON 是否已存在且已成功破解
                skip_mask = False
                if os.path.exists(output_json_mask):
                    try:
                        with open(output_json_mask, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                            if existing_data.get("Status") == "Cracked" and existing_data.get("Cracked_Password") and existing_data.get("Cracked_Password") != "Na":
                                print(f"[SKIP] {csv_basename}, row {row_index+1} - 已破解 (密碼: {existing_data.get('Cracked_Password')})")
                                skip_mask = True
                    except Exception as e:
                        print(f"[WARN] 讀取現有 JSON 失敗: {e}，將重新執行")
                
                if not skip_mask:
                    print(f"[MASK ATTACK] {csv_basename}, row {row_index+1} → {output_json_mask}")
                    run_hashcat_task(
                        HASHCAT_BASE_CMD,
                        mode=3,
                        attack_payload=mask,
                        max_seconds=mask_timeout,
                        output_json_path=output_json_mask,
                        test_folder=test_folder  # 傳遞測試類型
                    )


        
           