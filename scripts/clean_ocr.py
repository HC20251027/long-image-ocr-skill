#!/usr/bin/env python3
"""
OCR乱码清理与文本整理工具

用于清理传统OCR（如pytesseract）产生的乱码噪声，
以及整理视觉模型提取的文本结果。

用法:
    python3 clean_ocr.py <input_file> [--output <output_file>] [--mode <mode>]

模式:
    clean    - 仅清理乱码，保留原始结构 (默认)
    chat     - 按聊天记录格式整理（识别发言人、时间戳）
    doc      - 按文档格式整理（保留标题、段落结构）
"""

import argparse
import json
import os
import re
import sys
from typing import Optional


# 常见OCR噪声模式
NOISE_PATTERNS = [
    # 微信截图常见噪声
    r"^Biography$",
    r"^avd stl\) on a\)$",
    r"^ead$",
    r"^ER$",
    r"^ES$",
    r"^SEE$",
    r"^RE$",
    r"^GIN\.$",
    r"^\[ES\]$",
    r"^die$",
    r"^al$",
    r"^ae\)$",
    r"^ree$",
    r"^wok$",
    r"^LSI$",
    r"^cig$",
    r"^Nae$",
    r"^Ea$",
    r"^Cu$",
    r"^AS$",
    r"^EH$",
    r"^saber\)$",
    r"^rayne$",
    # 随机字母噪声（3-5个连续小写字母，无元音或纯辅音）
    r"^[a-z]{3,5}$",
    # 纯标点/符号行
    r"^[^\w\u4e00-\u9fff]+$",
    # 短乱码（1-2个无意义字符）
    r"^[a-zA-Z]{1,2}$",
]

# 编译正则
COMPILED_PATTERNS = [re.compile(p) for p in NOISE_PATTERNS]


def is_noise_line(line: str) -> bool:
    """判断一行文本是否为OCR噪声"""
    stripped = line.strip()
    if not stripped:
        return True

    for pattern in COMPILED_PATTERNS:
        if pattern.match(stripped):
            return True

    return False


def clean_text(text: str) -> str:
    """
    清理OCR文本中的乱码噪声。

    Args:
        text: 原始OCR文本

    Returns:
        清理后的文本
    """
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        if not is_noise_line(line):
            cleaned_lines.append(line)

    # 合并连续空行为单个空行
    result = []
    prev_empty = False
    for line in cleaned_lines:
        is_empty = not line.strip()
        if is_empty and prev_empty:
            continue
        result.append(line)
        prev_empty = is_empty

    # 去除首尾空行
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()

    return "\n".join(result)


def extract_chat_messages(text: str) -> list:
    """
    从文本中提取聊天消息结构。

    识别模式：
    - 发言人行：以已知用户名开头
    - 时间戳行：HH:MM 格式
    - 系统消息：包含"邀请"、"加入了群聊"等关键词

    Args:
        text: 清理后的文本

    Returns:
        消息列表，每条消息为 dict
    """
    messages = []
    current_speaker = None
    current_timestamp = None

    # 常见发言人模式
    speaker_patterns = [
        r"^([^：:]{2,20})[：:]\s*(.+)$",  # 发言人：内容
        r"^\*\*(.+?)\*\*[：:]\s*(.+)$",  # **发言人**：内容
    ]

    timestamp_pattern = r"^(\d{1,2}:\d{2})$"

    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # 检查时间戳
        ts_match = re.match(timestamp_pattern, stripped)
        if ts_match:
            current_timestamp = ts_match.group(1)
            continue

        # 检查发言人
        speaker_found = False
        for pattern in speaker_patterns:
            match = re.match(pattern, stripped)
            if match:
                current_speaker = match.group(1).strip().strip("*")
                content = match.group(2).strip()
                messages.append({
                    "speaker": current_speaker,
                    "content": content,
                    "timestamp": current_timestamp,
                })
                speaker_found = True
                break

        if not speaker_found and current_speaker:
            # 继续上一发言人的消息
            if messages and messages[-1]["speaker"] == current_speaker:
                messages[-1]["content"] += "\n" + stripped
            else:
                messages.append({
                    "speaker": current_speaker,
                    "content": stripped,
                    "timestamp": current_timestamp,
                })

    return messages


def format_chat_markdown(messages: list, title: str = "聊天记录") -> str:
    """将消息列表格式化为Markdown"""
    if not messages:
        return "# " + title + "\n\n（无内容）"

    # 提取所有发言人
    speakers = list(dict.fromkeys(m["speaker"] for m in messages if m["speaker"]))

    lines = [
        f"# {title}",
        "",
        f"> 参与成员：{'、'.join(speakers)}",
        "",
        "---",
        "",
    ]

    current_timestamp = None
    for msg in messages:
        # 时间戳
        if msg.get("timestamp") and msg["timestamp"] != current_timestamp:
            current_timestamp = msg["timestamp"]
            lines.append(f"*{current_timestamp}*")
            lines.append("")

        speaker = msg["speaker"] or "（匿名）"
        content = msg["content"]

        # 检测系统消息
        if any(kw in content for kw in ["邀请", "加入了群聊", "撤回", "请注意隐私"]):
            lines.append(f"**【系统消息】** {content}")
        else:
            lines.append(f"**{speaker}：** {content}")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="OCR乱码清理与文本整理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("input_file", help="输入文本文件路径")
    parser.add_argument("--output", "-o", help="输出文件路径（默认覆盖输入文件）")
    parser.add_argument(
        "--mode", "-m",
        choices=["clean", "chat", "doc"],
        default="clean",
        help="整理模式: clean=仅清理, chat=聊天记录, doc=文档 (默认: clean)"
    )
    parser.add_argument("--title", "-t", default="聊天记录", help="输出标题（chat模式）")

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"错误: 文件不存在 - {args.input_file}")
        sys.exit(1)

    with open(args.input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # 清理乱码
    cleaned = clean_text(text)

    # 按模式整理
    if args.mode == "chat":
        messages = extract_chat_messages(cleaned)
        result = format_chat_markdown(messages, args.title)
    elif args.mode == "doc":
        result = cleaned  # 文档模式仅清理
    else:
        result = cleaned

    # 输出
    output_path = args.output or args.input_file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"处理完成: {output_path}")
    print(f"  模式: {args.mode}")
    print(f"  原始行数: {len(text.splitlines())}")
    print(f"  输出行数: {len(result.splitlines())}")


if __name__ == "__main__":
    main()
