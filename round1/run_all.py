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
    print("開始執行完整測試流程")
    print("="*60)
    
    # 執行 run_m.py (Mask 攻擊)
    success_m = run_script("run_m.py")
    
    if not success_m:
        print("[ERROR] run_m.py 執行失敗，停止後續執行")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ 所有測試完成！")
    print("="*60)
