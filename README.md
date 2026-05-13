<div align="center">
  <img width="180" src="https://cdn.jsdelivr.net/gh/jchliao/RMrecord/assets/icon.ico" alt="logo">
</div>

<h1 align="center">RMrecord</h1>

<p align="center">🎬 一个用于录制 RoboMaster 比赛多视角直播的轻量级工具 🎥</p>

# 📘 项目简介

RMrecord 会根据比赛直播数据自动识别可录制的视角，并调用 ffmpeg 进行后台录制。支持按赛区选择、按清晰度选择，以及为输出文件添加自定义前缀。

# 🚀 快速开始

## 运行程序

在项目目录下打开终端并运行：

```bash
python record.py
```

<p align="center">
  <img src="https://cdn.nlark.com/yuque/0/2025/png/26139354/1747746252512-7acb43e6-a59a-4463-8d09-6dacca491451.png">
</p>

# 📘 使用说明

## 选择赛区

启动后会自动读取赛区列表。选择赛区后，程序会刷新对应的直播数据，并更新当前可用的录制视角。

## 获取比赛信息

点击菜单栏中的 **“获取比赛信息”**，程序会自动拉取当前进行中的比赛信息，并把“第xx场.学校简称.战队名.vs.学校简称.战队名.第x局”填入文件前缀输入框。

## 选择清晰度

支持以下清晰度：

- 540p
- 720p
- 1080p

默认值是 720p。

## 选择录制视角

界面会根据当前直播数据自动启用或禁用可用视角。可录制项包括：

勾选需要录制的视角：

- 全场：主画面直播流
- 其他：补充机位或其它可用画面
- 红方操作手：红方 FPV 视角
- 蓝方操作手：蓝方 FPV 视角

## 开始/停止录制

点击“开始录制”后，程序会在项目目录下创建 output 文件夹，并按当前时间或自定义前缀生成子目录。按钮会切换为“停止录制”，再次点击即可结束所有录制任务。

## 自定义文件前缀

可在底部输入框中填写文件前缀。

如果前缀中包含英文句点，程序会把当前赛区名称拼接到前缀前面，再生成输出目录和视频文件名。

## 输出文件结构

录制文件会保存为 mp4，命名格式大致如下：

```text
output/20260513_123456/前缀_全场.mp4
output/20260513_123456/前缀_红方操作手.mp4
```

如果同名目录已存在，程序会自动追加序号避免覆盖。

# 📦 打包

项目提供了一个打包脚本 [build.py](build.py)。在 Windows 下可以直接运行：

```bash
python build.py
```

可选参数：

- `--withffmpeg`：把 [bin](bin) 目录中的 ffmpeg 一起打包进去
- `--withupx`：使用 UPX 压缩可执行文件

示例：

```bash
python build.py --withffmpeg --withupx
```

# 📁 目录说明

- [record.py](record.py)：主程序
- [build.py](build.py)：打包脚本
- [assets/team_names.json](assets/team_names.json)：学校简称映射
- [bin](bin)：本地 ffmpeg 依赖

