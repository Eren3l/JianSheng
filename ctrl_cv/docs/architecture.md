# 技术架构设计

## 总体架构

采用分层架构，自上而下：

```
┌─────────────────────────────────┐
│          UI 层 (PyQt5)          │
│  main_window / list / detail    │
│  search_bar / settings_dialog   │
├─────────────────────────────────┤
│        业务逻辑层               │
│  clipboard_monitor              │
│  cleanup_manager                │
├─────────────────────────────────┤
│         数据访问层               │
│  data_manager                   │
│  image_compress (工具)          │
├─────────────────────────────────┤
│         数据层                   │
│  SQLite (clipboard.db)          │
│  本地文件系统 (images/)         │
└─────────────────────────────────┘
```

## 各层职责

### UI 层
- 基于 PyQt5 构建
- 主窗口 `MainWindow` 作为容器，包含搜索栏、列表、详情面板
- 设置弹窗 `SettingsDialog` 独立对话框
- 不直接操作数据库，通过 `data_manager` 访问

### 业务逻辑层
- **clipboard_monitor**：定时轮询系统剪贴板（QTimer，500ms 间隔），检测文字/图片变化，去重后写入数据库
- **cleanup_manager**：检查过期记录，计算过期数量，弹窗确认后调用 data_manager 清理

### 数据访问层
- **data_manager**：封装所有 SQLite CRUD 操作，提供统一的增删改查接口
- **image_compress**：使用 Pillow 对图片进行等比缩放 + JPEG 压缩

### 数据层
- **SQLite**：单文件数据库 `data/clipboard.db`，表结构见 `database.md`
- **文件系统**：图片文件存储在 `data/images/` 目录

## 数据流

### 复制内容 → 写入数据库
```
用户 Ctrl+C → 剪贴板内容变化 → clipboard_monitor 检测到
→ 判断类型(文字/图片) → 是图片则压缩存到 data/images/
→ 调用 data_manager.add_item() → 写入 SQLite
→ 刷新 UI 列表
```

### 搜索筛选 → 查询数据库
```
用户输入关键词/选择日期 → 搜索栏发出信号
→ MainWindow 调用 data_manager.search_items()
→ 返回结果列表 → UI 刷新
```

### 过期清理流程
```
软件启动 → cleanup_manager 检查过期记录
→ 有过期则弹窗显示数量 → 用户确认
→ data_manager.delete_expired() → UI 刷新
```

## 关键设计决策

| 决策 | 理由 |
|------|------|
| QTimer 轮询而非钩子 | PyQt 不支持底层钩子，轮询 500ms 足够且稳定 |
| 软删除（is_deleted 标记） | 数据可恢复，避免误删 |
| 图片存文件系统而非数据库 BLOB | 数据库不膨胀，图片文件管理更灵活 |
| 置顶不过期 | 用户明确表达需求 |
| 启动即过期检查 | 逻辑简单，避免持久后台进程 |
