import time
import sys
import subprocess

# Try to import pyautogui
try:
    import pyautogui
except ImportError:
    print("错误: 需要安装 pyautogui 库才能使用鼠标操作功能。")
    print("请在终端运行以下命令进行安装：")
    print("pip install pyautogui")
    print("或者")
    print("pip3 install pyautogui")
    sys.exit(1)

def paste_text(text):
    """Copy text to clipboard and paste it using PyAutoGUI."""
    # Copy to clipboard using pbcopy (macOS)
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.stdin.write(text.encode('utf-8'))
    process.stdin.close()
    process.wait()
    
    # Paste
    time.sleep(0.5)
    pyautogui.hotkey('command', 'v')

def calibrate_mouse():
    """Guide user to set mouse positions."""
    print("\n=== 鼠标位置校准 ===")
    print("程序需要知道 '+' 按钮和 '输入框' 的位置。")
    
    # Calibrate '+' button
    print("\n步骤 1/2: 请将鼠标移动到 '+' (新建任务) 按钮上。")
    print("将在 5 秒后记录坐标，请保持不动...")
    for i in range(5, 0, -1):
        print(f"{i}...", end=' ', flush=True)
        time.sleep(1)
    print("")
    pos_plus = pyautogui.position()
    print(f"已记录 '+' 按钮位置: {pos_plus}")
    
    # Calibrate Input box
    print("\n步骤 2/2: 请将鼠标移动到 文本输入框 (对话框) 上。")
    print("将在 5 秒后记录坐标，请保持不动...")
    for i in range(5, 0, -1):
        print(f"{i}...", end=' ', flush=True)
        time.sleep(1)
    print("")
    pos_input = pyautogui.position()
    print(f"已记录输入框位置: {pos_input}")
    
    return pos_plus, pos_input

def main():
    total_loops = 20
    # Command to be entered
    command_text = "请阅读docs文件夹中的FACTOR_MINING_PROMPT.md ,并按照当中的规则进行一次因子挖掘"

    print("程序已启动。")
    
    # Run calibration
    pos_plus, pos_input = calibrate_mouse()

    print(f"\n校准完成。将在 3 秒后开始执行 {total_loops} 次循环...")
    print("按 Control+C 可随时停止程序。")
    time.sleep(3)

    try:
        for i in range(total_loops):
            print(f"\n--- 第 {i + 1}/{total_loops} 次循环 ---")
            
            # 1. Click '+' button
            print(f"点击 '+' 按钮 ({pos_plus})")
            pyautogui.click(pos_plus)
            
            # Wait a bit for the new task to initialize
            time.sleep(2)
            
            # 2. Switch back to dialog box (Click input box)
            print(f"点击输入框 ({pos_input})")
            pyautogui.click(pos_input)
            
            # Ensure focus
            time.sleep(1)
            
            # 3. Input the Chinese command
            print("输入指令...")
            paste_text(command_text)
            
            # 4. Press Enter
            pyautogui.press('enter')
            
            # 5. Wait 30 minutes
            if i < total_loops - 1:
                print("等待 30 分钟...")
                # Loop with sleep to handle Ctrl+C responsively
                for _ in range(30 * 60):
                    time.sleep(1)
            else:
                print("最后一次任务已提交。等待 30 分钟（按需完成流程）...")
                for _ in range(30 * 60):
                    time.sleep(1)
                    
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断 (Control+C)。")
        sys.exit(0)

    print("\n所有任务已完成。")

if __name__ == "__main__":
    main()
