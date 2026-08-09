import os
import subprocess
import sys
import time
from pathlib import Path

# 定义加密配置：(源 JSON 文件, 导出密文文件)
TARGET_FILES_TO_ENCRYPT = [
    ("fty.json", "fty.txt"),
    ("jsm.json", "jsm.txt"),
    ("xiaosa/api.json", "xiaosa/api.txt"),
]

STANDARD_KEY = "1234567890123456"
STANDARD_IV = "1234567890123456"

def fix_header_if_needed(txt_file: Path):
    """如果 tvbox.py 生成了 13 位的旧 Header ($#1234567890123#$)，将其强制修正为标准的 16 位 Header ($#1234567890123456#$)"""
    try:
        content = txt_file.read_text(encoding="utf-8", errors="ignore")
        if content.startswith("$#1234567890123#$"):
            # 将 13 位 Header 替换为 16 位 Header，以便标准 TVBox 客户端识别
            new_content = "$#1234567890123456#$" + content[len("$#1234567890123#$"):]
            txt_file.write_text(new_content, encoding="utf-8")
            print(f"[修复] 已将 {txt_file.name} 头部修正为标准的 16 位特征码")
    except Exception as e:
        print(f"[警告] 检查/修正文件头部时出错: {e}")

def run_tvbox_encrypt(tools_script: Path, json_rel_path: str, txt_rel_path: str, workspace_dir: Path):
    json_file = workspace_dir / json_rel_path
    txt_file = workspace_dir / txt_rel_path

    print(f"\n--------------------------------------------------")
    print(f"[准备加密] 处理源文件: {json_rel_path} -> 导出密文: {txt_rel_path}")

    if not json_file.exists():
        print(f"[警告] 跳过加密！未找到目标 JSON 文件: {json_file}")
        return

    txt_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(tools_script),
        str(json_file),
        str(txt_file),
        "enc",
        STANDARD_KEY,
        STANDARD_IV
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if txt_file.exists() and txt_file.stat().st_size > 0:
            # 加密成功后检查并修正头部特征
            fix_header_if_needed(txt_file)
            print(f"[成功] 加密成功，已生成密文文件: {txt_file.name}")
        else:
            print(f"[错误] 未生成有效密文文件: {txt_file}")
    except subprocess.CalledProcessError as e:
        print(f"[失败] 加密文件发生错误: {e}")

def main():
    workspace_dir = Path(__file__).resolve().parent.parent
    tools_script = workspace_dir / "tools" / "tvbox.py"

    if not tools_script.exists():
        print(f"[错误] 未找到加密工具脚本: {tools_script}")
        sys.exit(1)

    for json_rel, txt_rel in TARGET_FILES_TO_ENCRYPT:
        run_tvbox_encrypt(tools_script, json_rel, txt_rel, workspace_dir)

if __name__ == "__main__":
    main()
