"""
过期清理模块
检查过期记录，提示用户确认后清理
"""

import os

from PyQt5.QtWidgets import QMessageBox


class CleanupManager:
    """过期内容清理管理器"""

    def __init__(self, data_manager, parent_widget):
        """
        参数:
            data_manager: 数据管理模块
            parent_widget: 父窗口（用于弹出对话框）
        """
        self.data_manager = data_manager
        self.parent_widget = parent_widget

    def check_and_prompt(self, retention_days):
        """
        检查过期内容，如果有则弹窗提示用户确认清理
        返回: True 表示执行了清理，False 表示无过期内容或用户取消
        """
        expired_items = self.data_manager.get_expired_items(retention_days)

        if not expired_items:
            return False

        count = len(expired_items)

        msg = QMessageBox(self.parent_widget)
        msg.setWindowTitle("清理过期内容")
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"发现 {count} 条超过 {retention_days} 天的历史记录。")
        msg.setInformativeText("是否删除这些过期内容？\n（置顶内容不会被删除）")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.button(QMessageBox.Yes).setText("清理")
        msg.button(QMessageBox.No).setText("暂不清理")

        reply = msg.exec_()

        if reply == QMessageBox.Yes:
            # 获取过期记录的 id 和图片路径
            item_ids = [item["id"] for item in expired_items]

            # 删除关联的图片文件
            for item in expired_items:
                if item["image_path"] and os.path.exists(item["image_path"]):
                    try:
                        os.remove(item["image_path"])
                    except OSError:
                        pass  # 文件删除失败不影响数据库清理

            # 从数据库删除
            self.data_manager.delete_items_by_ids(item_ids)
            return True

        return False
