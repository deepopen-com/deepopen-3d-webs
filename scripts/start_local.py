# -*- coding: utf-8 -*-
"""光域造景 · 本机启动入口。

用法:
  python scripts/start_local.py
  python scripts/start_local.py --demo
  python scripts/start_local.py --force-cuda
  python scripts/start_local.py --port 8090
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def probe():
    cuda = False
    vram_gb = 0.0
    ext_ok = False
    try:
        import torch

        cuda = bool(torch.cuda.is_available())
        if cuda:
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    except Exception as e:
        print("TORCH_ERR", e)
    try:
        import simple_knn  # noqa: F401
        import depth_diff_gaussian_rasterization_min  # noqa: F401

        ext_ok = True
    except Exception:
        ext_ok = False
    return cuda, vram_gb, ext_ok


def main():
    parser = argparse.ArgumentParser(description="光域造景本机启动")
    parser.add_argument("--demo", action="store_true", help="强制演示模式")
    parser.add_argument("--force-cuda", action="store_true", help="强制完整算法")
    parser.add_argument("--port", type=int, default=8090)
    args = parser.parse_args()

    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))

    cuda, vram, ext_ok = probe()
    print("=" * 56)
    print(" 光域造景 · 本机启动")
    print("=" * 56)
    print(f"目录: {ROOT}")
    print(f"端口: {args.port}")
    print(f"CUDA: {cuda} | VRAM: {vram:.2f} GB | 扩展: {ext_ok}")

    if args.demo:
        os.environ["LD_DEMO_MODE"] = "1"
        print("[模式] 强制演示")
    elif args.force_cuda:
        os.environ["LD_DEMO_MODE"] = "0"
        print("[模式] 强制完整算法")
        if not cuda:
            print("[警告] 未检测到 CUDA")
        if vram and vram < 10:
            print(f"[警告] 显存约 {vram:.1f}GB，完整算法通常需要 >=12GB")
        if not ext_ok:
            print("[警告] 请先运行: python scripts/install_cuda_ext.py")
    else:
        if cuda and ext_ok and vram >= 10:
            os.environ["LD_DEMO_MODE"] = "0"
            print("[模式] 自动完整算法")
        else:
            os.environ["LD_DEMO_MODE"] = "1"
            print("[模式] 自动演示（完整算法条件不足）")
            if not cuda:
                print("  - 无 CUDA")
            if not ext_ok:
                print("  - 缺少 CUDA 扩展")
            if vram and vram < 10:
                print(f"  - 显存 {vram:.1f}GB < 10GB")

    os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"
    os.environ["GRADIO_SERVER_PORT"] = str(args.port)
    os.environ["PORT"] = str(args.port)
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    print(f"\n浏览器访问: http://127.0.0.1:{args.port}\n")
    # 直接调用 web_app.main，避免再开子进程
    from web_app import main as web_main

    web_main()


if __name__ == "__main__":
    main()
