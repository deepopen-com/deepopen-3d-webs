"""把官方 3DGS PLY 抽成轻量彩色点云，供 Gradio Model3D 预览。"""
from __future__ import annotations

import math
import struct
from pathlib import Path
from typing import List, Optional, Tuple

from .paths import OUTPUTS_DIR, ensure_dirs

# 球面谐函数 0 阶系数 → 近似 RGB
_C0 = 0.28209479177387814
_PREVIEW_DIR = OUTPUTS_DIR / "ply_preview"
_DEFAULT_POINTS = 45000


def _parse_header(raw: bytes) -> Tuple[dict, int]:
    if not raw.startswith(b"ply"):
        raise ValueError("不是 PLY 文件")
    end = raw.find(b"end_header")
    if end < 0:
        raise ValueError("PLY 缺少 end_header")
    header_end = raw.find(b"\n", end) + 1
    text = raw[:header_end].decode("ascii", errors="replace")
    fmt = "ascii"
    n_vertex = 0
    props: List[Tuple[str, str]] = []  # (type, name)
    in_vertex = False
    for line in text.splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        if parts[0] == "format":
            fmt = parts[1]
        elif parts[0] == "element" and parts[1] == "vertex":
            in_vertex = True
            n_vertex = int(parts[2])
        elif parts[0] == "element":
            in_vertex = False
        elif parts[0] == "property" and in_vertex:
            if parts[1] == "list":
                continue
            props.append((parts[1], parts[2]))
    return {
        "format": fmt,
        "n_vertex": n_vertex,
        "props": props,
        "header_end": header_end,
    }, header_end


def _type_size(t: str) -> int:
    return {
        "char": 1,
        "uchar": 1,
        "int8": 1,
        "uint8": 1,
        "short": 2,
        "ushort": 2,
        "int16": 2,
        "uint16": 2,
        "int": 4,
        "uint": 4,
        "int32": 4,
        "uint32": 4,
        "float": 4,
        "float32": 4,
        "double": 8,
        "float64": 8,
    }.get(t, 4)


def _unpack_fmt(t: str) -> str:
    return {
        "char": "b",
        "uchar": "B",
        "int8": "b",
        "uint8": "B",
        "short": "h",
        "ushort": "H",
        "int16": "h",
        "uint16": "H",
        "int": "i",
        "uint": "I",
        "int32": "i",
        "uint32": "I",
        "float": "f",
        "float32": "f",
        "double": "d",
        "float64": "d",
    }.get(t, "f")


def _sh_to_rgb(f0: float, f1: float, f2: float) -> Tuple[int, int, int]:
    r = max(0.0, min(1.0, 0.5 + _C0 * f0))
    g = max(0.0, min(1.0, 0.5 + _C0 * f1))
    b = max(0.0, min(1.0, 0.5 + _C0 * f2))
    return int(r * 255), int(g * 255), int(b * 255)


def make_preview_ply(
    src: str | Path,
    max_points: int = _DEFAULT_POINTS,
    force: bool = False,
) -> Optional[str]:
    """从高斯 PLY 生成可交互预览点云；已存在则复用。"""
    src_p = Path(src)
    if not src_p.exists():
        return None

    ensure_dirs()
    _PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out = _PREVIEW_DIR / f"{src_p.stem}_preview.ply"
    if out.exists() and out.stat().st_size > 1000 and not force:
        # 源更新后重建
        if out.stat().st_mtime >= src_p.stat().st_mtime:
            return str(out)

    raw = src_p.read_bytes()
    meta, header_end = _parse_header(raw)
    props = meta["props"]
    n = int(meta["n_vertex"])
    if n <= 0 or not props:
        return None

    names = [p[1] for p in props]
    need = {"x", "y", "z"}
    if not need.issubset(set(names)):
        return None
    ix, iy, iz = names.index("x"), names.index("y"), names.index("z")
    idc = [names.index(k) if k in names else -1 for k in ("f_dc_0", "f_dc_1", "f_dc_2")]
    irgb = [names.index(k) if k in names else -1 for k in ("red", "green", "blue")]

    step = max(1, n // max_points)
    take = list(range(0, n, step))[:max_points]

    points: List[Tuple[float, float, float, int, int, int]] = []

    if "binary" in meta["format"]:
        endian = "<" if "little" in meta["format"] else ">"
        sizes = [_type_size(t) for t, _ in props]
        stride = sum(sizes)
        fmts = endian + "".join(_unpack_fmt(t) for t, _ in props)
        body = memoryview(raw)[header_end:]
        for i in take:
            off = i * stride
            if off + stride > len(body):
                break
            vals = struct.unpack_from(fmts, body, off)
            x, y, z = float(vals[ix]), float(vals[iy]), float(vals[iz])
            if all(j >= 0 for j in idc):
                r, g, b = _sh_to_rgb(float(vals[idc[0]]), float(vals[idc[1]]), float(vals[idc[2]]))
            elif all(j >= 0 for j in irgb):
                r, g, b = int(vals[irgb[0]]), int(vals[irgb[1]]), int(vals[irgb[2]])
            else:
                r = g = b = 200
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                continue
            points.append((x, y, z, r, g, b))
    else:
        # ascii：跳过表头行，按行采样
        lines = raw[header_end:].decode("ascii", errors="ignore").splitlines()
        for i in take:
            if i >= len(lines):
                break
            parts = lines[i].split()
            if len(parts) < len(props):
                continue
            try:
                x, y, z = float(parts[ix]), float(parts[iy]), float(parts[iz])
                if all(j >= 0 for j in idc):
                    r, g, b = _sh_to_rgb(float(parts[idc[0]]), float(parts[idc[1]]), float(parts[idc[2]]))
                else:
                    r = g = b = 200
                points.append((x, y, z, r, g, b))
            except Exception:
                continue

    if not points:
        return None

    # 写二进制小 PLY，Model3D 友好
    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        f"element vertex {len(points)}\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property uchar red\n"
        "property uchar green\n"
        "property uchar blue\n"
        "end_header\n"
    ).encode("ascii")
    body = bytearray()
    for x, y, z, r, g, b in points:
        body += struct.pack("<fffBBB", x, y, z, r & 255, g & 255, b & 255)
    out.write_bytes(header + body)
    return str(out)


def ply_for_viewer(src: str | Path) -> Tuple[Optional[str], Optional[str]]:
    """返回 (轻量预览PLY路径, 原文件下载路径)。"""
    src_p = Path(src) if src else None
    if not src_p or not src_p.exists():
        return None, None
    download = str(src_p)
    mb = src_p.stat().st_size / (1024 * 1024)
    if mb <= 25:
        try:
            head = src_p.read_bytes()[:800].decode("ascii", errors="replace")
            if "f_dc_0" not in head and "property float x" in head:
                return download, download
        except Exception:
            pass
    preview = make_preview_ply(src_p)
    return preview, download


def _load_xyzrgb(preview_ply: Path, max_points: int = 28000):
    """读取预览 PLY → 居中归一化后的 xyz/rgb 数组。"""
    import numpy as np

    raw = preview_ply.read_bytes()
    meta, header_end = _parse_header(raw)
    n = int(meta["n_vertex"])
    if n <= 0:
        return None, None
    if "binary" not in meta["format"]:
        return None, None
    body = memoryview(raw)[header_end:]
    # 预览文件固定 stride=15
    stride = 15
    if len(body) < n * stride:
        n = len(body) // stride
    step = max(1, n // max_points)
    idx = list(range(0, n, step))[:max_points]
    xyz = np.zeros((len(idx), 3), dtype=np.float32)
    rgb = np.zeros((len(idx), 3), dtype=np.float32)
    for i, vi in enumerate(idx):
        x, y, z, r, g, b = struct.unpack_from("<fffBBB", body, vi * stride)
        xyz[i] = (x, y, z)
        rgb[i] = (r / 255.0, g / 255.0, b / 255.0)
    center = xyz.mean(axis=0)
    xyz = xyz - center
    scale = float(np.max(np.linalg.norm(xyz, axis=1)) or 1.0)
    xyz = xyz / scale * 1.6
    return xyz, rgb


def viewer_html(preview_ply: Optional[str], title: str = "高斯点云预览") -> str:
    """Gradio Model3D 对无面点云常黑屏；用 Three.js Points 做可拖拽预览。"""
    import base64
    import html as html_lib

    if not preview_ply or not Path(preview_ply).exists():
        return (
            '<div style="height:360px;display:flex;align-items:center;justify-content:center;'
            'background:#0b1220;color:#94a3b8;border-radius:14px;">暂无点云预览</div>'
        )
    try:
        xyz, rgb = _load_xyzrgb(Path(preview_ply))
    except Exception as e:
        return (
            f'<div style="padding:16px;background:#fff7ed;border-radius:12px;color:#9a3412;">'
            f'点云解析失败：{html_lib.escape(str(e))}</div>'
        )
    if xyz is None:
        return (
            '<div style="height:360px;display:flex;align-items:center;justify-content:center;'
            'background:#0b1220;color:#94a3b8;border-radius:14px;">点云格式不支持预览</div>'
        )

    # 降采样，保证 data-URI 体积可控
    if xyz.shape[0] > 22000:
        step = xyz.shape[0] // 22000
        xyz = xyz[::step][:22000]
        rgb = rgb[::step][:22000]
    payload = base64.b64encode(xyz.tobytes() + rgb.astype("float32").tobytes()).decode("ascii")
    n = int(xyz.shape[0])
    cap = html_lib.escape(title)

    # 纯 Canvas 实现（无 CDN），可拖拽旋转 —— Gradio Model3D 对点云常黑屏
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>
html,body{{margin:0;height:100%;background:#0b1220;overflow:hidden;font-family:sans-serif;user-select:none}}
#cap{{position:absolute;z-index:2;left:10px;top:8px;color:#cbd5e1;font-size:12px;pointer-events:none}}
canvas{{display:block;width:100%;height:100%;cursor:grab}}
</style></head><body>
<div id="cap">{cap} · {n} 点 · 拖拽旋转 / 滚轮缩放</div>
<canvas id="cv"></canvas>
<script>
(function() {{
  const n = {n};
  const u8 = Uint8Array.from(atob("{payload}"), function(c) {{ return c.charCodeAt(0); }});
  const ab = u8.buffer.slice(u8.byteOffset, u8.byteOffset + u8.byteLength);
  const xyz = new Float32Array(ab, 0, n * 3);
  const rgb = new Float32Array(ab, n * 12, n * 3);
  const cv = document.getElementById("cv");
  const ctx = cv.getContext("2d");
  let yaw = 0.55, pitch = -0.55, dist = 3.2, dragging = false, lx = 0, ly = 0;

  function resize() {{
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = cv.clientWidth * dpr;
    cv.height = cv.clientHeight * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }}
  function rot(x,y,z) {{
    // pitch then yaw
    const cp = Math.cos(pitch), sp = Math.sin(pitch);
    const cy = Math.cos(yaw), sy = Math.sin(yaw);
    let y1 = y * cp - z * sp, z1 = y * sp + z * cp;
    let x2 = x * cy + z1 * sy, z2 = -x * sy + z1 * cy;
    return [x2, y1, z2];
  }}
  function draw() {{
    const w = cv.clientWidth, h = cv.clientHeight;
    ctx.fillStyle = "#0b1220";
    ctx.fillRect(0, 0, w, h);
    const f = Math.min(w, h) * 0.92;
    const pts = [];
    for (let i = 0; i < n; i++) {{
      const x = xyz[i*3], y = xyz[i*3+1], z = xyz[i*3+2];
      const r = rot(x, y, z);
      const zz = r[2] + dist;
      if (zz < 0.2) continue;
      const sx = w * 0.5 + f * r[0] / zz;
      const sy = h * 0.5 - f * r[1] / zz;
      pts.push([sx, sy, zz, rgb[i*3], rgb[i*3+1], rgb[i*3+2]]);
    }}
    pts.sort(function(a,b){{ return b[2]-a[2]; }});
    for (let i = 0; i < pts.length; i++) {{
      const p = pts[i];
      const s = Math.max(1.0, 2.6 * (2.2 / p[2]));
      ctx.fillStyle = "rgb(" + ((p[3]*255)|0) + "," + ((p[4]*255)|0) + "," + ((p[5]*255)|0) + ")";
      ctx.fillRect(p[0]-s*0.5, p[1]-s*0.5, s, s);
    }}
  }}
  cv.addEventListener("pointerdown", function(e) {{
    dragging = true; lx = e.clientX; ly = e.clientY; cv.setPointerCapture(e.pointerId); cv.style.cursor = "grabbing";
  }});
  cv.addEventListener("pointerup", function() {{ dragging = false; cv.style.cursor = "grab"; }});
  cv.addEventListener("pointermove", function(e) {{
    if (!dragging) return;
    yaw += (e.clientX - lx) * 0.008;
    pitch += (e.clientY - ly) * 0.008;
    pitch = Math.max(-1.4, Math.min(1.4, pitch));
    lx = e.clientX; ly = e.clientY; draw();
  }});
  cv.addEventListener("wheel", function(e) {{
    e.preventDefault();
    dist *= (e.deltaY > 0 ? 1.08 : 0.92);
    dist = Math.max(1.2, Math.min(8.0, dist));
    draw();
  }}, {{ passive: false }});
  window.addEventListener("resize", resize);
  resize();
}})();
</scr""" + """ipt>
</body></html>
"""
    data_uri = "data:text/html;base64," + base64.b64encode(page.encode("utf-8")).decode("ascii")
    return (
        f'<iframe src="{data_uri}" style="width:100%;height:420px;border:0;'
        f'border-radius:14px;background:#0b1220;" sandbox="allow-scripts allow-same-origin"></iframe>'
    )
