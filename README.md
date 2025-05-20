## 在程序所在文件夹打开终端

```bash
python record.py
```

![](https://cdn.nlark.com/yuque/0/2025/png/26139354/1747746252512-7acb43e6-a59a-4463-8d09-6dacca491451.png)

## 录制

- (可选)获取比赛信息
- 选择清晰度
- 选择需要录制的视角
- 点击开始录制，开始录制按钮变为停止录制
- 录制完成后点击停止录制
- (可选)设置保存文件前缀

视频将保存到 output 文件夹中



## 打包

```bash
python -m venv venv
.\venv\Scripts\activate
pip install pyinstaller
pyinstaller -w -F --add-data ".\\icon.ico;." --add-data ".\\bin\\*;.\\bin" -i .\icon.ico record.py
```

