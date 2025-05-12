import tkinter as tk
from tkinter import ttk
import subprocess
import os
import sys
from datetime import datetime
import urllib.request
import json

hint_text = "文件前缀"
json_url = 'https://pro-robomasters-hz-n5i3.oss-cn-hangzhou.aliyuncs.com/live_json/live_game_info.json'

if getattr(sys,'frozen',False):
    script_dir = os.path.dirname(os.path.abspath(sys.executable))
    base_path = sys._MEIPASS
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = script_dir

json_path = os.path.join(script_dir,'live_data.json')
ffmpeg_path = os.path.join(base_path,'bin','ffmpeg.exe')

def download_json():
    with urllib.request.urlopen(json_url) as response:
        response_data = response.read()
        return json.loads(response_data)

def update_json():
    data = download_json()
    event_list = data['eventData']
    has_live = any(event.get('liveState') == 1 for event in event_list)
    data = data['eventData'][0]
    # 组成新的 JSON 对象
    new_data = {
        'liveState': has_live,
        'zoneLiveString': data['zoneLiveString'],
        'fpvData': data['fpvData']
    }
    # 保存到文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

if not os.path.exists(json_path):
    update_json()

# 下载任务列表
processes = []
downloading = False

def start_stop_downloads():
    global downloading
    if downloading:
        stop_downloads()
        download_button.config(text="开始录制")
    else:
        start_downloads()
        download_button.config(text="停止录制")
    downloading = not downloading

def find_src_by_label(data, label):
    for item in data:
        if item['label'] == label:
            return item['src']
    return None

def file_list():
    global main_view_var,base_view_var,red_team_var,blue_team_var,resolution_combobox
    files = []
    resolution = resolution_combobox.get()
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        zonelive = data['zoneLiveString']
        src = find_src_by_label(zonelive,resolution)
        if main_view_var.get():
            files.append(('主视角', src))
        for fpv in data['fpvData']:
            role = fpv['role']
            if red_team_var.get() and "红" in role:
                src = find_src_by_label(fpv['sources'], resolution)
                files.append((role, src))
            elif blue_team_var.get() and "蓝" in role:
                src = find_src_by_label(fpv['sources'], resolution)
                files.append((role, src))
            elif base_view_var.get() and "号机" in role:
                src = find_src_by_label(fpv['sources'], resolution)
                files.append((role, src))
    return files

def start_downloads():
    global processes
    files = file_list()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join(script_dir,'output', timestamp)
    os.makedirs(output_folder, exist_ok=True)

    # 设置录制文件前缀
    game_info = text_entry.get()
    if game_info == hint_text:
        game_info = ''
    if game_info != '':
        game_info = game_info+'_'

    # 创建并行下载的 subprocess 任务
    processes = []
    for file in files:
        output_file = game_info+file[0]+'.mp4'
        cmd = [ffmpeg_path,'-i', file[1], '-c','copy',os.path.join(output_folder, output_file)]
        process = subprocess.Popen(cmd,stdin=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(process)

def stop_downloads():
    global processes
    for process in processes:
        # 如果还在运行，发送 'q' 键命令到 ffmpeg 进程
        if process.poll() is None:
            process.stdin.write(b'q')
            process.stdin.flush()
    # 等待所有子进程完成
    for process in processes:
        process.wait()
    print("所有下载任务已停止。")
    processes = []

def on_closing():
    if downloading:
        stop_downloads()
    # 关闭窗口
    root.destroy()

def center_window(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"+{x}+{y}")

# 创建主窗口
root = tk.Tk()
root.withdraw()
root.title("RMrecord")
root.iconbitmap(os.path.join(base_path,'icon.ico'))
root.resizable(width=False, height=False)
# 创建菜单栏
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
menu_bar.add_command(label="更新 JSON", command=update_json)

frame = tk.Frame(root)
frame.grid(row=0, column=0, padx=25, pady=10,sticky='nsew')  # 使用 grid 布局

# 创建下拉选择控件
resolution_combobox = ttk.Combobox(frame, values=["540p", "720p", "1080p"])
resolution_combobox.current(1)  # 将当前选项设置为 720p
resolution_combobox.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

main_view_var = tk.BooleanVar()
red_team_var = tk.BooleanVar()
blue_team_var = tk.BooleanVar()
base_view_var = tk.BooleanVar()

main_view_check = tk.Checkbutton(frame, text="主视角", variable=main_view_var, anchor='w')
main_view_check.grid(row=1, column=0, padx=5, pady=0, sticky='ew')

base_view_check = tk.Checkbutton(frame, text="基地", variable=base_view_var, anchor='w')
base_view_check.grid(row=1, column=1, padx=5, pady=0, sticky='ew')

red_team_check = tk.Checkbutton(frame, text="红方", variable=red_team_var, anchor='w')
red_team_check.grid(row=2, column=0, padx=5, pady=0, sticky='ew')

blue_team_check = tk.Checkbutton(frame, text="蓝方", variable=blue_team_var, anchor='w')
blue_team_check.grid(row=2, column=1, padx=5, pady=0, sticky='ew')

download_button = tk.Button(frame, text="开始录制", command=start_stop_downloads)
download_button.grid(row=3, column=0, columnspan=2,padx=10,pady=10, sticky='ew')

def on_entry_focus_in(event):
    if text_entry.get() == hint_text:
        text_entry.delete(0, tk.END)
        text_entry.config(fg='black')

def on_entry_focus_out(event):
    if text_entry.get() == "":
        text_entry.insert(0, hint_text)
        text_entry.config(fg='grey')

# 添加单行文本框
text_entry = tk.Entry(frame, fg='grey')
text_entry.insert(0, hint_text)
text_entry.bind("<FocusIn>", on_entry_focus_in)
text_entry.bind("<FocusOut>", on_entry_focus_out)
text_entry.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

# 设置窗口关闭时的处理函数
root.protocol("WM_DELETE_WINDOW", on_closing)
center_window(root)
root.deiconify()
# 启动主循环
root.mainloop()