"""
剪贴板监听模块
定时轮询系统剪贴板，检测文字和图片变化，去重后写入数据库
"""

from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QImage


class ClipboardMonitor(QObject):
    """剪贴板监听器，使用 QTimer 轮询"""

    # 当有新内容时发出信号
    new_item_added = pyqtSignal()

    def __init__(self, app, interval_ms=500):
        """
        参数:
            app: QApplication 实例
            interval_ms: 轮询间隔（毫秒）
        """
        super().__init__()
        self.clipboard = app.clipboard()
        self.last_text = ""
        self.last_image_hash = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_clipboard)
        self.timer.setInterval(interval_ms)

    def start(self):
        """开始监听"""
        # 记录当前剪贴板内容作为基线（避免启动时重复记录）
        self.last_text = self.clipboard.text() or ""
        self.timer.start()

    def stop(self):
        """停止监听"""
        self.timer.stop()

    def _check_clipboard(self):
        """检查剪贴板变化"""
        # 先检查图片（图片优先级高于文字）
        image = self.clipboard.image()
        if image and not image.isNull():
            self._handle_image(image)
            return

        # 检查文字
        text = self.clipboard.text()
        if text and text != self.last_text:
            self._handle_text(text)

    def _handle_text(self, text):
        """处理新文字"""
        if text == self.last_text:
            return
        self.last_text = text

        from src.data_manager import add_item
        add_item("text", text_content=text)
        self.new_item_added.emit()

    def _handle_image(self, qimage):
        """处理新图片"""
        from PIL import Image
        import hashlib

        # QImage -> raw bytes
        qimage = qimage.convertToFormat(QImage.Format_RGB32)
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())
        raw_bytes = bytes(ptr)

        # 哈希去重
        image_hash = hashlib.md5(raw_bytes).hexdigest()
        if image_hash == self.last_image_hash:
            return
        self.last_image_hash = image_hash

        # QImage -> PIL Image
        pil_image = Image.frombytes(
            "RGB", (qimage.width(), qimage.height()), raw_bytes, "raw", "BGRX"
        )

        # 先插入数据库获取 id
        from src.data_manager import add_item, update_image_path
        item_id = add_item("image", image_path="")

        # 压缩并保存图片
        from src.utils.image_compress import compress_and_save
        image_path = compress_and_save(pil_image, item_id)

        # 更新数据库中的图片路径
        update_image_path(item_id, image_path)
        self.new_item_added.emit()
