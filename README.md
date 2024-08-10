## 在程序所在文件夹打开终端

```bash
python record.py
```

## 录制

- 选择清晰度
- 选择红蓝方

- 开始录制

- 停止录制

视频将保存到 output 文件夹中



## 打包

```bash
python -m venv venv
.\venv\Scripts\activate
pip install pyinstaller
pyinstaller -w -F --add-data ".\\icon.ico;." --add-data ".\\bin\\*;.\\bin" -i .\icon.ico record.py
```

