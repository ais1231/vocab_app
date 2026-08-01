# 考研英语二词汇背单词 App

> 全部代码由 **DeepSeek V4 Flash** 完成

基于 `pywebview` 的桌面背单词应用，带本地数据持久化，支持双词库切换、学习进度追踪和复习提醒。

---

## 📦 下载

[![Release](https://img.shields.io/github/v/release/ais1231/vocab_app)](https://github.com/ais1231/vocab_app/releases)

👉 **[点此下载最新版 exe](https://github.com/ais1231/vocab_app/releases/latest)**

下载后双击运行即可，无需安装 Python 或任何依赖。

---

## ✨ 功能一览

### 📖 背单词
| 功能 | 说明 |
|:---|:---|
| **双词库** | 2026考研英语二大纲（5298词） & 2027马天艺单词之间（3764词） |
| **四种学习模式** | 顺序模式 · 随机模式 · 核心词汇 · 未学习模式 |
| **三档标记** | ❌ 不会 · 😕 模糊 · ✅ 会了 |
| **复习插入** | 标记"不会/模糊"的单词会自动排队，学几个新词后插入复习 |
| **进度持久化** | 所有学习记录自动保存，下次打开继续 |

### ⌨️ 快捷键
| 操作 | 默认按键 |
|:---|:---|
| 显示释义 | `空格` |
| ❌ 不认识 | `1` / `Q` |
| 😕 模糊 | `2` / `W` |
| ✅ 认识 | `3` / `E` |
| ⬅️ 上一个 | `←` / `A` |
| ➡️ 下一个 | `→` / `D` |
| ⚙️ 设置 | `Esc` |

> 快捷键可在设置面板中自定义修改。

### 📊 数据管理
- **自动保存**：每次操作后自动持久化到 `D:\vocab_app_data\vocab_save.json`
- **导出备份**：导出完整学习进度为 JSON 文件，便于分享或迁移
- **导入备份**：导入他人的学习进度，查看其学习数据
- **重置进度**：可重置当前词书的特定模式浏览顺序，或清空当前词书全部学习进度

### 🔄 实时同步
支持多窗口数据同步（桌面窗口 + 浏览器窗口同时使用时自动保持数据一致）。

---

## 🖥️ 运行方式

### 直接运行（推荐）
下载 `发布/` 目录下的 exe 双击运行。

### 源码运行
需要 Python 3.8+：

```bash
pip install pywebview bottle screeninfo
python main_desktop.py
```

### 打包为 exe
```bash
pip install pyinstaller
pyinstaller vocab_app.spec
```

---

## 🗂️ 项目结构

```
vocab_app/
├── main_desktop.py       # pywebview 桌面窗口 + 内嵌 HTTP 服务器
├── run.py                # 纯浏览器版（http.server + 浏览器打开）
├── simple.html           # 前端 UI（全部逻辑在单 HTML 中）
├── vocab_app.spec        # PyInstaller 打包配置
├── 启动.bat              # Windows 快捷启动脚本
├── vocab_data.json       # 2026考研英语二大纲词库（5298词）
├── bbdc_vocab.json       # 2027马天艺单词之间词库（3764词）
├── books.json            # 词库元数据
└── 发布/                 # 打包好的 exe
    └── 考研词汇背单词 v3.8.exe
```

---

## 📜 更新日志

### v3.2
- 🚫 去除 exe 启动时的终端弹窗（`console=False`）
- 🎯 全面替换原生 `alert/confirm` 为自定义 Toast 和确认框
- 🐛 修复键盘快捷键回弹问题（`e.repeat` 拦截 + `preventDefault`）
- 🐛 修复切换单词书/模式时数据回弹（`checkDataSync` 不再覆盖活动状态）
- 🐛 修复导入导出数据丢失的 Bug（异步 await + 强制刷盘）
- 🐛 修复重置进度不持久化的问题（补上 `saveCurrentBookState`）
- 🔄 未学会词库改为自动同步，移除手动同步按钮

### v3.1
- 新增未完全学会词库
- 新增复习插入机制
- 新增快捷键自定义
- 优化 UI 交互

### v3.0
- 基于 pywebview 的桌面版重构
- 双词库切换
- 四种学习模式

---

## 📄 开源协议

本项目仅供个人学习使用。
