"""生成引擎：优先真实 LucidDreamer，失败则演示闭环（不抛未捕获异常）。"""
from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any, Optional, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageFilter

from . import history
from .catalog import (
    GEN_PATH_LABELS,
    MODEL_LABELS,
    RENDER_PATH_LABELS,
    get_scene,
    scene_by_choice,
)
from .paths import OUTPUTS_DIR, ensure_dirs
from .stats import demo_mode


_engine = None
_engine_error = ""


def _ext_status() -> str:
    missing = []
    try:
        import simple_knn  # noqa: F401
    except Exception:
        missing.append("simple-knn")
    try:
        import depth_diff_gaussian_rasterization_min  # noqa: F401
    except Exception:
        missing.append("gaussian-rasterization")
    if missing:
        return "缺少扩展: " + ", ".join(missing) + "（本机可运行 scripts/install_cuda_ext.ps1）"
    return "CUDA 扩展已就绪"


def engine_status() -> str:
    if demo_mode():
        return (
            "演示模式：可生成预览图与演示视频；完整 3D 需 GPU + 扩展 + 模型权重。"
            f"（{_ext_status()}）本机可用 start_cuda.bat。"
        )
    if _engine is not None:
        return "完整算力模式：三维生成引擎已加载。"
    if _engine_error:
        return f"引擎未就绪（将降级演示输出）：{_engine_error}；{_ext_status()}"
    return f"完整算力模式：引擎尚未初始化。{_ext_status()}"


def _try_load_engine():
    global _engine, _engine_error
    if demo_mode():
        return None
    if _engine is not None:
        return _engine
    try:
        import torch
        if not torch.cuda.is_available():
            _engine_error = "LD_DEMO_MODE=0 但当前 PyTorch 未检测到 CUDA"
            return None
        mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        if mem_gb < 8:
            # 仍然尝试加载；显存过小通常会在推理时 OOM，由调用方降级
            pass
        from luciddreamer import LucidDreamer
        _engine = LucidDreamer(for_gradio=True, save_dir="./")
        _engine_error = ""
        return _engine
    except Exception as e:
        _engine_error = str(e)
        return None


def _to_en_gen(label: str) -> str:
    return GEN_PATH_LABELS.get(label, label if label in ("lookaround", "lookdown", "rotate360") else "lookaround")


def _to_en_render(label: str) -> str:
    return RENDER_PATH_LABELS.get(
        label, label if label in ("back_and_forth", "llff", "headbanging") else "llff"
    )


def _to_en_model(label: str) -> str:
    return MODEL_LABELS.get(label, label if "SD" in str(label) or "Vision" in str(label) else "SD1.5 (default)")


def _load_font(size: int):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            if Path(path).exists():
                return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _as_rgb_image(source) -> Optional[Image.Image]:
    if source is None:
        return None
    if isinstance(source, Image.Image):
        return source.convert("RGB")
    try:
        return Image.open(source).convert("RGB")
    except Exception:
        return None


def _compose_preview(prompt: str, title: str, source=None) -> Image.Image:
    """基于输入图制作清晰可见的演示预览（非黑块）。"""
    W, H = 960, 540
    base = _as_rgb_image(source)
    if base is not None:
        # 居中裁切铺满
        bw, bh = base.size
        scale = max(W / bw, H / bh)
        nw, nh = int(bw * scale), int(bh * scale)
        base = base.resize((nw, nh), Image.Resampling.LANCZOS)
        left, top = (nw - W) // 2, (nh - H) // 2
        canvas = base.crop((left, top, left + W, top + H))
        canvas = ImageEnhance.Color(canvas).enhance(1.25)
        canvas = ImageEnhance.Contrast(canvas).enhance(1.08)
        # 轻微模糊边缘光感
        glow = canvas.filter(ImageFilter.GaussianBlur(12))
        canvas = Image.blend(canvas, glow, 0.18)
    else:
        canvas = Image.new("RGB", (W, H), (255, 120, 70))
        draw = ImageDraw.Draw(canvas)
        for y in range(H):
            r = int(255 - y * 0.18)
            g = int(90 + y * 0.22)
            b = int(140 + y * 0.08)
            draw.line([(0, y), (W, y)], fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # 底部信息条
    od.rounded_rectangle([24, H - 150, W - 24, H - 24], radius=18, fill=(20, 24, 38, 200))
    # 顶部角标
    od.rounded_rectangle([24, 24, 260, 78], radius=14, fill=(255, 92, 58, 220))

    font_lg = _load_font(28)
    font_md = _load_font(20)
    font_sm = _load_font(16)
    od.text((44, 38), "GuangYu ZaoJing", fill=(255, 255, 255, 255), font=font_md)
    od.text((48, H - 130), f"{title}", fill=(255, 255, 255, 255), font=font_lg)
    od.text((48, H - 90), "GuangYu demo preview (no GPU fallback)", fill=(255, 220, 140, 255), font=font_sm)
    tip = (prompt or "no prompt")[:48]
    od.text((48, H - 62), f"Prompt: {tip}", fill=(210, 230, 255, 255), font=font_sm)

    composed = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    return composed


def _camera_frames(frames_src: Image.Image, frames: int = 8, size=(360, 200)):
    W, H = size
    base = frames_src.resize((W, H), Image.Resampling.BILINEAR)
    seq = []
    for i in range(frames):
        t = i / max(frames - 1, 1)
        zoom = 1.0 + 0.10 * t
        nw, nh = int(W * zoom), int(H * zoom)
        layer = base.resize((nw, nh), Image.Resampling.BILINEAR)
        ox = int((nw - W) * (0.1 + 0.8 * t))
        oy = int((nh - H) * (0.25 + 0.25 * (1 - abs(2 * t - 1))))
        seq.append(layer.crop((ox, oy, ox + W, oy + H)).convert("RGB"))
    return seq


def _to_depth_frame(frame: Image.Image) -> Image.Image:
    import numpy as np

    arr = np.asarray(frame.convert("L"), dtype=np.float32) / 255.0
    rgb = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    rgb[..., 0] = (40 + arr * 30).astype(np.uint8)
    rgb[..., 1] = (80 + arr * 120).astype(np.uint8)
    rgb[..., 2] = (140 + arr * 100).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")


def _write_demo_gif(frames_src: Image.Image, out_path: Path, *, depth: bool = False, frames: int = 8) -> str:
    """Pillow GIF：浏览器可直接播放（体积控制，避免接口超时）。"""
    seq = _camera_frames(frames_src, frames=frames)
    if depth:
        seq = [_to_depth_frame(f) for f in seq]
    seq[0].save(
        out_path,
        save_all=True,
        append_images=seq[1:],
        duration=140,
        loop=0,
        optimize=True,
    )
    return str(out_path)


def media_to_html(path: Optional[str], title: str = "") -> str:
    """本地媒体转 base64 HTML，前端必定能显示。"""
    import base64
    import html as html_lib

    if not path or not Path(path).exists():
        label = html_lib.escape(title or "媒体")
        return (
            f'<div style="padding:24px;color:#64748b;background:#fff;border-radius:14px;'
            f'border:1px dashed #e2e8f0;">暂无{label}</div>'
        )
    p = Path(path)
    raw = p.read_bytes()
    # 超大文件不内嵌；视频改走文件直链提示（历史页用 Gradio Video 播放）
    if len(raw) > 2_500_000:
        cap = html_lib.escape(title or p.name)
        return (
            f'<div style="padding:18px;border-radius:14px;background:#fff7ed;border:1px solid #fed7aa;">'
            f'<b>{cap}</b> 已生成（{len(raw)//1024} KB），文件较大未内嵌预览。'
            f'<br/>请到「任务历史」打开 demo-* 任务播放/下载。</div>'
        )
    b64 = base64.b64encode(raw).decode("ascii")
    suffix = p.suffix.lower()
    cap = html_lib.escape(title or p.name)
    if suffix == ".gif":
        mime = "image/gif"
    elif suffix in (".jpg", ".jpeg"):
        mime = "image/jpeg"
    elif suffix == ".png":
        mime = "image/png"
    elif suffix == ".webp":
        mime = "image/webp"
    elif suffix == ".mp4":
        mime = "video/mp4"
    elif suffix == ".webm":
        mime = "video/webm"
    else:
        return f'<div style="padding:16px;">不支持的文件：{cap}</div>'

    if mime.startswith("video/"):
        body = (
            f'<video controls autoplay muted loop playsinline '
            f'style="width:100%;max-height:420px;display:block;" '
            f'src="data:{mime};base64,{b64}"></video>'
        )
    else:
        body = (
            f'<img src="data:{mime};base64,{b64}" alt="{cap}" '
            f'style="width:100%;display:block;max-height:420px;object-fit:contain;"/>'
        )
    return (
        f'<div style="border-radius:16px;overflow:hidden;background:#0f172a;">'
        f"{body}"
        f'<div style="padding:8px 12px;color:#cbd5e1;font-size:12px;">{cap}</div></div>'
    )


def _write_colored_ply(image: Image.Image, ply_path: Path, step: int = 4) -> Tuple[str, int]:
    """根据图像生成带颜色的可见点云（非空 PLY），可用 MeshLab / SuperSplat 打开。"""
    import numpy as np

    img = image.convert("RGB")
    max_side = 240
    w0, h0 = img.size
    scale = min(1.0, max_side / max(w0, h0))
    if scale < 1.0:
        img = img.resize((max(1, int(w0 * scale)), max(1, int(h0 * scale))), Image.Resampling.BILINEAR)
    arr = np.asarray(img, dtype=np.uint8)
    h, w = arr.shape[:2]
    gray = arr.mean(axis=2).astype(np.float32) / 255.0
    ys, xs = np.mgrid[0:h:step, 0:w:step]
    zs_base = 1.2 - gray[ys, xs] * 0.85
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    nx = (xs - cx) / max(cx, 1.0)
    ny = (ys - cy) / max(cy, 1.0)
    bump = 0.15 * (1.0 - (nx * nx + ny * ny).clip(0, 1))
    xs_f = nx.astype(np.float32)
    ys_f = (-ny).astype(np.float32)
    zs_f = (zs_base + bump).astype(np.float32)
    cols = arr[ys, xs]

    keep = gray[ys, xs] > 0.04
    xs_f, ys_f, zs_f = xs_f[keep], ys_f[keep], zs_f[keep]
    cols = cols[keep]
    n = int(xs_f.size)
    if n < 100:
        ys2, xs2 = np.mgrid[0:h:step, 0:w:step]
        xs_f = ((xs2 - cx) / max(cx, 1.0)).astype(np.float32).ravel()
        ys_f = (-(ys2 - cy) / max(cy, 1.0)).astype(np.float32).ravel()
        zs_f = np.full(xs_f.shape, 0.8, dtype=np.float32)
        cols = arr[ys2, xs2].reshape(-1, 3)
        n = int(xs_f.size)

    header = (
        "ply\nformat ascii 1.0\n"
        f"element vertex {n}\n"
        "property float x\nproperty float y\nproperty float z\n"
        "property uchar red\nproperty uchar green\nproperty uchar blue\n"
        "end_header\n"
    )
    body = np.column_stack([xs_f, ys_f, zs_f, cols.astype(np.int32)])
    with ply_path.open("w", encoding="ascii", newline="\n") as f:
        f.write(header)
        np.savetxt(f, body, fmt="%.5f %.5f %.5f %d %d %d")
    return str(ply_path), n


def _render_pointcloud_preview(image: Image.Image, title: str = "Point Cloud") -> Image.Image:
    """把点云效果画成深色背景预览，避免「一片黑看不出」。"""
    import numpy as np

    src = image.convert("RGB").resize((320, 180), Image.Resampling.BILINEAR)
    arr = np.asarray(src, dtype=np.uint8)
    h, w = arr.shape[:2]
    canvas = np.zeros((540, 960, 3), dtype=np.uint8)
    canvas[:] = (12, 16, 28)
    canvas[::24, :, :] = (22, 28, 44)
    canvas[:, ::24, :] = (22, 28, 44)

    gray = arr.mean(axis=2) / 255.0
    step = 2
    ys, xs = np.mgrid[0:h:step, 0:w:step]
    keep = gray[ys, xs] > 0.05
    ys, xs = ys[keep], xs[keep]
    depth = 1.2 - gray[ys, xs] * 0.85
    scale = 1.15 / np.maximum(0.35, depth)
    x = (480 + (xs - w / 2) * scale * 1.6).astype(np.int32)
    y = (270 + (ys - h / 2) * scale * 1.6).astype(np.int32)
    valid = (x >= 0) & (x < 960) & (y >= 0) & (y < 540)
    x, y = x[valid], y[valid]
    cols = arr[ys[valid], xs[valid]]
    canvas[y, x] = cols
    # 加粗一点像素
    for dx, dy in ((1, 0), (0, 1), (1, 1)):
        xx = np.clip(x + dx, 0, 959)
        yy = np.clip(y + dy, 0, 539)
        canvas[yy, xx] = cols

    out = Image.fromarray(canvas, mode="RGB")
    draw = ImageDraw.Draw(out)
    font = _load_font(22)
    draw.rounded_rectangle([24, 24, 420, 78], radius=12, fill=(255, 92, 58))
    draw.text((40, 40), f"光域造景 · {title}", fill=(255, 255, 255), font=font)
    draw.text((40, 500), "GuangYu colored point cloud - open PLY in viewer", fill=(180, 200, 230), font=_load_font(16))
    return out


def _make_preview(prompt: str, title: str, source=None) -> Tuple[str, str, str, str]:
    """演示产物：彩色点云 PLY + 预览图 + 彩色 GIF + 深度 GIF。"""
    ensure_dirs()
    out = OUTPUTS_DIR / f"demo_{history.stats_counts()['total'] + 1}"
    out.mkdir(parents=True, exist_ok=True)
    img_path = out / "preview.jpg"
    color_gif = out / "preview_color.gif"
    depth_gif = out / "preview_depth.gif"
    info_path = out / "result.txt"
    ply_path = out / "scene_demo.ply"

    base = _as_rgb_image(source) or _compose_preview(prompt, title, source)
    # 页面预览：点云渲染图（深色底+彩色点），不再只给黑块感
    cloud_preview = _render_pointcloud_preview(base, title=title[:18] or "Point Cloud")
    ui_preview = _compose_preview(prompt, title, cloud_preview)
    ui_preview.save(img_path, quality=92)
    _write_demo_gif(ui_preview, color_gif, depth=False)
    _write_demo_gif(ui_preview, depth_gif, depth=True)
    _, n_pts = _write_colored_ply(base, ply_path, step=2)

    info_path.write_text(
        f"标题: {title}\n提示词: {prompt}\n点云顶点数: {n_pts}\n"
        f"说明: 演示模式已生成带颜色的 PLY 点云与预览动画。"
        f"完整三维高斯生成需要 GPU（设置 LD_DEMO_MODE=0）。\n",
        encoding="utf-8",
    )
    return str(ply_path), str(img_path), str(color_gif), str(depth_gif)


def _safe_image(rgb_cond) -> Optional[Any]:
    return _as_rgb_image(rgb_cond)


def run_pipeline(
    rgb_cond,
    prompt: str,
    n_prompt: str,
    gen_path: str,
    seed: int,
    steps: int,
    render_path: str,
    model_name: str,
    example_choice: str = "不使用预载",
    progress=None,
):
    title = "自定义生成"
    mode = "一键生成"
    scene = None
    if example_choice and example_choice not in ("不使用预载", "DON'T", "DONT"):
        scene = scene_by_choice(example_choice) or get_scene(example_choice)
        if scene:
            title = scene.title
            mode = "示例预载"
            if rgb_cond is None and scene.image:
                try:
                    rgb_cond = scene.image
                except Exception:
                    pass
            prompt = prompt or scene.prompt
            n_prompt = n_prompt or scene.negative
            model_name = model_name or scene.model

    task = history.add_task(
        title=title,
        prompt=prompt or "",
        status="处理中",
        mode=mode,
        model=model_name or "标准模型 SD1.5",
    )

    try:
        eng = _try_load_engine()
        if eng is None:
            ply, preview, video, depth = _make_preview(prompt or title, title, rgb_cond)
            history.update_task(
                task["id"],
                status="已完成",
                ply_file=ply,
                rgb_video=video,
                depth_video=depth,
            )
            return (
                ply,
                preview,
                video,
                depth,
                f"✅ 演示模式已出图/出视频：{title}（任务 {task['id']}）。完整 3D 需 GPU。",
            )

        en_model = _to_en_model(model_name)
        en_gen = _to_en_gen(gen_path)
        en_render = _to_en_render(render_path)
        ply, rgb_v, depth_v = eng.run(
            _safe_image(rgb_cond),
            prompt,
            n_prompt,
            en_gen,
            int(seed),
            int(steps),
            en_render,
            en_model,
            None,
        )
        history.update_task(
            task["id"],
            status="已完成",
            ply_file=str(ply) if ply else "",
            rgb_video=str(rgb_v) if rgb_v else "",
            depth_video=str(depth_v) if depth_v else "",
        )
        return ply, str(rgb_v) if rgb_v else None, str(depth_v) if depth_v else None, None, f"✅ 生成完成：{title}（任务 {task['id']}）"
    except Exception as e:
        history.update_task(task["id"], status="失败")
        ply, preview, video, depth = _make_preview(f"{prompt}\n错误: {e}", title, rgb_cond)
        tb = traceback.format_exc(limit=3)
        return ply, preview, video, depth, f"⚠️ 已降级演示输出：{e}\n{tb}"


def create_only(
    rgb_cond,
    prompt: str,
    n_prompt: str,
    gen_path: str,
    seed: int,
    steps: int,
    model_name: str,
    example_choice: str = "不使用预载",
):
    title = "高斯生成"
    scene = None
    if example_choice and example_choice not in ("不使用预载",):
        scene = scene_by_choice(example_choice)
        if scene:
            title = scene.title
            if rgb_cond is None and scene.image:
                rgb_cond = scene.image

    task = history.add_task(
        title=f"{title} · 步骤1",
        prompt=prompt or "",
        status="处理中",
        mode="分步生成",
        model=model_name or "标准模型 SD1.5",
    )
    try:
        eng = _try_load_engine()
        if eng is None:
            ply, preview, video, _ = _make_preview(prompt or title, title, rgb_cond)
            history.update_task(task["id"], status="已完成", ply_file=ply, rgb_video=video)
            return ply, preview, f"✅ 演示模式 · 步骤1完成，已生成预览（{task['id']}）"
        ply = eng.create(
            _safe_image(rgb_cond),
            prompt,
            n_prompt,
            _to_en_gen(gen_path),
            int(seed),
            int(steps),
            _to_en_model(model_name),
            None,
        )
        history.update_task(task["id"], status="已完成", ply_file=str(ply) if ply else "")
        return ply, None, f"✅ 步骤1完成（{task['id']}）"
    except Exception as e:
        history.update_task(task["id"], status="失败")
        ply, preview, video, _ = _make_preview(str(e), title, rgb_cond)
        return ply, preview, f"⚠️ 步骤1降级演示：{e}"


def render_only(render_path: str, example_choice: str = "不使用预载", rgb_cond=None):
    title = "视频渲染"
    scene = None
    if example_choice and example_choice not in ("不使用预载",):
        scene = scene_by_choice(example_choice)
        if scene:
            title = f"{scene.title} · 渲染"
            if rgb_cond is None and scene.image:
                rgb_cond = scene.image

    task = history.add_task(
        title=f"{title} · 步骤2",
        prompt="",
        status="处理中",
        mode="分步生成",
        model="-",
    )
    try:
        eng = _try_load_engine()
        if eng is None:
            _, preview, video, depth = _make_preview("渲染预览", title, rgb_cond)
            history.update_task(task["id"], status="已完成", rgb_video=video, depth_video=depth)
            return preview, video, depth, f"✅ 演示模式 · 步骤2完成，已生成彩色/深度视频（{task['id']}）"
        rgb_v, depth_v = eng.render_video(_to_en_render(render_path), None)
        history.update_task(
            task["id"],
            status="已完成",
            rgb_video=str(rgb_v) if rgb_v else "",
            depth_video=str(depth_v) if depth_v else "",
        )
        return rgb_v, depth_v, None, f"✅ 步骤2完成（{task['id']}）"
    except Exception as e:
        history.update_task(task["id"], status="失败")
        _, preview, video, depth = _make_preview(str(e), title, rgb_cond)
        return preview, video, depth, f"⚠️ 步骤2降级演示：{e}"


def load_example_assets(choice: str):
    """返回值全部为可序列化类型；图片用路径，避免 PIL 传输失败。"""
    try:
        scene = scene_by_choice(choice)
        if not scene:
            normalized = (choice or "").replace("(", "（").replace(")", "）").strip()
            scene = scene_by_choice(normalized)
        if not scene:
            return None, "", "", "环顾四周", 1, 30, "经典环绕", "标准模型 SD1.5", f"未找到示例：{choice}"

        img_path = None
        if scene.image and Path(scene.image).exists():
            img_path = scene.image
        elif scene.image:
            return (
                None,
                scene.prompt,
                scene.negative,
                scene.gen_path,
                scene.seed,
                scene.steps,
                scene.render_path,
                scene.model,
                f"示例图片缺失：{scene.image}",
            )

        return (
            img_path,
            scene.prompt,
            scene.negative,
            scene.gen_path,
            scene.seed,
            scene.steps,
            scene.render_path,
            scene.model,
            f"已载入示例：{scene.title}",
        )
    except Exception as e:
        return None, "", "", "环顾四周", 1, 30, "经典环绕", "标准模型 SD1.5", f"载入失败：{e}"
