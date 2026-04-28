# long-image-ocr-skill

> 长图切割与 OCR 文字提取技能

将长截图（微信群聊记录、网页长图、文档截图等）切割成多张小图，使用视觉模型逐段提取文字，并清理乱码、按结构整理成可读文本。

## ✨ 特性

- 🖼️ **智能切割** — 自动检测图片尺寸，按合适高度切割长图
- 👁️ **视觉OCR** — 使用视觉模型逐段读取，对深色主题/低分辨率图片效果远超传统 OCR
- 🧹 **乱码清理** — 内置常见 OCR 噪声模式库，自动清理乱码
- 💬 **聊天记录整理** — 自动识别发言人、时间戳、引用关系、系统消息
- 📄 **多格式支持** — 适配微信群聊截图、网页截图、文档截图等场景

## 📁 文件结构

```
long-image-ocr-skill/
├── SKILL.md              # 技能定义文件（完整 SOP + 使用说明）
├── README.md             # 本文件
└── scripts/
    ├── split_image.py    # 长图切割脚本
    └── clean_ocr.py      # OCR 乱码清理脚本
```

## 🚀 使用方式

### 作为 SOLO Skill 使用

将本仓库内容复制到 SOLO 的 skills 目录下即可自动识别：

```bash
cp -r long-image-ocr-skill /data/user/skills/long-image-ocr
```

触发关键词：`长图OCR`、`截图提取文字`、`聊天记录提取`、`切割长图`、`图片转文字` 等。

### 独立使用脚本

#### 切割长图

```bash
# 默认参数（切割高度 2000px）
python3 scripts/split_image.py screenshot.png

# 自定义切割高度
python3 scripts/split_image.py screenshot.png --chunk-height 1500

# 自定义输出目录
python3 scripts/split_image.py screenshot.png --output-dir ./output
```

#### 清理 OCR 文本

```bash
# 仅清理乱码
python3 scripts/clean_ocr.py ocr_output.txt --mode clean

# 按聊天记录格式整理
python3 scripts/clean_ocr.py ocr_output.txt --mode chat --title "群聊记录"

# 按文档格式整理
python3 scripts/clean_ocr.py ocr_output.txt --mode doc
```

## 📋 工作流程

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  上传长截图   │ ──▶ │  检测图片尺寸  │ ──▶ │  切割为多张小图   │ ──▶ │  视觉模型读取  │
└─────────────┘     └──────────────┘     └─────────────────┘     └──────────────┘
                                                                         │
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐            │
│  输出 Markdown│ ◀── │  按结构整理   │ ◀── │  清理乱码/去重   │ ◀──────────┘
└─────────────┘     └──────────────┘     └─────────────────┘
```

1. **检测图片** — 判断是否为长图（高度 > 3000px）
2. **切割长图** — 按固定高度切割，保存为 `chunk_01.png`, `chunk_02.png`, ...
3. **视觉模型读取** — 逐段用视觉模型提取文字（核心步骤，准确率远超 pytesseract）
4. **清理整理** — 去重、识别发言人、标注时间戳、保留链接
5. **输出文件** — 生成结构化的 Markdown 文件

## 🔧 依赖

- Python 3.7+
- Pillow (`pip install pillow`)

## 📝 注意事项

- 切割高度建议：微信聊天 1500-2000px，网页截图 2000-2500px
- 视觉模型每次最多并行读取 3 张图片
- 传统 OCR（pytesseract）对深色主题截图效果很差，建议优先使用视觉模型

## 📄 License

MIT
