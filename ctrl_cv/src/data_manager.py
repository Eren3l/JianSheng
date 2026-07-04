"""
数据管理模块
封装 SQLite 数据库的所有操作：增删改查
"""

import sqlite3
import os
from datetime import datetime


DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "clipboard.db")


def get_connection():
    """获取数据库连接（自动创建目录和数据库）"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表（程序启动时调用）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clipboard_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT    NOT NULL,
            text_content TEXT,
            image_path   TEXT,
            created_at   TEXT    NOT NULL,
            is_pinned    INTEGER DEFAULT 0,
            is_deleted   INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_items(created_at DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_pinned ON clipboard_items(is_pinned)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON clipboard_items(content_type)")
    conn.commit()
    conn.close()


def add_item(content_type, text_content=None, image_path=None):
    """添加一条记录，返回新记录的 id"""
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    cursor.execute(
        "INSERT INTO clipboard_items (content_type, text_content, image_path, created_at) VALUES (?, ?, ?, ?)",
        (content_type, text_content, image_path, created_at)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id


def get_items(keyword=None, date_from=None):
    """查询记录列表：置顶优先、时间倒序"""
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT id, content_type, text_content, image_path, created_at, is_pinned
        FROM clipboard_items
        WHERE is_deleted = 0
    """
    params = []

    if keyword:
        sql += " AND text_content LIKE ?"
        params.append(f"%{keyword}%")

    if date_from:
        sql += " AND created_at >= ?"
        params.append(date_from)

    sql += " ORDER BY is_pinned DESC, created_at DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_item_by_id(item_id):
    """根据 id 获取单条记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, content_type, text_content, image_path, created_at, is_pinned "
        "FROM clipboard_items WHERE id = ? AND is_deleted = 0",
        (item_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def toggle_pin(item_id):
    """切换置顶状态"""
    item = get_item_by_id(item_id)
    if not item:
        return
    new_state = 0 if item["is_pinned"] else 1
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clipboard_items SET is_pinned = ? WHERE id = ?", (new_state, item_id))
    conn.commit()
    conn.close()


def soft_delete(item_id):
    """软删除一条记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clipboard_items SET is_deleted = 1 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def get_expired_items(retention_days):
    """查询过期记录（超过保留天数且非置顶）"""
    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%dT%H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, image_path FROM clipboard_items "
        "WHERE is_deleted = 0 AND is_pinned = 0 AND created_at < ?",
        (cutoff,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_items_by_ids(item_ids):
    """物理删除指定 id 的记录"""
    if not item_ids:
        return
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in item_ids)
    cursor.execute(f"DELETE FROM clipboard_items WHERE id IN ({placeholders})", item_ids)
    conn.commit()
    conn.close()


def get_total_count():
    """获取未删除记录总数"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clipboard_items WHERE is_deleted = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def update_image_path(item_id, image_path):
    """更新图片记录的文件路径"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clipboard_items SET image_path = ? WHERE id = ?", (image_path, item_id))
    conn.commit()
    conn.close()
