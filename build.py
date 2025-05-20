import os
import sys
import subprocess
import shutil
import argparse
import zipfile
import urllib.request

UPX_URL = "https://github.com/upx/upx/releases/download/v5.0.1/upx-5.0.1-win64.zip"
UPX_ZIP = "upx.zip"
UPX_DIR = "upx"

def run_command(command, env=None):
    result = subprocess.run(command, shell=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"命令执行失败: {command}")

def download_and_extract_upx():
    print("下载 UPX 压缩工具...")
    urllib.request.urlretrieve(UPX_URL, UPX_ZIP)
    with zipfile.ZipFile(UPX_ZIP, 'r') as zip_ref:
        zip_ref.extractall(UPX_DIR)
    os.remove(UPX_ZIP)
    for root, dirs, files in os.walk(UPX_DIR):
        for f in files:
            if f.lower() == "upx.exe":
                return os.path.join(root, f)
    raise FileNotFoundError("未找到 upx.exe")

def main():
    if not sys.platform.startswith("win"):
        print("此脚本仅适用于 Windows 系统")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="打包 Python 脚本为可执行文件")
    parser.add_argument('--withffmpeg', action='store_true', help="是否包含 ffmpeg（bin 目录）")
    parser.add_argument('--withupx', action='store_true', help="是否使用 UPX 压缩可执行文件")
    args = parser.parse_args()

    print("创建虚拟环境...")
    run_command("python -m venv venv")

    venv_path = os.path.abspath("venv")
    python_exec = os.path.join(venv_path, "Scripts", "python.exe")
    pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")

    print("安装 pyinstaller...")
    run_command(f'"{pip_exec}" install pyinstaller')

    upx_dir_option = ""
    if args.withupx:
        upx_path = download_and_extract_upx()
        upx_dir_option = f'--upx-dir "{os.path.dirname(upx_path)}"'
        print(f"UPX 已准备好: {upx_path}")

    print("打包 exe...")
    pyinstaller_cmd = [
        f'"{python_exec}"', "-m", "PyInstaller",
        "-w", "-F",
        '--add-data', f".\\icon.ico;.",
        "-i", ".\\icon.ico"
    ]

    if args.withffmpeg:
        pyinstaller_cmd += ['--add-data', f".\\bin\\*;.\\bin"]

    if upx_dir_option:
        pyinstaller_cmd += [upx_dir_option]

    pyinstaller_cmd.append("record.py")

    run_command(" ".join(pyinstaller_cmd))

    dist_exe = os.path.join("dist", "record.exe")
    if os.path.exists(dist_exe):
        shutil.move(dist_exe, "record.exe")

    print("清理中间文件...")
    for folder in ["build", "dist", "__pycache__", "venv"]:
        shutil.rmtree(folder, ignore_errors=True)
    if args.withupx:
        shutil.rmtree(UPX_DIR, ignore_errors=True)
    for file in os.listdir():
        if file.endswith(".spec"):
            os.remove(file)

    print("✅ 打包完成！")

if __name__ == "__main__":
    main()
