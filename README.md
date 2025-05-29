<div align="center">
  <img width="180" src="https://cdn.jsdelivr.net/gh/jchliao/RMrecord/icon.ico" alt="logo">
</div>

<h1 align="center">RMrecord</h1>

<p align="center">🎬 一个用于录制 RoboMaster 比赛多视角直播的轻量级工具 🎥</p>

# 🚀快速开始

## 运行程序

在项目目录下打开终端并运行：

```bash
python record.py
```

<p align="center">
  <img src="https://cdn.nlark.com/yuque/0/2025/png/26139354/1747746252512-7acb43e6-a59a-4463-8d09-6dacca491451.png">
</p>

# 📘 使用说明

## 更新JSON

点击菜单栏中的 **“更新JSON”**，程序会自动拉取当前比赛的直播数据。

## 获取比赛信息

点击菜单栏中的 **“获取比赛信息”**，程序会自动拉取当前比赛信息并填入前缀输入框。

## 选择清晰度

通过下拉框选择所需清晰度：

- 540p
- 720p
- 1080p

## 选择录制视角

勾选需要录制的视角：

- ✅ **全场**：全场机位视角
- ✅ **半场**：补充机位视角
- ✅ **红方操作手**：红方操作手视角
- ✅ **蓝方操作手**：蓝方操作手视角

## 开始/停止录制

点击 “开始录制” 后，程序会创建输出目录并开始后台录制。按钮文字变为 “停止录制”，再次点击将结束所有录制任务。

## 自定义文件前缀

录制前可在文本框中输入自定义文件名前缀。

## 输出文件结构

录制的视频文件将保存在 output 文件夹中，以比自定义文件前缀或时间戳命名。

# 📦打包

```bash
python -m venv venv
.\venv\Scripts\activate
pip install pyinstaller
pyinstaller -w -F --add-data ".\\icon.ico;." --add-data ".\\bin\\*;.\\bin" -i .\icon.ico record.py
```

