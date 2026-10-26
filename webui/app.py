"""光域造景 · 汉化彩色 Gradio 多页界面（Gradio 3.x 兼容）。"""
from __future__ import annotations

import base64
import json
import traceback
from pathlib import Path

import gradio as gr

from . import engine, history
from .catalog import (
    MODEL_LABELS,
    GEN_PATH_LABELS,
    RENDER_PATH_LABELS,
    catalog_table_rows,
    scene_choices,
)
from .engine import engine_status
from .paths import ROOT
from .stats import cards_html, system_detail_html
from .styles import CSS

BRAND_NAME = "光域造景"
BRAND_TAGLINE = "图像驱动的三维场景生成工作室 · 一图成景，空间可游"


def _logo_data_uri() -> str:
    logo = ROOT / "assets" / "logo-guangyu-zaojing.jpg"
    if not logo.exists():
        return ""
    b64 = base64.b64encode(logo.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _hero_html() -> str:
    logo = _logo_data_uri()
    logo_img = (
        f'<img class="hzq-logo" src="{logo}" alt="{BRAND_NAME}" />' if logo else ""
    )
    return f"""
<div id="hzq-hero">
  <div class="hzq-hero-row">
    {logo_img}
    <div class="hzq-hero-text">
      <div class="hzq-brand">{BRAND_NAME}</div>
      <p class="hzq-tagline">{BRAND_TAGLINE}</p>
      <div class="hzq-chips">
        <span class="hzq-chip"><i></i>图像驱动</span>
        <span class="hzq-chip"><i></i>一键 / 分步生成</span>
        <span class="hzq-chip"><i></i>任务可追溯</span>
      </div>
    </div>
  </div>
</div>
"""


def _section(title: str, subtitle: str) -> str:
    return f"""
    <div class="hzq-section">
      <h3>{title}</h3>
      <p>{subtitle}</p>
    </div>
    """


def _engine_html() -> str:
    return f"""
    <div class="hzq-section">
      <h3>引擎状态</h3>
      <p>{engine_status()}</p>
    </div>
    """


def _md_table(headers, rows) -> str:
    if not rows:
        return "_暂无数据_"
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return f"{head}\n{sep}\n{body}"


def _catalog_md() -> str:
    return _md_table(
        ["名称", "分类", "模型", "生成轨迹", "渲染轨迹", "更新日期", "文件"],
        catalog_table_rows(),
    )


def _history_md() -> str:
    return _md_table(
        ["编号", "标题", "状态", "模式", "模型", "创建时间", "更新时间"],
        history.table_rows(),
    )


def _ply_note(viewer_ok: bool, download_path) -> str:
    if not download_path:
        return ""
    from pathlib import Path as _P

    name = _P(download_path).name
    mb = _P(download_path).stat().st_size / (1024 * 1024)
    if viewer_ok:
        return (
            f'<div style="padding:8px 12px;color:#166534;background:#f0fdf4;'
            f'border-radius:10px;font-size:13px;">'
            f'上方为可拖拽点云预览；完整高斯 <b>{name}</b>（{mb:.0f} MB）可下载到本地用 SuperSplat / MeshLab 打开。</div>'
        )
    return (
        f'<div style="padding:8px 12px;color:#9a3412;background:#fff7ed;'
        f'border-radius:10px;font-size:13px;">点云预览失败，请下载 <b>{name}</b>。</div>'
    )


def _ply_panel(ply_src: str):
    """返回 (html预览, 下载文件, 说明)。"""
    from .ply_preview import ply_for_viewer, viewer_html

    preview, download = ply_for_viewer(ply_src or "")
    html = viewer_html(preview, "高斯点云预览")
    note = _ply_note(bool(preview), download)
    return html, download, note


def _safe(fn, n_outputs: int = 1):
    """捕获异常并返回可读结果，避免 raise 导致前端 Connection errored out。"""

    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            msg = f"操作失败：{e}"
            if n_outputs <= 1:
                return msg
            outs = [None] * (n_outputs - 1) + [msg]
            return tuple(outs)

    return wrapper


def build_demo() -> gr.Blocks:
    history.ensure_official_demos()
    example_labels = ["不使用预载"] + scene_choices()
    gen_choices = list(GEN_PATH_LABELS.keys())
    render_choices = list(RENDER_PATH_LABELS.keys())
    model_choices = list(MODEL_LABELS.keys())

    with gr.Blocks(css=CSS, title=BRAND_NAME, theme=gr.themes.Soft()) as demo:
        gr.HTML(_hero_html())

        with gr.Tabs():
            with gr.TabItem("工作台"):
                gr.HTML(
                    _section(
                        "今日工作台",
                        "汇总任务、示例与主机状态。适合作为每天打开系统的第一眼。",
                    )
                )
                home_cards = gr.HTML(cards_html())
                refresh_btn = gr.Button("刷新系统数据", elem_id="btn-refresh-home")
                home_detail = gr.HTML(system_detail_html())
                home_engine = gr.HTML(_engine_html())

                def refresh_home():
                    return cards_html(), system_detail_html(), _engine_html()

                refresh_btn.click(
                    _safe(refresh_home, 3),
                    outputs=[home_cards, home_detail, home_engine],
                )

            with gr.TabItem("场景生成"):
                gr.HTML(
                    _section(
                        "场景生成工作室",
                        "上传参考图、填写提示词，一键出结果，或按步骤烘焙高斯与视频。",
                    )
                )
                with gr.Row():
                    with gr.Column(scale=1, elem_classes=["panel-card"]):
                        input_image = gr.Image(label="输入图像", type="filepath")
                        example_name = gr.Dropdown(
                            label="预载示例（可选）",
                            choices=example_labels,
                            value="不使用预载",
                        )
                        load_ex_btn = gr.Button("载入选中示例到表单")
                        model_name = gr.Radio(
                            label="扩散模型",
                            choices=model_choices,
                            value=model_choices[0],
                        )
                        prompt = gr.Textbox(
                            label="正向提示词",
                            value="温馨明亮的客厅，午后阳光，软装细节丰富",
                            lines=3,
                        )
                        n_prompt = gr.Textbox(
                            label="负向提示词",
                            value="相框, 边框, 简单色块, 不一致, 人物, 人脸, 低质量, 模糊",
                            lines=2,
                        )
                        gen_camerapath = gr.Radio(
                            label="生成相机轨迹（步骤1）",
                            choices=gen_choices,
                            value=gen_choices[0],
                        )
                        with gr.Row():
                            seed = gr.Number(label="随机种子", value=42, precision=0)
                            diff_steps = gr.Slider(
                                label="重绘步数",
                                minimum=1,
                                maximum=50,
                                step=1,
                                value=30,
                            )
                        render_camerapath = gr.Radio(
                            label="渲染相机轨迹（步骤2）",
                            choices=render_choices,
                            value=render_choices[1],
                        )

                    with gr.Column(scale=1, elem_classes=["panel-card"]):
                        status_box = gr.Textbox(label="运行状态", lines=3)
                        run_button = gr.Button("一键生成", elem_id="run-button")
                        with gr.Row():
                            gaussian_button = gr.Button("步骤1 · 生成高斯", elem_id="btn-create")
                            render_button = gr.Button("步骤2 · 渲染视频", elem_id="btn-render")
                        result_preview = gr.Image(label="预览图", type="filepath")
                        result_video = gr.HTML(label="彩色预览动画", value=engine.media_to_html(None, "彩色预览动画"))
                        result_depth = gr.HTML(label="深度预览动画", value=engine.media_to_html(None, "深度预览动画"))
                        result_ply_file = gr.File(label="高斯点云 PLY")

                load_ex_btn.click(
                    _safe(engine.load_example_assets, 9),
                    inputs=[example_name],
                    outputs=[
                        input_image,
                        prompt,
                        n_prompt,
                        gen_camerapath,
                        seed,
                        diff_steps,
                        render_camerapath,
                        model_name,
                        status_box,
                    ],
                )

                def on_run(img, p, np_, g, sd, st, r, m, ex):
                    ply, preview, video, depth, msg = engine.run_pipeline(
                        img, p, np_, g, int(sd or 1), int(st or 30), r, m, ex
                    )
                    # 真实引擎可能把视频放在 preview 位
                    if isinstance(preview, str) and preview.lower().endswith((".mp4", ".webm", ".gif")):
                        if not video:
                            video = preview
                        preview = None
                    color_html = engine.media_to_html(video, "彩色预览动画")
                    depth_html = engine.media_to_html(depth, "深度预览动画")
                    return ply, preview, color_html, depth_html, msg

                run_button.click(
                    _safe(on_run, 5),
                    inputs=[
                        input_image, prompt, n_prompt, gen_camerapath, seed,
                        diff_steps, render_camerapath, model_name, example_name,
                    ],
                    outputs=[
                        result_ply_file, result_preview, result_video,
                        result_depth, status_box,
                    ],
                )

                def on_create(img, p, np_, g, sd, st, m, ex):
                    ply, preview, msg = engine.create_only(
                        img, p, np_, g, int(sd or 1), int(st or 30), m, ex
                    )
                    return ply, preview, msg

                gaussian_button.click(
                    _safe(on_create, 3),
                    inputs=[
                        input_image, prompt, n_prompt, gen_camerapath,
                        seed, diff_steps, model_name, example_name,
                    ],
                    outputs=[result_ply_file, result_preview, status_box],
                )

                def on_render(r, ex, img):
                    preview, video, depth, msg = engine.render_only(r, ex, img)
                    return (
                        preview,
                        engine.media_to_html(video, "彩色预览动画"),
                        engine.media_to_html(depth, "深度预览动画"),
                        msg,
                    )

                render_button.click(
                    _safe(on_render, 4),
                    inputs=[render_camerapath, example_name, input_image],
                    outputs=[
                        result_preview, result_video, result_depth, status_box,
                    ],
                )

            with gr.TabItem("示例图库"):
                gr.HTML(
                    _section(
                        "精选场景图库",
                        "预览会同时展示参考图、彩色/深度动画，以及对应的高斯点云 PLY（有官方资产时）。",
                    )
                )
                gallery_md = gr.Markdown(_catalog_md())
                with gr.Row():
                    pick = gr.Dropdown(label="选择示例", choices=scene_choices())
                    pick_btn = gr.Button("预览示例", elem_id="btn-preview-example")
                pick_img = gr.Image(label="示例预览（参考图）", type="filepath")
                with gr.Row():
                    pick_rgb = gr.Video(label="彩色预览动画")
                    pick_depth = gr.Video(label="深度预览动画")
                with gr.Row():
                    pick_ply_html = gr.HTML(label="高斯点云预览")
                    pick_ply_file = gr.File(label="下载完整高斯 PLY")
                pick_ply_note = gr.HTML()
                pick_prompt = gr.Textbox(label="提示词", lines=3)
                pick_msg = gr.Textbox(label="状态", lines=2)

                def preview_scene(choice):
                    try:
                        img, p, np_, g, sd, st, r, m, msg = engine.load_example_assets(choice)
                        demo = history.media_for_scene(choice or "")
                        rgb_v, _ = history.split_animation(demo.get("rgb") or "")
                        dep_v, _ = history.split_animation(demo.get("depth") or "")
                        if not rgb_v and demo.get("rgb"):
                            rgb_v = demo["rgb"]
                        if not dep_v and demo.get("depth"):
                            dep_v = demo["depth"]
                        ply_html, ply_dl, ply_note = _ply_panel(demo.get("ply") or "")
                        if demo.get("rgb") or demo.get("ply"):
                            extra = " · 已挂载三维演示资产"
                        else:
                            extra = " · 该示例暂无三维演示资产"
                        return (
                            img,
                            rgb_v,
                            dep_v,
                            ply_html,
                            ply_dl,
                            ply_note,
                            p or "",
                            (msg or "") + extra,
                        )
                    except Exception as e:
                        return None, None, None, "<div>预览失败</div>", None, "", "", f"预览失败：{e}"

                pick_btn.click(
                    preview_scene,
                    inputs=[pick],
                    outputs=[
                        pick_img,
                        pick_rgb,
                        pick_depth,
                        pick_ply_html,
                        pick_ply_file,
                        pick_ply_note,
                        pick_prompt,
                        pick_msg,
                    ],
                )
                gr.Button("刷新图库表").click(_safe(_catalog_md, 1), outputs=[gallery_md])

            with gr.TabItem("任务历史"):
                gr.HTML(
                    _section(
                        "任务历史",
                        "查看任务会同时预览：彩色预览动画、深度预览动画、高斯点云 PLY。官方演示编号 demo-*。",
                    )
                )
                hist_md = gr.Markdown(_history_md())
                with gr.Row():
                    hist_id = gr.Textbox(
                        label="任务编号",
                        placeholder="例如 demo-animelake / demo-doge / task-xxxxxxxx",
                        value="demo-animelake",
                    )
                    hist_view = gr.Button("查看并演示", elem_id="btn-hist-view")
                    hist_refresh = gr.Button("刷新历史", elem_id="btn-hist-refresh")
                hist_detail = gr.Textbox(label="任务详情", lines=6)
                with gr.Row():
                    hist_preview = gr.Image(label="场景参考图", type="filepath")
                    hist_rgb = gr.Video(label="彩色预览动画")
                    hist_depth = gr.Video(label="深度预览动画")
                with gr.Row():
                    hist_ply_html = gr.HTML(label="高斯点云预览")
                    hist_ply = gr.File(label="下载完整高斯 PLY")
                hist_ply_note = gr.HTML()

                def refresh_history():
                    return _history_md()

                hist_refresh.click(_safe(refresh_history, 1), outputs=[hist_md])

                def view_task(tid):
                    empty = ("请输入任务编号，例如 demo-animelake", None, None, None, "<div></div>", None, "")
                    try:
                        key = (tid or "").strip()
                        if not key:
                            return empty
                        media = history.task_media(key)
                        if media.get("detail", "").startswith("未找到"):
                            return (media["detail"], None, None, None, "<div></div>", None, "")
                        rgb_v, _ = history.split_animation(media.get("rgb") or "")
                        dep_v, _ = history.split_animation(media.get("depth") or "")
                        if not rgb_v and media.get("rgb"):
                            rgb_v = media["rgb"]
                        if not dep_v and media.get("depth"):
                            dep_v = media["depth"]
                        ply_html, ply_dl, ply_note = _ply_panel(media.get("ply") or "")
                        return (
                            media["detail"],
                            media["preview"] or None,
                            rgb_v,
                            dep_v,
                            ply_html,
                            ply_dl,
                            ply_note,
                        )
                    except Exception as e:
                        return (f"操作失败：{e}", None, None, None, f"<div>{e}</div>", None, "")

                hist_view.click(
                    view_task,
                    inputs=[hist_id],
                    outputs=[
                        hist_detail,
                        hist_preview,
                        hist_rgb,
                        hist_depth,
                        hist_ply_html,
                        hist_ply,
                        hist_ply_note,
                    ],
                )

            with gr.TabItem("系统状态"):
                sys_md = gr.HTML(system_detail_html())
                sys_engine = gr.HTML(_engine_html())
                sys_refresh = gr.Button("刷新", elem_id="btn-refresh-sys")
                gr.HTML(
                    """
                    <div class="hzq-section">
                      <h3>使用指南</h3>
                      <p>1. 工作台看数据 · 2. 场景生成出结果 · 3. 图库取灵感 · 4. 历史可回看 · 5. 无 GPU 自动演示模式。</p>
                    </div>
                    """
                )

                def refresh_sys():
                    return system_detail_html(), _engine_html()

                sys_refresh.click(_safe(refresh_sys, 2), outputs=[sys_md, sys_engine])

    return demo
