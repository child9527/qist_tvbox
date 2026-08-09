import os
import subprocess
import sys
import time
from pathlib import Path

# 定义需要执行加密的目标 JSON 文件与导出的加密 TXT 文件对应关系 (源 JSON -> 加密 TXT)
TARGET_FILES_TO_ENCRYPT = [
    ("fty.json", "fty.txt"),
    ("jsm.json", "jsm.txt"),
    ("xiaosa/api.json", "xiaosa/api.txt"),
]

def run_tvbox_encrypt(tools_script: Path, json_rel_path: str, txt_rel_path: str, workspace_dir: Path):
    """调用 ./tools/tvbox.py 将 JSON 文件加密导出为 TVBox 可识别的 TXT 加密接口文件"""
    json_file = workspace_dir / json_rel_path
    txt_file = workspace_dir / txt_rel_path

    print(f"\n--------------------------------------------------")
    print(f"[准备加密] 处理源文件: {json_rel_path} -> 导出密文: {txt_rel_path}")

    # 1. 检查目标 JSON 文件是否存在
    if not json_file.exists():
        print(f"[警告] 跳过加密！未找到目标 JSON 文件: {json_file}")
        return

    # 获取原文件大小
    raw_size = json_file.stat().st_size
    print(f"[信息] 原始 JSON 文件存在，大小为: {raw_size / 1024:.2f} KB ({raw_size} 字节)")

    # 确保输出目录存在
    txt_file.parent.mkdir(parents=True, exist_ok=True)

    # 构建命令行参数: python tvbox.py <输入json> <输出txt> enc
    # 注意：这里输出文件为 txt_file，绝对不能覆盖原始的 json_file！
    cmd = [
        sys.executable,
        str(tools_script),
        str(json_file),
        str(txt_file),
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

        # 2. 验证生成的加密 TXT 文件
        if txt_file.exists() and txt_file.stat().st_size > 0:
            enc_size = txt_file.stat().st_size
            print(f"[信息] 加密完成，耗时: {elapsed_time:.2f} 秒")
            print(f"[信息] 加密后 TXT 大小: {enc_size / 1024:.2f} KB ({enc_size} 字节)")
            print(f"[成功] 原 JSON 保持明文，加密结果已写入: {txt_file.name}")
        else:
            print(f"[错误] 加密命令执行完成，但未生成有效的输出文件: {txt_file}")

    except subprocess.CalledProcessError as e:
        print(f"[失败] 加密文件时发生错误: {json_file}")
        print(f"[错误详情] 返回码: {e.returncode}")
        if e.stderr:
            print(f"[错误日志]\n{e.stderr.strip()}")
        
        # 清理可能生成的残余空文件
        if txt_file.exists() and txt_file.stat().st_size == 0:
            txt_file.unlink()
            print(f"[清理] 已删除未完成的临时文件: {txt_file.name}")

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
    print(f"[信息] 本次计划处理 {total_files} 个配置文件的加密导出。")

    for index, (json_rel, txt_rel) in enumerate(TARGET_FILES_TO_ENCRYPT, start=1):
        print(f"\n>>> 进度 [{index}/{total_files}]")
        run_tvbox_encrypt(tools_script, json_rel, txt_rel, workspace_dir)

    print("\n==================================================")
    print("          TVBox 接口文件自动化加密任务 Finish      ")
    print("==================================================")

if __name__ == "__main__":
    main()
