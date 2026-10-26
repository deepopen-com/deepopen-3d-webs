# -*- coding: utf-8 -*-
"""安装 simple-knn 与高斯光栅化 CUDA 扩展。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd, cwd):
    print("$", " ".join(cmd), f"(cwd={cwd})")
    r = subprocess.run(cmd, cwd=str(cwd))
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def main():
    print("安装光域造景 CUDA 扩展…")
    print("需要: VS C++ Build Tools + 与 PyTorch 匹配的 CUDA Toolkit")

    glm = ROOT / "submodules" / "depth-diff-gaussian-rasterization-min" / "third_party" / "glm"
    if not glm.exists():
        glm.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", "https://github.com/g-truc/glm.git", str(glm)], ROOT)

    run([sys.executable, "setup.py", "install"], ROOT / "submodules" / "simple-knn")
    run(
        [sys.executable, "setup.py", "install"],
        ROOT / "submodules" / "depth-diff-gaussian-rasterization-min",
    )

    import simple_knn  # noqa: F401
    import depth_diff_gaussian_rasterization_min  # noqa: F401

    print("OK: 扩展导入成功")
    print("启动: python scripts/start_local.py --force-cuda")


if __name__ == "__main__":
    main()
