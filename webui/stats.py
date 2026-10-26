"""首页系统数据：真实采集主机与业务统计。"""
from __future__ import annotations

import html
import os
import platform
import shutil
from datetime import datetime
from typing import Any, Dict

from . import history
from .catalog import list_scenes
from .paths import DATA_DIR, EXAMPLES_DIR, OUTPUTS_DIR, ROOT


def _bytes_gb(n: float) -> float:
    return round(n / (1024 ** 3), 2)


def disk_info(path: str = None) -> Dict[str, Any]:
    path = path or str(ROOT)
    try:
        usage = shutil.disk_usage(path)
        return {
            "total_gb": _bytes_gb(usage.total),
            "used_gb": _bytes_gb(usage.used),
            "free_gb": _bytes_gb(usage.free),
            "percent": round(usage.used / usage.total * 100, 1) if usage.total else 0,
        }
    except Exception:
        return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}


def cuda_available() -> bool:
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return False


def demo_mode() -> bool:
    flag = os.environ.get("LD_DEMO_MODE", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return True
    if flag in ("0", "false", "no", "off"):
        return False
    return not cuda_available()


def collect() -> Dict[str, Any]:
    counts = history.stats_counts()
    disk = disk_info()
    scenes = list_scenes()
    return {
        "now": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "cuda": cuda_available(),
        "demo_mode": demo_mode(),
        "task_total": counts["total"],
        "task_done": counts["done"],
        "task_running": counts["running"],
        "task_failed": counts["failed"],
        "scene_count": len(scenes),
        "disk": disk,
        "examples_dir": str(EXAMPLES_DIR),
        "outputs_dir": str(OUTPUTS_DIR),
        "data_dir": str(DATA_DIR),
        "port": int(os.environ.get("GRADIO_SERVER_PORT", os.environ.get("PORT", "8090"))),
    }


def cards_html() -> str:
    s = collect()
    mode_label = "演示模式" if s["demo_mode"] else "完整算力"
    mode_color = "#ffb020" if s["demo_mode"] else "#0d9488"
    cuda_label = "可用" if s["cuda"] else "不可用"
    d = s["disk"]

    def card(kicker, title, value, sub, accent):
        return f"""
        <div class="hzq-card" style="--accent:{accent}">
          <div class="hzq-card-kicker">{html.escape(kicker)}</div>
          <div class="hzq-card-title">{html.escape(title)}</div>
          <div class="hzq-card-value">{html.escape(str(value))}</div>
          <div class="hzq-card-sub">{html.escape(sub)}</div>
        </div>
        """

    cards = "".join([
        card("TASKS", "任务总数", s["task_total"], f"完成 {s['task_done']} · 进行中 {s['task_running']} · 失败 {s['task_failed']}", "#ff5c3a"),
        card("LIBRARY", "示例场景", s["scene_count"], "图库一键载入生成", "#0891b2"),
        card("ENGINE", "运行模式", mode_label, f"CUDA {cuda_label}", mode_color),
        card("STORAGE", "磁盘剩余", f"{d['free_gb']} GB", f"已用 {d['percent']}% / 共 {d['total_gb']} GB", "#0d9488"),
        card("HOST", "主机节点", s["hostname"] or "-", s["os"], "#e11d6a"),
        card("SERVICE", "服务端口", s["port"], f"更新于 {s['now']}", "#ea580c"),
    ])
    return f'<div class="hzq-card-grid">{cards}</div>'


def system_detail_html() -> str:
    s = collect()
    d = s["disk"]
    items = [
        ("刷新时间", s["now"], "#ff5c3a"),
        ("主机名", s["hostname"], "#0891b2"),
        ("操作系统", s["os"], "#0d9488"),
        ("Python", s["python"], "#e11d6a"),
        ("CUDA", "可用" if s["cuda"] else "不可用", "#ea580c"),
        ("运行模式", "演示模式" if s["demo_mode"] else "完整算力模式", "#ffb020"),
        ("磁盘", f"{d['used_gb']} / {d['total_gb']} GB（剩余 {d['free_gb']} GB）", "#14b8a6"),
        ("示例目录", s["examples_dir"], "#f43f5e"),
        ("输出目录", s["outputs_dir"], "#2563eb"),
        ("数据目录", s["data_dir"], "#c2410c"),
    ]
    body = "".join(
        f"""
        <div class="hzq-sys-item">
          <div class="hzq-sys-dot" style="background:{color}"></div>
          <div><b>{html.escape(k)}</b><span>{html.escape(str(v))}</span></div>
        </div>
        """
        for k, v, color in items
    )
    return f"""
    <div class="hzq-section">
      <h3>实时系统信息</h3>
      <p>以下数据来自当前运行环境，可随时刷新。</p>
      <div class="hzq-sys-panel">{body}</div>
    </div>
    """


def system_detail_md() -> str:
    """兼容旧调用名，实际返回精美 HTML。"""
    return system_detail_html()
