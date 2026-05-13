import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import os
import sys
from datetime import datetime
import urllib.request
import json
import ctypes
import shutil
import logging

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

HINT_TEXT = "文件前缀"
LIVE_GAME_INFO_URL = "https://rm-static.djicdn.com/live_json/live_game_info.json"
CURRENT_MATCHE_URL = (
    "https://rm-static.djicdn.com/live_json/current_and_next_matches.json"
)

if getattr(sys, "frozen", False):
    script_exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    base_path = sys._MEIPASS  # type: ignore
else:
    script_exe_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = script_exe_dir

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(script_exe_dir, "rmrecord.log"), encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def find_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        logger.info(f"在系统环境变量中找到ffmpeg: {ffmpeg_path}")
        return ffmpeg_path
    exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    local_paths = [
        os.path.join(base_path, exe_name),
        os.path.join(base_path, "bin", exe_name),
    ]
    for path in local_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            logger.info(f"在本地路径找到ffmpeg: {path}")
            return path
    logger.error("未找到ffmpeg可执行文件")
    messagebox.showerror("错误", "未找到 ffmpeg，请确保其已安装并添加到系统环境变量")
    sys.exit(1)


# 在初始化时查找 ffmpeg 路径
ffmpeg_path = find_ffmpeg()
json_path = os.path.join(script_exe_dir, "live_data.json")


def download_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            response_data = response.read()
            return json.loads(response_data)
    except Exception as e:
        logger.error(f"下载JSON失败: {e}")
        return None


def load_team_names():
    team_names_path = os.path.join(base_path, "assets", "team_names.json")
    with open(team_names_path, "r", encoding="utf-8") as f:
        return json.load(f)


team_names = load_team_names()


def get_college_abbreviation(college_name):
    """获取学校简称"""
    return team_names.get(college_name, {}).get("学校简称", college_name)


def fetch_match_info():
    try:
        data = download_json(CURRENT_MATCHE_URL)
        if not data:
            logger.warning("获取比赛信息失败: 网络请求失败")
            return
        for item in data:
            current_match = item.get("currentMatch")
            if not current_match:
                continue
            order_number = current_match.get("orderNumber")
            round_number = current_match.get("round")
            blue_team = (
                current_match.get("blueSide", {}).get("player", {}).get("team", {})
            )
            red_team = (
                current_match.get("redSide", {}).get("player", {}).get("team", {})
            )
            if not blue_team or not red_team:
                continue
            blue_college = blue_team.get("collegeName", "")
            blue_name = blue_team.get("name", "")
            red_college = red_team.get("collegeName", "")
            red_name = red_team.get("name", "")
            if not (order_number and round_number):
                continue
            red_college_abbr = get_college_abbreviation(red_college)
            blue_college_abbr = get_college_abbreviation(blue_college)
            match_info = (
                (
                    f"第{int(order_number):02}场."
                    f"{red_college_abbr}."
                    f"{red_name}."
                    f"vs."
                    f"{blue_college_abbr}."
                    f"{blue_name}."
                    f"第{round_number}局"
                )
                .replace("（", "(")
                .replace("）", ")")
            )
            root.after(
                0,
                lambda: (
                    text_entry.delete(0, tk.END),
                    text_entry.insert(0, match_info),
                    text_entry.config(foreground="black"),
                ),
            )
            return
        root.after(
            0,
            lambda: messagebox.showwarning(
                "提示",
                "当前没有进行中的比赛",
            ),
        )
    except Exception as e:
        logger.error(f"获取比赛信息失败: {e}")
        root.after(
            0,
            lambda: messagebox.showwarning(
                "提示",
                "当前没有进行中的比赛",
            ),
        )


def get_current_match():
    threading.Thread(target=fetch_match_info, daemon=True).start()


def get_all_zones():
    """获取所有赛区列表"""
    try:
        data = download_json(LIVE_GAME_INFO_URL)
        if data is None:
            print("获取赛区列表失败: 网络请求失败")
            return []
        event_list = data.get("eventData", [])
        zones = []
        for e in event_list:
            zone_name = e.get("zoneName", "")
            if zone_name:
                zones.append(zone_name)
        return zones
    except Exception as e:
        logger.error(f"获取赛区列表失败: {e}")
        return []


def get_live_game_info(zone_name=None):
    data = download_json(LIVE_GAME_INFO_URL)
    if data is None:
        return None
    event_list = data.get("eventData", [])
    event = None

    # 如果指定了赛区，直接查找该赛区
    if zone_name:
        for e in event_list:
            if e.get("zoneName") == zone_name:
                event = e
                break
    else:
        # 否则，查找今天有比赛的赛区
        today_str = datetime.now().strftime("%Y-%m-%d")
        for e in event_list:
            zone_dates = e.get("zoneDate", [])
            if today_str in zone_dates:
                event = e
                break
        if event is None and event_list:
            event = event_list[0]
            messagebox.showwarning("提示", "当前不在比赛期间")
    return event


def update_json(event=None, zone_name=None):
    def do_update():
        if event is None:
            local_event = get_live_game_info(zone_name)
        else:
            local_event = event
        if local_event:
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "zoneName": local_event.get("zoneName", ""),
                            "liveState": local_event.get("liveState", 0),
                            "zoneLiveString": local_event.get("zoneLiveString", []),
                            "fpvData": local_event.get("fpvData", []),
                        },
                        f,
                        ensure_ascii=False,
                        indent=4,
                    )
            except Exception as e:
                logger.error(f"更新JSON文件失败: {e}")

    # 在后台线程中执行更新操作
    threading.Thread(target=do_update, daemon=True).start()


def check_and_update_json():
    try:
        event = get_live_game_info()
        update_json(event)
    except Exception as e:
        logger.error(f"初始化 JSON 检查失败: {e}")


def init_ui_from_json():
    """根据live_data.json初始化UI状态"""
    try:
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            local_zone_name = data.get("zoneName", "")
            # 检查下拉框是否已有值
            if zone_combobox["values"]:
                # 如果本地赛区存在于下拉框中，设置为默认
                if local_zone_name and local_zone_name in zone_combobox["values"]:
                    zone_combobox.set(local_zone_name)
            else:
                # 如果下拉框还没有值，先设置本地赛区，稍后更新下拉框时会自动匹配
                if local_zone_name:
                    zone_combobox.set(local_zone_name)
            # 更新复选框状态
            update_checkboxes_state()
    except Exception as e:
        logger.error(f"初始化UI失败: {e}")


threading.Thread(target=check_and_update_json, daemon=True).start()

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
        if item["label"] == label:
            return item["src"]
    return None


def file_list():
    files = []
    resolution = resolution_combobox.get()
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    zonelive = data.get("zoneLiveString", [])
    main_src = find_src_by_label(zonelive, resolution)

    if main_view_var.get() and main_src:
        files.append(("全场", main_src))

    fpv_data = data.get("fpvData", [])

    for fpv in fpv_data:
        role = fpv.get("role", "")
        sources = fpv.get("sources", [])
        fpv_src = find_src_by_label(sources, resolution)

        if not fpv_src:
            continue

        if "红" in role:
            if red_team_var.get():
                files.append((role, fpv_src))
        elif "蓝" in role:
            if blue_team_var.get():
                files.append((role, fpv_src))
        else:
            if others_view_var.get():
                files.append((role, fpv_src))

    return files


def get_current_zone():
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("zoneName", "")
    except Exception as e:
        logger.error(f"获取当前赛区失败: {e}")
        return ""


def get_unique_folder(base_dir, out_dir, folder_name):
    output_folder = os.path.join(base_dir, out_dir, folder_name)
    counter = 1
    unique_folder = output_folder
    while os.path.exists(unique_folder):
        unique_folder = f"{output_folder}_{counter}"
        counter += 1
    os.makedirs(unique_folder)
    return unique_folder


def start_downloads():
    global processes
    files = file_list()
    dirmane = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 设置录制文件前缀
    game_info = text_entry.get()
    if game_info == HINT_TEXT:
        game_info = ""
    if game_info:
        dirmane = game_info.split(".")[0]
        if "." in game_info:
            zone_name = get_current_zone()
            if zone_name:
                dirmane = f"{zone_name}{dirmane}"
        game_info += "_"
    output_folder = get_unique_folder(script_exe_dir, "output", dirmane)
    os.makedirs(output_folder, exist_ok=True)
    # 创建并行下载的 subprocess 任务
    processes = []
    for file in files:
        output_file = game_info + file[0] + ".mp4"
        cmd = [
            ffmpeg_path,
            "-i",
            file[1],
            "-c",
            "copy",
            os.path.join(output_folder, output_file),
        ]
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW
        )
        processes.append(process)


def stop_downloads():
    global processes
    for process in processes:
        # 如果还在运行，发送 'q' 键命令到 ffmpeg 进程
        if process.poll() is None:
            try:
                process.stdin.write(b"q")
                process.stdin.flush()
                process.stdin.close()
            except Exception as e:
                logger.error(f"关闭进程stdin失败: {e}")
    # 等待所有子进程完成
    for process in processes:
        process.wait()
    logger.info("所有下载任务已停止。")
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
    root.minsize(window_width, window_height)


# 创建主窗口
root = tk.Tk()
root.withdraw()
root.title("RMrecord")
root.iconbitmap(os.path.join(base_path, "assets", "icon.ico"))
root.resizable(width=False, height=False)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
# 创建菜单栏
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
menu_bar.add_command(label="获取比赛信息", command=get_current_match)
frame = ttk.Frame(root)
frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # 使用 grid 布局

# 创建赛区选择下拉框
zone_label = ttk.Label(frame, text="赛区选择:")
zone_combobox = ttk.Combobox(frame)


# 在后台线程中获取赛区列表
def load_zones():
    zones = get_all_zones()
    # 在主线程中更新下拉框
    root.after(0, lambda: update_zone_combobox(zones))


def update_zone_combobox(zones):
    # 保存当前已设置的值
    current_value = zone_combobox.get()
    zone_combobox["values"] = zones
    if zones:
        # 如果当前值在新的选项列表中，保持不变
        if current_value in zones:
            zone_combobox.set(current_value)
        else:
            # 否则设置为第一个选项
            zone_combobox.current(0)


# 启动后台线程获取赛区列表

threading.Thread(target=load_zones, daemon=True).start()

# 创建分辨率选择下拉框
resolution_label = ttk.Label(frame, text="分辨率:")
resolution_combobox = ttk.Combobox(frame, values=["540p", "720p", "1080p"])
resolution_combobox.current(1)  # 将当前选项设置为 720p

# 布局控件
zone_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
zone_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
resolution_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
resolution_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")


def update_checkboxes_state():
    """根据live_data.json中的数据更新复选框的可用状态"""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 检查zoneLiveString是否有数据，控制全场选项
        zone_live_string = data.get("zoneLiveString", [])
        has_main_stream = len(zone_live_string) > 0
        main_view_check.config(state="normal" if has_main_stream else "disabled")
        if not has_main_stream:
            main_view_var.set(False)

        # 检查fpvData中的角色，控制红蓝方和其他选项
        fpv_data = data.get("fpvData", [])
        has_red = False
        has_blue = False
        has_others = False

        for fpv in fpv_data:
            role = fpv.get("role", "")
            if "红" in role:
                has_red = True
            elif "蓝" in role:
                has_blue = True
            else:
                has_others = True

        # 更新红方复选框
        red_team_check.config(state="normal" if has_red else "disabled")
        if not has_red:
            red_team_var.set(False)

        # 更新蓝方复选框
        blue_team_check.config(state="normal" if has_blue else "disabled")
        if not has_blue:
            blue_team_var.set(False)

        # 更新其他复选框
        others_view_check.config(state="normal" if has_others else "disabled")
        if not has_others:
            others_view_var.set(False)

    except Exception as e:
        logger.error(f"更新复选框状态失败: {e}")


# 赛区选择事件处理
def on_zone_select(event):
    selected_zone = zone_combobox.get()
    if selected_zone:

        def update_after_json():
            update_json(zone_name=selected_zone)
            # 等待JSON更新完成后再更新复选框状态
            root.after(500, update_checkboxes_state)

        # 在后台线程中执行更新操作
        threading.Thread(target=update_after_json, daemon=True).start()


zone_combobox.bind("<<ComboboxSelected>>", on_zone_select)


main_view_var = tk.BooleanVar()
red_team_var = tk.BooleanVar()
blue_team_var = tk.BooleanVar()
others_view_var = tk.BooleanVar()

main_view_check = ttk.Checkbutton(frame, text="全场", variable=main_view_var)
main_view_check.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

others_view_check = ttk.Checkbutton(frame, text="其他", variable=others_view_var)
others_view_check.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

red_team_check = ttk.Checkbutton(frame, text="红方操作手", variable=red_team_var)
red_team_check.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

blue_team_check = ttk.Checkbutton(frame, text="蓝方操作手", variable=blue_team_var)
blue_team_check.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

download_button = ttk.Button(frame, text="开始录制", command=start_stop_downloads)
download_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")


def on_entry_focus_in(event):
    if text_entry.get() == HINT_TEXT:
        text_entry.delete(0, tk.END)
        text_entry.config(foreground="black")


def on_entry_focus_out(event):
    if text_entry.get() == "":
        text_entry.insert(0, HINT_TEXT)
        text_entry.config(foreground="grey")


text_entry = ttk.Entry(frame, foreground="grey")
text_entry.insert(0, HINT_TEXT)
text_entry.bind("<FocusIn>", on_entry_focus_in)
text_entry.bind("<FocusOut>", on_entry_focus_out)
text_entry.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# 设置窗口关闭时的处理函数
root.protocol("WM_DELETE_WINDOW", on_closing)
center_window(root)
root.update_idletasks()
root.after(200, init_ui_from_json)
root.deiconify()
# 启动主循环
root.mainloop()
