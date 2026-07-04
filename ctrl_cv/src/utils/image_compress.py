"""
图片压缩模块
将图片压缩至约 100KB 以内，保持可辨认的画质
"""

import os
from datetime import datetime

from PIL import Image

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "images")

MAX_SIZE_KB = 100  # 目标最大文件大小（KB）


def compress_and_save(image, item_id):
    """
    压缩图片并保存到 data/images/ 目录
    参数:
        image: PIL.Image 对象 或 文件路径
        item_id: 数据库记录 id
    返回:
        保存后的文件路径
    """
    os.makedirs(IMAGES_DIR, exist_ok=True)

    if isinstance(image, str):
        # 如果传入的是文件路径
        img = Image.open(image)
    else:
        img = image

    # 转换为 RGB（处理 RGBA 等格式）
    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background
    elif img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # 如果图片尺寸过大，等比缩放
    max_dimension = 1200
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{item_id}_{timestamp}.jpg"
    filepath = os.path.join(IMAGES_DIR, filename)

    # 压缩保存，逐步降低质量直到满足大小要求
    quality = 75
    img.save(filepath, "JPEG", quality=quality, optimize=True)

    while os.path.getsize(filepath) > MAX_SIZE_KB * 1024 and quality > 20:
        quality -= 10
        img.save(filepath, "JPEG", quality=quality, optimize=True)

    # 兜底：如果质量降到最低仍然超限，进一步缩小图片尺寸
    if os.path.getsize(filepath) > MAX_SIZE_KB * 1024:
        ratio = 0.6
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        img.save(filepath, "JPEG", quality=50, optimize=True)

    return filepath


def get_image_size_kb(image_path):
    """获取图片文件大小（KB）"""
    if not os.path.exists(image_path):
        return 0
    return os.path.getsize(image_path) / 1024
