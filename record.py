import tkinter as tk
from tkinter import filedialog
import subprocess
import os
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(script_dir,'bin','ffmpeg.exe')

# 下载任务列表
processes = []
downloading = False
url_file = ""

def start_stop_downloads():
    global processes, downloading
    if downloading:
        stop_downloads()
        download_button.config(text="开始下载")
    else:
        start_downloads()
        download_button.config(text="停止下载")
    downloading = not downloading

def start_downloads():
    global processes
    urls = []
    
    # 从文件中读取 URL 列表
    with open(url_file, 'r') as file:
        urls = file.readlines()
    
    # 去除每行末尾的换行符
    urls = [url.strip() for url in urls]
    
    # 创建并行下载的 subprocess 任务
    processes = []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join('output', timestamp)
    os.makedirs(output_folder, exist_ok=True)

    for url in urls:
        # 提取文件名部分
        filename_with_extension = url.split('/')[-1].split('?')[0]
        base_name = filename_with_extension.split('.')[0]
        output_file = base_name+'.mp4'
        cmd = [ffmpeg_path,'-i', url, '-c','copy',os.path.join(output_folder, output_file)]
        process = subprocess.Popen(cmd,stdin=subprocess.PIPE)
        processes.append(process)

def stop_downloads():
    global processes
    for process in processes:
        # 发送 'q' 键命令到 ffmpeg 进程
        process.stdin.write(b'q')
        process.stdin.flush()
    # 等待所有子进程完成
    for process in processes:
        process.wait()
    print("所有下载任务已停止。")
    processes = []

def select_file():
    global url_file
    url_file = filedialog.askopenfilename(title="选择 URL 文件", filetypes=[("Text Files", "*.txt")])
    if url_file:
        file_label.config(text=f"已选择文件: {os.path.basename(url_file)}")
        download_button.config(state=tk.NORMAL)  # 启用下载按钮
    else:
        file_label.config(text="尚未选择文件")
        download_button.config(state=tk.DISABLED)  # 禁用下载按钮

def on_closing():
    if downloading:
        stop_downloads()
    # 关闭窗口
    root.destroy()

# 创建主窗口
root = tk.Tk()
root.title("record")

# 设置窗口大小 (宽 x 高)
root.geometry("250x200")
root.resizable(width=False, height=False)

# 创建并放置按钮
frame = tk.Frame(root)
frame.pack(expand=True, fill=tk.BOTH)

select_button = tk.Button(frame, text="选择 URL 文件", command=select_file)
select_button.pack(expand=True)

download_button = tk.Button(frame, text="开始下载", command=start_stop_downloads, state=tk.DISABLED)
download_button.pack(expand=True)

file_label = tk.Label(frame, text="尚未选择文件")
file_label.pack(expand=True)

# 设置窗口关闭时的处理函数
root.protocol("WM_DELETE_WINDOW", on_closing)

# 启动主循环
root.mainloop()