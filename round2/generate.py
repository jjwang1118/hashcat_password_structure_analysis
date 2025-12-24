import subprocess
import sys
import os

def run_script(script_name):
    """執行指定的 Python 腳本"""
    print(f"\n{'='*60}")
    print(f"開始執行：{script_name}")
    print(f"{'='*60}\n")
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True
        )
        print(f"\n{'='*60}")
        print(f"✓ {script_name} 執行完成")
        print(f"{'='*60}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{'='*60}")
        print(f"✗ {script_name} 執行失敗，返回碼：{e.returncode}")
        print(f"{'='*60}\n")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("開始生成測試資料")
    print("="*60)
    
    # 1. 先執行 gen_mask.py (生成 Mask 攻擊密碼)
    success_random = run_script("gen_mask.py")
    
    if not success_random:
        print("[ERROR] gen_mask.py 執行失敗，停止後續執行")
        sys.exit(1)
    
    # 2. 再執行 filter.py (從字典提取密碼)
    success_filter = run_script("filter.py")
    
    if not success_filter:
        print("[ERROR] filter.py 執行失敗")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ 所有測試資料生成完成！")
    print("="*60)
    print("\n生成的檔案:")
    print("  Mask 攻擊資料:")
    print("    - firsttest/result/mask_data/convert_basic*.csv")
    print("    - secondtest/result/mask_data/convert_basic8+*.csv")
    print("  字典攻擊資料:")
    print("    - firsttest/result/dict_data/basic*_d.csv")
    print("    - secondtest/result/dict_data/basic8+*_d.csv")
    print("\n下一步：執行 eval.py 驗證資料完整性")
    print("="*60)
