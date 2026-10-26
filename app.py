"""兼容入口：转发到汉化 WebUI（完整引擎需 GPU，默认可由 LD_DEMO_MODE 控制）。"""
from web_app import main

if __name__ == "__main__":
    main()
