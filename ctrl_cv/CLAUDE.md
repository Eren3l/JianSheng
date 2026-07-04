# CLAUDE.md — 历史粘贴板项目

## 项目简介
为用户（编程小白）开发一款 Windows 桌面历史粘贴板软件。软件打开后自动记录复制的内容（文字+图片），支持浏览、搜索、置顶、删除和过期清理。

- **用户技术水平**：不懂代码，不要使用编程术语
- **沟通语言**：中文
- **工作目录**：`e:/VC/ctrl_cv/`

## 规范文档索引

| 文档 | 路径 | 内容 |
|------|------|------|
| 需求规格 | `docs/requirements.md` | 功能需求、用户场景、边界定义 |
| 技术架构 | `docs/architecture.md` | 分层架构、数据流、设计决策 |
| UI 设计 | `docs/ui-design.md` | 布局、配色、组件规格、交互规范 |
| 数据库设计 | `docs/database.md` | 表结构、SQL、索引 |
| 开发计划 | `docs/development-plan.md` | 分阶段执行步骤和验证方式 |

## 开发日志
- 目录：`devlogs/`
- 命名：`YYYY-MM-DD.md`
- 每次开发完成后更新，记录：完成事项、待办事项、遇到的问题

## 工作约定
1. **小步迭代**：每次只做一个阶段中的一项任务
2. **先验证再推进**：每完成一个功能，运行 `python main.py` 验证
3. **中文沟通**：向用户汇报进度使用中文
4. **不跳过验证**：每阶段最后一步一定是运行验证

## 技术要点
- **语言**：Python 3.x
- **GUI**：PyQt5
- **数据库**：SQLite（`data/clipboard.db`）
- **图片处理**：Pillow
- **启动方式**：`python main.py`
- **依赖安装**：`pip install -r requirements.txt`

## 项目结构
```
e:\VC\ctrl_cv\
├── main.py
├── CLAUDE.md              ← 本文件
├── requirements.txt
├── docs/                  ← 规范文档
├── devlogs/               ← 开发日志
├── src/                   ← 源码
│   ├── clipboard_monitor.py
│   ├── data_manager.py
│   ├── cleanup_manager.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── clipboard_list.py
│   │   ├── detail_panel.py
│   │   ├── search_bar.py
│   │   └── settings_dialog.py
│   └── utils/
│       ├── image_compress.py
│       └── config.py
└── data/                  ← 运行时数据（自动生成）
    ├── clipboard.db
    └── images/
```
