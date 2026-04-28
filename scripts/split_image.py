#!/usr/bin/env python3
"""
长图切割脚本 - 将长截图按固定高度切割成多张小图

用法:
    python3 split_image.py <input_image> [--output-dir <dir>] [--chunk-height <pixels>]

示例:
    python3 split_image.py screenshot.png
    python3 split_image.py screenshot.png --chunk-height 1500 --output-dir /workspace/output
"""

import argparse
import os
import sys
from PIL import Image


def split_image(input_path: str, output_dir: str, chunk_height: int) -> list:
    """
    将长图切割成多个切片。

    Args:
        input_path: 输入图片路径
        output_dir: 输出目录
        chunk_height: 每个切片的高度（像素）

    Returns:
        切片文件路径列表
    """
    # 验证输入文件
    if not os.path.exists(input_path):
        print(f"错误: 文件不存在 - {input_path}")
        sys.exit(1)

    # 打开图片
    img = Image.open(input_path)
    width, height = img.size

    print(f"图片信息:")
    print(f"  路径: {input_path}")
    print(f"  尺寸: {width}x{height} (宽x高)")
    print(f"  模式: {img.mode}")
    print(f"  切割高度: {chunk_height}px")

    # 判断是否需要切割
    if height <= chunk_height:
        print(f"\n图片高度 ({height}px) 不超过切割高度 ({chunk_height}px)，无需切割。")
        print("建议直接使用视觉模型读取整张图片。")
        return [input_path]

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 计算切片数量
    num_chunks = (height + chunk_height - 1) // chunk_height
    print(f"\n将切割为 {num_chunks} 个部分")
    print("-" * 50)

    # 切割图片
    chunk_paths = []
    for i in range(num_chunks):
        top = i * chunk_height
        bottom = min((i + 1) * chunk_height, height)
        actual_height = bottom - top

        # 切割
        chunk = img.crop((0, top, width, bottom))

        # 保存
        chunk_filename = f"chunk_{i + 1:02d}.png"
        chunk_path = os.path.join(output_dir, chunk_filename)
        chunk.save(chunk_path, optimize=True)
        chunk_paths.append(chunk_path)

        print(f"  [{i + 1:02d}/{num_chunks}] {chunk_filename}"
              f"  (像素: {top}-{bottom}, 高度: {actual_height}px)")

    print("-" * 50)
    print(f"切割完成! 共 {num_chunks} 个切片")
    print(f"输出目录: {output_dir}")

    return chunk_paths


def main():
    parser = argparse.ArgumentParser(
        description="长图切割工具 - 将长截图按固定高度切割成多张小图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s screenshot.png                    # 使用默认参数
  %(prog)s screenshot.png --chunk-height 1500  # 自定义切割高度
  %(prog)s screenshot.png --output-dir ./output  # 自定义输出目录
        """
    )

    parser.add_argument(
        "input_image",
        help="输入图片路径"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="/workspace/split_images",
        help="输出目录 (默认: /workspace/split_images)"
    )
    parser.add_argument(
        "--chunk-height", "-c",
        type=int,
        default=2000,
        help="每个切片的高度，单位像素 (默认: 2000)"
    )

    args = parser.parse_args()
    split_image(args.input_image, args.output_dir, args.chunk_height)


if __name__ == "__main__":
    main()
