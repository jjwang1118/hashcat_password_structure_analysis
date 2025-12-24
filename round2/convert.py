import os
import pandas as pd
import json
import hashlib


file=["firsttest","secondtest"]
convert_list=[]

def converthash(pw):
    hash_value=hashlib.sha1(pw.encode('utf-8')).hexdigest()
    return hash_value

def check_char_type(char):
    if char.isupper():
        return "U"
    elif char.isdigit():
        return "D"
    elif not char.isalnum():
        return "S"
    else:
        return "L"

def mask(pw):
    mask_str = ""
    for char in pw:
        ctype = check_char_type(char)
        if ctype == "U":
            mask_str += "?u"
        elif ctype == "D":
            mask_str += "?d"
        elif ctype == "S":
            mask_str += "?s"
        else:
            mask_str += "?l"
    return mask_str
    
file=["firsttest","secondtest"]
# 取得目前腳本所在的目錄 (exam/round1)
script_dir = os.path.dirname(os.path.abspath(__file__))

for f in range (len(file)):
    for basic_len in range(8,13,1):
        if f==0:
            # 使用絕對路徑
            read_dir = os.path.join(script_dir, file[f], "data", f"basic{basic_len}.txt")
        else:
            read_dir = os.path.join(script_dir, file[f], "data", f"basic+{basic_len-7}.txt")
        
        if not os.path.exists(read_dir):
            print(f"Skipping missing file: {read_dir}")
            continue

        with open(read_dir, 'r', encoding='utf-8-sig') as file_obj:
            pws= file_obj.readlines()
            for pw in pws:
                pw=pw.strip()
                hashvalue=converthash(pw)
                maskvalue=mask(pw)
                convert_list.append([pw,hashvalue,maskvalue])
        
        convert_list_df=pd.DataFrame(convert_list,columns=['password','hashvalue','mask'])
        if f==0:
            save_dir = os.path.join(script_dir, file[f], "result", f"convert_basic{basic_len}.csv")
        else:
            save_dir = os.path.join(script_dir, file[f], "result", f"convert_basic8+{basic_len-7}.csv")

        
        os.makedirs(os.path.dirname(save_dir), exist_ok=True)
        
        convert_list_df.to_csv(save_dir, index=False,encoding='utf-8-sig')
        convert_list=[]
        



