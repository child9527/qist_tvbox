import os
import subprocess
import sys
import time
from pathlib import Path

# 定义需要执行加密的目标 JSON 文件列表（相对路径）
TARGET_FILES_TO_ENCRYPT = [
    "fty.json",
    "jsm.json",
    "xiaosa/api.json",
]

def run_tvbox_encrypt(tools_script: Path, file_path: Path):
    """调用 ./tools/tvbox.py 进行文件原地加密"""
    print(f"\n--------------------------------------------------")
    print(f"[准备加密] 开始处理文件: {file_path}")

    # 1. 检查目标文件是否存在
    if not file_path.exists():
        print(f"[警告] 跳过加密！未找到目标文件: {file_path}")
        return

    # 获取原文件大小
    raw_size = file_path.stat().st_size
    print(f"[信息] 原始文件存在，大小为: {raw_size / 1024:.2f} KB ({raw_size} 字节)")

    # 2. 构建临时文件路径
    temp_encrypted_file = file_path.with_suffix(file_path.suffix + ".tmp")

    # 构建命令行参数: python tvbox.py <输入文件> <输出文件> enc
    cmd = [
        sys.executable,
        str(tools_script),
        str(file_path),
        str(temp_encrypted_file),
        "enc"
    ]

    print(f"[执行命令] {' '.join(cmd)}")
    start_time = time.time()

    try:
        # 执行加密命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        elapsed_time = time.time() - start_time

        # 如果加密脚本自身有标准输出，打印出来
        if result.stdout and result.stdout.strip():
            print(f"[加密脚本日志]\n{result.stdout.strip()}")

        # 3. 验证加密输出文件
        if temp_encrypted_file.exists():
            enc_size = temp_encrypted_file.stat().st_size
            print(f"[信息] 加密完成，耗时: {elapsed_time:.2f} 秒")
            print(f"[信息] 加密后文件大小: {enc_size / 1024:.2f} KB ({enc_size} 字节)")

            # 用加密后的文件覆盖原文件
            temp_encrypted_file.replace(file_path)
            print(f"[成功] 文件已被加密并成功覆盖原文件: {file_path.name}")
        else:
            print(f"[错误] 加密命令执行成功，但未生成临时输出文件: {temp_encrypted_file}")

    except subprocess.CalledProcessError as e:
        print(f"[失败] 加密文件时发生错误: {file_path}")
        print(f"[错误详情] 返回码: {e.returncode}")
        if e.stderr:
            print(f"[错误日志]\n{e.stderr.strip()}")
        
        # 清理可能生成的残余临时文件
        if temp_encrypted_file.exists():
            temp_encrypted_file.unlink()
            print(f"[清理] 已删除未完成的临时文件: {temp_encrypted_file.name}")

def main():
    print("==================================================")
    print("          TVBox 接口文件自动化加密任务 Start       ")
    print("==================================================")

    # 获取当前项目的根目录
    workspace_dir = Path(__file__).resolve().parent.parent
    tools_script = workspace_dir / "tools" / "tvbox.py"

    print(f"[信息] 项目根目录: {workspace_dir}")
    print(f"[信息] 加密脚本路径: {tools_script}")

    # 检查加密脚本是否存在
    if not tools_script.exists():
        print(f"[致命错误] 无法找到加密工具脚本: {tools_script}")
        print("[提示] 请检查 tools/tvbox.py 是否保存在仓库中。")
        sys.exit(1)

    # 循环处理需要加密的文件
    total_files = len(TARGET_FILES_TO_ENCRYPT)
    print(f"[信息] 本次计划处理 {total_files} 个 JSON 配置文件。")

    for index, rel_path in enumerate(TARGET_FILES_TO_ENCRYPT, start=1):
        target_file = workspace_dir / rel_path
        print(f"\n>>> 进度 [{index}/{total_files}]")
        run_tvbox_encrypt(tools_script, target_file)

    print("\n==================================================")
    print("          TVBox 接口文件自动化加密任务 Finish      ")
    print("==================================================")

if __name__ == "__main__":
    main()
