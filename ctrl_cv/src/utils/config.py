"""
配置管理模块
管理用户设置：保留天数
"""

import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "config.json")

DEFAULT_CONFIG = {
    "retention_days": 3,  # 保留天数：1 / 3 / 5
}


def load_config():
    """加载配置，如果配置文件不存在则创建默认配置"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 合并默认值，确保所有键都存在
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置到文件"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_retention_days():
    """获取当前保留天数设置"""
    config = load_config()
    return config.get("retention_days", 3)


def set_retention_days(days):
    """设置保留天数（只允许 1/3/5）"""
    if days not in (1, 3, 5):
        raise ValueError(f"保留天数只支持 1/3/5，收到: {days}")
    config = load_config()
    config["retention_days"] = days
    save_config(config)
