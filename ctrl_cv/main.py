"""
历史粘贴板 — 程序入口
一款 Windows 桌面工具，记录复制过的文字和图片，支持搜索、置顶、删除和过期清理。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QStatusBar, QMenu, QAction, QMessageBox, QTextEdit,
    QSplitter, QComboBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QColor


# ═══════════════════════════════════════════════════════════════
# 配色常量
# ═══════════════════════════════════════════════════════════════

COLOR_BG          = "#F0F6FB"   # 主背景
COLOR_CARD        = "#FFFFFF"   # 卡片
COLOR_PINNED      = "#E3F0FA"   # 置顶卡片背景
COLOR_PRIMARY     = "#5B9BD5"   # 主色调
COLOR_PRIMARY_DARK= "#3A7BC8"   # 深主色
COLOR_TEXT        = "#333333"   # 正文
COLOR_TEXT_SUB    = "#888888"   # 辅助文字
COLOR_BORDER      = "#DDE8F0"   # 边框
COLOR_DANGER      = "#E74C3C"   # 危险操作

# ═══════════════════════════════════════════════════════════════
# 样式表
# ═══════════════════════════════════════════════════════════════

APP_STYLE = f"""
    QMainWindow {{
        background-color: {COLOR_BG};
    }}
    QWidget {{
        font-family: "Microsoft YaHei";
    }}
"""

TOOLBAR_STYLE = f"""
    QWidget {{
        background-color: {COLOR_CARD};
        border-bottom: 1px solid {COLOR_BORDER};
    }}
    QLineEdit {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 10pt;
        background-color: #F5F8FB;
        color: {COLOR_TEXT};
    }}
    QLineEdit:focus {{
        border-color: {COLOR_PRIMARY};
    }}
    QPushButton {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 10pt;
        background-color: #F5F8FB;
        color: {COLOR_TEXT};
    }}
    QPushButton:hover {{
        background-color: {COLOR_PINNED};
        border-color: {COLOR_PRIMARY};
    }}
    QComboBox {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 10pt;
        background-color: #F5F8FB;
        color: {COLOR_TEXT};
    }}
    QComboBox:hover {{
        border-color: {COLOR_PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_CARD};
        border: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_PINNED};
    }}
"""

LIST_STYLE = f"""
    QListWidget {{
        background-color: transparent;
        border: none;
        padding: 6px;
        font-size: 10pt;
        color: {COLOR_TEXT};
        outline: none;
    }}
    QListWidget::item {{
        background-color: {COLOR_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 10px 12px;
        margin: 2px 0px;
    }}
    QListWidget::item:hover {{
        background-color: #F5F8FB;
        border-color: {COLOR_PRIMARY};
    }}
    QListWidget::item:selected {{
        background-color: {COLOR_PINNED};
        border-color: {COLOR_PRIMARY};
    }}
"""

DETAIL_STYLE = f"""
    QFrame {{
        background-color: {COLOR_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
    }}
    QLabel {{
        color: {COLOR_TEXT};
        background-color: transparent;
    }}
    QTextEdit {{
        background-color: transparent;
        border: none;
        color: {COLOR_TEXT};
        font-size: 10pt;
    }}
"""

STATUS_STYLE = f"""
    QStatusBar {{
        background-color: {COLOR_CARD};
        border-top: 1px solid {COLOR_BORDER};
        font-size: 9pt;
        color: {COLOR_TEXT_SUB};
        padding: 4px 10px;
    }}
"""

MENU_STYLE = f"""
    QMenu {{
        background-color: {COLOR_CARD};
        border: 1px solid {COLOR_BORDER};
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px;
    }}
    QMenu::item:selected {{
        background-color: {COLOR_PINNED};
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {COLOR_BORDER};
        margin: 4px 8px;
    }}
"""


# ═══════════════════════════════════════════════════════════════
# 主窗口
# ═══════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """历史粘贴板主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("历史粘贴板")
        self.setMinimumSize(440, 600)
        self.resize(440, 680)

        self._init_backend()
        self._build_ui()
        self.refresh_list()
        self.monitor.start()

    # ─── 后端 ─────────────────────────────────────────

    def _init_backend(self):
        from src.data_manager import init_db
        init_db()

        from src.clipboard_monitor import ClipboardMonitor
        self.monitor = ClipboardMonitor(app)
        self.monitor.new_item_added.connect(self.refresh_list)

    # ─── 界面构建 ─────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet(APP_STYLE)

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._toolbar())

        # 列表 + 详情面板（用 splitter 分割）
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {COLOR_BORDER}; }}")

        # 列表区域
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(LIST_STYLE)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._on_context_menu)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.splitter.addWidget(self.list_widget)

        # 详情面板
        self.detail_frame = QFrame()
        self.detail_frame.setStyleSheet(DETAIL_STYLE)
        self.detail_frame.setVisible(False)
        self._build_detail_panel()
        self.splitter.addWidget(self.detail_frame)

        # 初始比例：列表占大头
        self.splitter.setSizes([380, 200])
        root.addWidget(self.splitter, stretch=1)

        # 状态栏
        self._build_statusbar()

    def _toolbar(self):
        bar = QWidget(self)
        bar.setFixedHeight(44)
        bar.setStyleSheet(TOOLBAR_STYLE)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文字...")
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input, stretch=1)

        self.date_combo = QComboBox()
        self.date_combo.addItems(["全部时间", "今天", "近3天", "近7天"])
        self.date_combo.currentIndexChanged.connect(self._on_search)
        self.date_combo.setFixedWidth(105)
        layout.addWidget(self.date_combo)

        self.settings_btn = QPushButton("设置")
        self.settings_btn.setFixedWidth(60)
        self.settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(self.settings_btn)

        return bar

    def _build_detail_panel(self):
        """详情面板：显示完整文字或图片预览"""
        layout = QVBoxLayout(self.detail_frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 标题行
        header = QHBoxLayout()
        self.detail_type_label = QLabel()
        self.detail_type_label.setFont(QFont("Microsoft YaHei", 9))
        self.detail_type_label.setStyleSheet(f"color: {COLOR_TEXT_SUB};")
        header.addWidget(self.detail_type_label)

        header.addStretch()

        copy_btn = QPushButton("复制")
        copy_btn.setFixedWidth(48)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLOR_PRIMARY};
                border-radius: 4px;
                padding: 3px 12px;
                font-size: 9pt;
                background-color: {COLOR_PRIMARY};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {COLOR_PRIMARY_DARK};
            }}
        """)
        copy_btn.clicked.connect(self._copy_current_item)
        header.addWidget(copy_btn)
        layout.addLayout(header)

        # 文字显示区
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(200)
        layout.addWidget(self.detail_text)

        # 图片显示区
        self.detail_image_scroll = QScrollArea()
        self.detail_image_scroll.setWidgetResizable(True)
        self.detail_image_scroll.setStyleSheet("border: none; background: transparent;")
        self.detail_image_label = QLabel()
        self.detail_image_label.setAlignment(Qt.AlignCenter)
        self.detail_image_scroll.setWidget(self.detail_image_label)
        layout.addWidget(self.detail_image_scroll)

    def _build_statusbar(self):
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(STATUS_STYLE)
        self.status_bar.setFont(QFont("Microsoft YaHei", 9))

        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        self.setStatusBar(self.status_bar)

    # ─── 数据加载 ─────────────────────────────────────

    def refresh_list(self):
        """从数据库加载并刷新列表"""
        from src.data_manager import get_items

        keyword = self.search_input.text().strip() or None
        date_from = self._get_date_filter()

        items = get_items(keyword=keyword, date_from=date_from)
        self.list_widget.clear()

        if not items:
            empty = QListWidgetItem("暂无复制记录")
            empty.setFlags(Qt.NoItemFlags)
            empty.setData(Qt.UserRole, -1)
            empty.setForeground(QColor(COLOR_TEXT_SUB))
            self.list_widget.addItem(empty)
            self.detail_frame.setVisible(False)
        else:
            for item in items:
                self._make_list_item(item)

        self._update_status()

    def _make_list_item(self, item):
        """创建一条列表项"""
        # 内容预览
        if item["content_type"] == "image":
            preview = "[图片]"
        else:
            text = item["text_content"] or ""
            preview = text.split("\n")[0]
            if len(preview) > 25:
                preview = preview[:25] + "..."

        # 时间显示
        created = item["created_at"]
        if "T" in created:
            d, t = created.split("T")
            time_str = f"{d[5:]} {t[:5]}"  # "MM-DD HH:MM"
        else:
            time_str = created

        if item["is_pinned"]:
            display = f"[置顶] {time_str}  |  {preview}"
        else:
            display = f"{time_str}  |  {preview}"

        widget_item = QListWidgetItem(display)
        widget_item.setData(Qt.UserRole, item["id"])
        from PyQt5.QtCore import QSize
        widget_item.setSizeHint(widget_item.sizeHint() + QSize(0, 8))

        # 置顶项：浅蓝底色 + 深色文字
        if item["is_pinned"]:
            widget_item.setBackground(QColor(COLOR_PINNED))
        else:
            widget_item.setBackground(QColor(COLOR_CARD))

        self.list_widget.addItem(widget_item)

    def _get_date_filter(self):
        """根据日期下拉框返回筛选起始时间"""
        from datetime import datetime, timedelta

        idx = self.date_combo.currentIndex()
        if idx == 0:  # 全部时间
            return None

        now = datetime.now()
        if idx == 1:  # 今天
            dt = now.replace(hour=0, minute=0, second=0)
        elif idx == 2:  # 近3天
            dt = now - timedelta(days=3)
        elif idx == 3:  # 近7天
            dt = now - timedelta(days=7)
        else:
            return None

        return dt.strftime("%Y-%m-%dT00:00:00")

    def _update_status(self):
        from src.data_manager import get_total_count
        from src.utils.config import get_retention_days

        count = get_total_count()
        days = get_retention_days()
        self.status_label.setText(f"共 {count} 条记录 | 保留 {days} 天")

    # ─── 交互 ─────────────────────────────────────────

    def _on_search(self):
        self.detail_frame.setVisible(False)
        self.current_item_id = None
        self.refresh_list()

    def _on_item_clicked(self, item):
        """单击列表项：展开详情"""
        item_id = item.data(Qt.UserRole)
        if item_id == -1:
            return

        self.current_item_id = item_id
        self._show_detail(item_id)

    def _show_detail(self, item_id):
        """在详情面板显示完整内容"""
        from src.data_manager import get_item_by_id

        record = get_item_by_id(item_id)
        if not record:
            return

        self.detail_frame.setVisible(True)

        # 格式化时间
        created = record["created_at"]
        if "T" in created:
            d, t = created.split("T")
            time_str = f"{d} {t[:5]}"
        else:
            time_str = created

        if record["content_type"] == "text":
            self.detail_type_label.setText(f"文字 | {time_str}")
            self.detail_text.setVisible(True)
            self.detail_text.setText(record["text_content"] or "")
            self.detail_image_scroll.setVisible(False)
        else:
            self.detail_type_label.setText(f"图片 | {time_str}")
            self.detail_text.setVisible(False)
            self.detail_image_scroll.setVisible(True)

            if record["image_path"] and os.path.exists(record["image_path"]):
                pixmap = QPixmap(record["image_path"])
                # 缩放到详情面板宽度
                available = self.detail_frame.width() - 24
                if pixmap.width() > available:
                    pixmap = pixmap.scaledToWidth(available, Qt.SmoothTransformation)
                self.detail_image_label.setPixmap(pixmap)
            else:
                self.detail_image_label.setText("图片文件已丢失")

    def _copy_current_item(self):
        """复制当前展开的内容到剪贴板"""
        if not hasattr(self, "current_item_id") or not self.current_item_id:
            return

        from src.data_manager import get_item_by_id
        record = get_item_by_id(self.current_item_id)
        if not record:
            return

        clipboard = app.clipboard()
        if record["content_type"] == "text":
            clipboard.setText(record["text_content"])
        else:
            if record["image_path"] and os.path.exists(record["image_path"]):
                pixmap = QPixmap(record["image_path"])
                clipboard.setPixmap(pixmap)
        self.status_label.setText("已复制到剪贴板")

    def _on_context_menu(self, pos):
        """右键菜单"""
        current = self.list_widget.itemAt(pos)
        if not current:
            return

        item_id = current.data(Qt.UserRole)
        if item_id == -1:
            return

        from src.data_manager import get_item_by_id
        record = get_item_by_id(item_id)
        if not record:
            return

        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)
        menu.setFont(QFont("Microsoft YaHei", 10))

        # 复制
        copy_action = menu.addAction("复制内容")
        copy_action.triggered.connect(lambda: self._do_copy(item_id))

        # 置顶
        if record["is_pinned"]:
            pin_action = menu.addAction("取消置顶")
        else:
            pin_action = menu.addAction("置顶")
        pin_action.triggered.connect(lambda: self._do_toggle_pin(item_id))

        menu.addSeparator()

        # 删除
        delete_action = menu.addAction("删除")
        delete_action.setIconText("删除")
        delete_action.triggered.connect(lambda: self._do_delete(item_id))

        menu.exec_(self.list_widget.mapToGlobal(pos))

    def _do_copy(self, item_id):
        from src.data_manager import get_item_by_id
        record = get_item_by_id(item_id)
        if not record:
            return

        clipboard = app.clipboard()
        if record["content_type"] == "text":
            clipboard.setText(record["text_content"])
        else:
            if record["image_path"] and os.path.exists(record["image_path"]):
                clipboard.setPixmap(QPixmap(record["image_path"]))
        self.status_label.setText("已复制到剪贴板")

    def _do_toggle_pin(self, item_id):
        from src.data_manager import toggle_pin
        toggle_pin(item_id)
        self.refresh_list()

    def _do_delete(self, item_id):
        msg = QMessageBox(self)
        msg.setWindowTitle("确认删除")
        msg.setText("确定要删除这条记录吗？")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("删除")
        msg.button(QMessageBox.No).setText("取消")

        if msg.exec_() == QMessageBox.Yes:
            from src.data_manager import get_item_by_id, soft_delete
            record = get_item_by_id(item_id)
            if record and record["image_path"] and os.path.exists(record["image_path"]):
                try:
                    os.remove(record["image_path"])
                except OSError:
                    pass

            soft_delete(item_id)
            self.detail_frame.setVisible(False)
            self.refresh_list()
            self.status_label.setText("已删除")

    # ─── 设置对话框 ───────────────────────────────────

    def _on_settings(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QButtonGroup, QRadioButton

        dlg = QDialog(self)
        dlg.setWindowTitle("设置")
        dlg.setFixedSize(300, 170)
        dlg.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_CARD};
            }}
            QLabel {{
                font-size: 11pt;
                color: {COLOR_TEXT};
            }}
            QRadioButton {{
                font-size: 10pt;
                color: {COLOR_TEXT};
            }}
            QPushButton {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 10pt;
                background-color: #F5F8FB;
                color: {COLOR_TEXT};
            }}
            QPushButton:hover {{
                background-color: {COLOR_PINNED};
                border-color: {COLOR_PRIMARY};
            }}
        """)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)

        layout.addWidget(QLabel("复制内容保留天数："))

        from src.utils.config import get_retention_days, set_retention_days
        current = get_retention_days()

        radios = {}
        group = QButtonGroup(dlg)
        row = QHBoxLayout()
        for days in [1, 3, 5]:
            r = QRadioButton(f"{days} 天")
            if days == current:
                r.setChecked(True)
            group.addButton(r)
            row.addWidget(r)
            radios[days] = r
        layout.addLayout(row)

        btns = QHBoxLayout()
        btns.addStretch()

        def save():
            for days, r in radios.items():
                if r.isChecked():
                    set_retention_days(days)
                    break
            self._update_status()
            dlg.accept()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(save)
        btns.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dlg.reject)
        btns.addWidget(cancel_btn)

        layout.addLayout(btns)
        dlg.exec_()

    # ─── 关闭 ─────────────────────────────────────────

    def closeEvent(self, event):
        self.monitor.stop()
        event.accept()


# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("历史粘贴板")
    app.setFont(QFont("Microsoft YaHei", 10))

    window = MainWindow()
    window.show()

    # 启动时检查过期内容
    from src.cleanup_manager import CleanupManager
    import src.data_manager as dm
    from src.utils.config import get_retention_days
    cleanup = CleanupManager(dm, window)
    cleanup.check_and_prompt(get_retention_days())

    sys.exit(app.exec_())
