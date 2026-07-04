# 数据库设计

## 数据库信息
- **类型**：SQLite 3
- **文件位置**：`data/clipboard.db`
- **编码**：UTF-8

## 表：clipboard_items

### 建表 SQL

```sql
CREATE TABLE IF NOT EXISTS clipboard_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT    NOT NULL,     -- 'text' 或 'image'
    text_content TEXT,                 -- 文字内容（图片时为 NULL）
    image_path   TEXT,                 -- 图片文件路径（文字时为 NULL）
    created_at   TEXT    NOT NULL,     -- ISO 格式: 2026-07-03T14:30:00
    is_pinned    INTEGER DEFAULT 0,    -- 0=普通, 1=置顶
    is_deleted   INTEGER DEFAULT 0     -- 0=正常, 1=已删除
);
```

### 索引

```sql
CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_is_pinned ON clipboard_items(is_pinned);
CREATE INDEX IF NOT EXISTS idx_content_type ON clipboard_items(content_type);
```

## CRUD 操作

### 插入
```sql
INSERT INTO clipboard_items (content_type, text_content, image_path, created_at)
VALUES (?, ?, ?, ?);
```

### 查询列表（置顶优先、时间倒序）
```sql
SELECT id, content_type, text_content, image_path, created_at, is_pinned
FROM clipboard_items
WHERE is_deleted = 0
ORDER BY is_pinned DESC, created_at DESC;
```

### 搜索
```sql
SELECT id, content_type, text_content, image_path, created_at, is_pinned
FROM clipboard_items
WHERE is_deleted = 0
  AND text_content LIKE ?   -- '%关键词%'
  AND created_at >= ?       -- 日期筛选起始时间
ORDER BY is_pinned DESC, created_at DESC;
```

### 置顶/取消置顶
```sql
UPDATE clipboard_items SET is_pinned = ? WHERE id = ?;
```

### 软删除
```sql
UPDATE clipboard_items SET is_deleted = 1 WHERE id = ?;
```

### 查询过期记录（用于清理提示）
```sql
SELECT id, image_path
FROM clipboard_items
WHERE is_deleted = 0
  AND is_pinned = 0
  AND created_at < ?;  -- 当前时间 - 保留天数
```

### 物理删除过期记录（用户确认后）
```sql
DELETE FROM clipboard_items WHERE id IN (...);
```

## 图片文件命名规则
- 格式：`{id}_{timestamp}.jpg`
- 示例：`42_20260703_143000.jpg`
- 存储路径：`data/images/`

## 数据迁移
- 数据库版本通过 `PRAGMA user_version` 管理
- 初始版本：1
- 后续如有表结构变更，在 data_manager 中实现迁移逻辑
