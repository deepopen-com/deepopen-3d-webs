"""任务历史：JSON 持久化，保证生成→记录→查看闭环。"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .paths import EXAMPLES_DIR, HISTORY_FILE, ROOT, SEED_FILE, ensure_dirs

# 官方 LucidDreamer 三维演示资产 → 可演示历史任务
# 相对路径，跨机器可解析（examples/ 已下载 PLY + MP4）
OFFICIAL_DEMOS: List[Dict[str, Any]] = [
    {
        "id": "demo-animelake",
        "title": "动漫湖畔小屋",
        "prompt": "动漫风格, 高清, 湖上小船, 湖边树木与岩石, 小屋与码头",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "标准模型 SD1.5",
        "created_at": "2026-10-12 09:15:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/Image015_animelakehouse.jpg",
        "rgb_video": "examples/animelake_llff.mp4",
        "depth_video": "examples/depth_animelake_llff.mp4",
        "ply_file": "examples/animelake.ply",
    },
    {
        "id": "demo-fantasy",
        "title": "奇幻浮空城",
        "prompt": "色彩绚丽的浮空社区城市, 云雾之上, 奇幻植物与森林, 漂浮岛屿与光球",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "标准模型 SD1.5",
        "created_at": "2026-10-11 14:20:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/Image003_fantasy.jpg",
        "rgb_video": "examples/fantasy_llff.mp4",
        "depth_video": "examples/depth_fantasy_llff.mp4",
        "ply_file": "examples/fantasy.ply",
    },
    {
        "id": "demo-kitchen",
        "title": "现代温馨厨房",
        "prompt": "高清摄影厨房, 木地板, 面向花园的小窗, 包豪斯家具, 温馨氛围",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "标准模型 SD1.5",
        "created_at": "2026-10-10 11:05:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/image020.png",
        "rgb_video": "examples/kitchen_llff.mp4",
        "depth_video": "examples/depth_kitchen_llff.mp4",
        "ply_file": "examples/kitchen.ply",
    },
    {
        "id": "demo-ruin",
        "title": "荒漠末日废墟",
        "prompt": "沙漠中的末日后城市废墟, 沙尘与残垣断壁, 电影感光影",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "炽热驱动 V11m",
        "created_at": "2026-10-09 16:30:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/ruin.png",
        "rgb_video": "examples/ruin_llff.mp4",
        "depth_video": "examples/depth_ruin_llff.mp4",
        "ply_file": "examples/ruin.ply",
    },
    {
        "id": "demo-christmas",
        "title": "圣诞客厅",
        "prompt": "圣诞节温馨客厅, 圣诞树与彩灯, 壁炉暖光, 节日氛围",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "写实视觉 V5.1",
        "created_at": "2026-10-08 20:00:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/christmas.png",
        "rgb_video": "examples/christmas_llff.mp4",
        "depth_video": "examples/depth_christmas_llff.mp4",
        "ply_file": "examples/christmas.ply",
    },
    {
        "id": "demo-elf",
        "title": "精灵深林",
        "prompt": "宁静幽深的精灵森林, 雾气与光斑, 苔藓与古树",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "卡通皮克斯 V5",
        "created_at": "2026-10-07 10:12:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/elf.png",
        "rgb_video": "examples/elf_llff.mp4",
        "depth_video": "examples/depth_elf_back_and_forth.mp4",
        "ply_file": "examples/elf.ply",
    },
    {
        "id": "demo-doge",
        "title": "狗狗温馨客厅",
        "prompt": "温馨舒适的客厅, 柔和灯光, 柔软沙发与地毯",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "写实视觉 V5.1",
        "created_at": "2026-10-12 08:30:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/doge.png",
        "rgb_video": "examples/doge_llff.mp4",
        "depth_video": "examples/depth_doge_llff.mp4",
        "ply_file": "examples/doge.ply",
    },
    {
        "id": "demo-girl",
        "title": "黑色电影房间",
        "prompt": "昏暗凌乱房间, 黑色电影风格, 室内, 酒瓶, 外套, 窗户, 景深",
        "status": "已完成",
        "mode": "官方三维演示",
        "model": "炽热驱动 V11m",
        "created_at": "2026-10-11 21:10:00",
        "updated_at": "2026-10-20 12:00:00",
        "preview_image": "examples/girl.jpg",
        "rgb_video": "examples/girl_llff.mp4",
        "depth_video": "examples/depth_girl_llff.mp4",
        "ply_file": "examples/girl.ply",
    },
]

# 兼容旧种子（无三维资产时仍可作占位）
SEED_TASKS: List[Dict[str, Any]] = list(OFFICIAL_DEMOS)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def resolve_path(p: Optional[str]) -> str:
    """把相对/绝对路径解析成当前机器上存在的绝对路径。"""
    if not p:
        return ""
    raw = str(p).strip()
    if not raw:
        return ""
    path = Path(raw)
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    candidates.extend(
        [
            ROOT / raw,
            ROOT / raw.replace("\\", "/"),
            EXAMPLES_DIR / path.name,
            ROOT / "outputs" / path.name,
        ]
    )
    # Windows 绝对路径在 Linux 上无效时，退回文件名匹配
    for c in candidates:
        try:
            if c.exists() and c.is_file():
                return str(c.resolve())
        except Exception:
            continue
    return raw


def asset_ready(task: Dict[str, Any]) -> bool:
    ply = resolve_path(task.get("ply_file"))
    rgb = resolve_path(task.get("rgb_video"))
    return bool(ply and Path(ply).exists() and rgb and Path(rgb).exists())


def _load_raw() -> List[Dict[str, Any]]:
    ensure_dirs()
    if not HISTORY_FILE.exists():
        SEED_FILE.write_text(
            json.dumps(SEED_TASKS, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        HISTORY_FILE.write_text(
            json.dumps(SEED_TASKS, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return list(SEED_TASKS)
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list) or len(data) == 0:
            HISTORY_FILE.write_text(
                json.dumps(SEED_TASKS, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return list(SEED_TASKS)
        return data
    except Exception:
        HISTORY_FILE.write_text(
            json.dumps(SEED_TASKS, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return list(SEED_TASKS)


def _save(tasks: List[Dict[str, Any]]) -> None:
    ensure_dirs()
    HISTORY_FILE.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8"
    )


_DEMOS_SYNCED = False


def ensure_official_demos(force_paths: bool = True) -> int:
    """把已下载的官方 PLY/MP4 注入/更新为历史任务，返回可用演示条数。"""
    global _DEMOS_SYNCED
    tasks = _load_raw()
    by_id = {t.get("id"): i for i, t in enumerate(tasks)}
    ready = 0
    changed = False
    for demo in OFFICIAL_DEMOS:
        item = dict(demo)
        ply_ok = Path(resolve_path(item["ply_file"])).exists()
        rgb_ok = Path(resolve_path(item["rgb_video"])).exists()
        if ply_ok and rgb_ok:
            item["status"] = "已完成"
            ready += 1
        else:
            item["status"] = "待同步资产"

        tid = item["id"]
        if tid in by_id:
            idx = by_id[tid]
            cur = tasks[idx]
            for k in (
                "title",
                "prompt",
                "mode",
                "model",
                "preview_image",
                "rgb_video",
                "depth_video",
                "ply_file",
                "status",
                "updated_at",
            ):
                if force_paths and cur.get(k) != item.get(k):
                    cur[k] = item[k]
                    changed = True
        else:
            tasks.insert(0, item)
            by_id = {t.get("id"): i for i, t in enumerate(tasks)}
            changed = True

    if changed or not _DEMOS_SYNCED:
        _save(tasks)
        SEED_FILE.write_text(
            json.dumps(OFFICIAL_DEMOS, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    _DEMOS_SYNCED = True
    return ready


def list_tasks() -> List[Dict[str, Any]]:
    tasks = _load_raw()
    tasks.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return tasks


def table_rows() -> List[List[str]]:
    rows = []
    for t in list_tasks():
        mark = "🎬" if t.get("mode") == "官方三维演示" and asset_ready(t) else ""
        rows.append([
            t.get("id", ""),
            f"{mark}{t.get('title', '')}",
            t.get("status", ""),
            t.get("mode", ""),
            t.get("model", ""),
            t.get("created_at", ""),
            t.get("updated_at", ""),
        ])
    return rows


def add_task(
    title: str,
    prompt: str,
    status: str,
    mode: str,
    model: str,
    rgb_video: str = "",
    depth_video: str = "",
    ply_file: str = "",
    preview_image: str = "",
) -> Dict[str, Any]:
    tasks = _load_raw()
    now = _now()
    item = {
        "id": f"task-{uuid.uuid4().hex[:8]}",
        "title": title or "未命名任务",
        "prompt": prompt or "",
        "status": status,
        "mode": mode,
        "model": model,
        "created_at": now,
        "updated_at": now,
        "preview_image": preview_image or "",
        "rgb_video": rgb_video or "",
        "depth_video": depth_video or "",
        "ply_file": ply_file or "",
    }
    tasks.insert(0, item)
    _save(tasks)
    return item


def update_task(task_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    tasks = _load_raw()
    for t in tasks:
        if t.get("id") == task_id:
            t.update({k: v for k, v in kwargs.items() if v is not None})
            t["updated_at"] = _now()
            _save(tasks)
            return t
    return None


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    for t in list_tasks():
        if t.get("id") == task_id:
            return t
    return None


# 图库场景 id / 标题 → 官方演示任务 id
SCENE_DEMO_MAP = {
    "anime_lake": "demo-animelake",
    "动漫湖畔小屋": "demo-animelake",
    "fantasy_float": "demo-fantasy",
    "奇幻浮空城": "demo-fantasy",
    "modern_kitchen": "demo-kitchen",
    "现代温馨厨房": "demo-kitchen",
    "desert_ruin": "demo-ruin",
    "荒漠末日废墟": "demo-ruin",
    "xmas_living": "demo-christmas",
    "圣诞客厅": "demo-christmas",
    "elf_forest": "demo-elf",
    "精灵深林": "demo-elf",
    "cozy_doge": "demo-doge",
    "狗狗温馨客厅": "demo-doge",
    "noir_room": "demo-girl",
    "黑色电影房间": "demo-girl",
}


def _ok_path(p: str) -> str:
    return p if p and Path(p).exists() else ""


def task_media(task_id: str) -> Dict[str, str]:
    """解析任务媒体绝对路径，供界面预览/下载。"""
    t = get_task(task_id)
    if not t:
        return {"preview": "", "ply": "", "rgb": "", "depth": "", "detail": "未找到任务"}
    preview = _ok_path(resolve_path(t.get("preview_image")))
    ply = _ok_path(resolve_path(t.get("ply_file")))
    rgb = _ok_path(resolve_path(t.get("rgb_video")))
    depth = _ok_path(resolve_path(t.get("depth_video")))

    slim = {
        "编号": t.get("id"),
        "标题": t.get("title"),
        "状态": t.get("status"),
        "模式": t.get("mode"),
        "模型": t.get("model"),
        "提示词": (t.get("prompt") or "")[:300],
        "创建时间": t.get("created_at"),
        "更新时间": t.get("updated_at"),
        "PLY": Path(ply).name if ply else "缺失",
        "彩色预览动画": Path(rgb).name if rgb else "缺失",
        "深度预览动画": Path(depth).name if depth else "缺失",
        "可演示": "是" if ply and rgb else "否（资产未就绪）",
    }
    return {
        "preview": preview,
        "ply": ply,
        "rgb": rgb,
        "depth": depth,
        "detail": json.dumps(slim, ensure_ascii=False, indent=2),
    }


def media_for_scene(choice_or_id: str) -> Dict[str, str]:
    """按图库选项/场景名解析对应官方三维演示资产。"""
    key = (choice_or_id or "").strip()
    demo_id = SCENE_DEMO_MAP.get(key)
    if not demo_id:
        # 「标题（分类）」
        title = key.split("（")[0].split("(")[0].strip()
        demo_id = SCENE_DEMO_MAP.get(title)
    if not demo_id:
        for d in OFFICIAL_DEMOS:
            if d["title"] in key or key in d["title"]:
                demo_id = d["id"]
                break
    if not demo_id:
        return {"preview": "", "ply": "", "rgb": "", "depth": "", "detail": ""}
    return task_media(demo_id)


def split_animation(path: str):
    """mp4/webm → Video 组件；gif/图片 → HTML 内嵌。返回 (video_path, html_or_none)。"""
    if not path:
        return None, None
    p = Path(path)
    if not p.exists():
        return None, None
    suf = p.suffix.lower()
    if suf in (".mp4", ".webm", ".ogg"):
        return str(p), None
    return None, str(p)


def ply_for_viewer(path: str, max_mb: float = 80.0):
    """返回 (Model3D轻量预览, 原PLY下载)。大高斯文件会抽点云预览。"""
    if not path:
        return None, None
    from .ply_preview import ply_for_viewer as _ply_view

    return _ply_view(path)



def stats_counts() -> Dict[str, int]:
    tasks = list_tasks()
    return {
        "total": len(tasks),
        "done": sum(1 for t in tasks if t.get("status") == "已完成"),
        "running": sum(1 for t in tasks if t.get("status") == "处理中"),
        "failed": sum(1 for t in tasks if t.get("status") == "失败"),
        "demo_ready": sum(1 for t in tasks if asset_ready(t)),
    }
