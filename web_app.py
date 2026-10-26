"""
光域造景 Web 入口
默认端口 8090。
- 服务器无 GPU：演示模式（Docker 默认 LD_DEMO_MODE=1）
- 本机有 CUDA：用 scripts/start_local_cuda.ps1 或 start_cuda.bat 启动
"""
import os
import sys


for key in ("NO_PROXY", "no_proxy"):
    cur = os.environ.get(key, "")
    extra = "localhost,127.0.0.1,::1,0.0.0.0"
    os.environ[key] = f"{cur},{extra}" if cur else extra

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")


def _print_banner():
    from webui.stats import cuda_available, demo_mode, collect

    s = collect()
    mode = "演示模式" if demo_mode() else "完整算力模式"
    print("=" * 56, flush=True)
    print(" 光域造景  WebUI", flush=True)
    print(f" 运行模式: {mode}", flush=True)
    print(f" CUDA: {'可用' if cuda_available() else '不可用'}", flush=True)
    print(f" 主机: {s.get('hostname')} | Python {s.get('python')}", flush=True)
    print(f" 端口: {s.get('port')}", flush=True)
    if demo_mode():
        print(" 说明: 当前为演示闭环；完整三维算法需 GPU + 扩展 + 模型权重", flush=True)
        print(" 本机启动: start_cuda.bat 或 scripts\\start_local_cuda.ps1", flush=True)
    else:
        print(" 说明: LD_DEMO_MODE=0，将尝试加载完整三维生成引擎", flush=True)
    print("=" * 56, flush=True)


def main():
    from webui.paths import ensure_dirs
    from webui.app import build_demo
    from webui import history

    ensure_dirs()
    n_demo = history.ensure_official_demos()
    history.list_tasks()
    print(f"[history] 官方三维演示就绪: {n_demo} 条", flush=True)
    try:
        _print_banner()
    except Exception as e:
        print(f"[banner] {e}", file=sys.stderr, flush=True)

    host = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
    port = int(os.environ.get("GRADIO_SERVER_PORT", os.environ.get("PORT", "8090")))
    demo = build_demo()
    demo.launch(
        server_name=host,
        server_port=port,
        share=False,
        show_error=True,
        inbrowser=False,
        prevent_thread_lock=False,
    )


if __name__ == "__main__":
    main()
