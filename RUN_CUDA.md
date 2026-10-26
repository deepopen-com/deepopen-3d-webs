# 光域造景 · CUDA / 本机启动说明

## 两种部署

| 场景 | 方式 | 模式 |
|------|------|------|
| 云服务器无 GPU（当前 106…235） | `docker compose up -d` | 演示模式 `LD_DEMO_MODE=1` |
| 本机有 NVIDIA GPU | `start_cuda.bat` 或下方脚本 | 自动判断：够条件则完整算法，否则演示 |
| 有 GPU 的 Linux 服务器 | `docker compose -f docker-compose.cuda.yml up -d --build` | 完整算法 `LD_DEMO_MODE=0` |

## 本机 Windows（推荐你这台电脑）

本机已检测到 **GTX 1650 4GB**。完整 LucidDreamer 算法通常需要 **≥12GB 显存**，因此默认会自动走**演示模式**保证页面可用。

### 1）一键启动（演示 / 自动）

双击项目根目录：

- `start_cuda.bat` — 自动模式（显存不足则演示）
- `start_demo.bat` — 强制演示

或命令行：

```bat
cd /d e:\code\hzq-lucid-dreamer\hzq-lucid-dreamer
python scripts\start_local.py
python scripts\start_local.py --demo
python scripts\start_local.py --force-cuda
```

浏览器打开：http://127.0.0.1:8090

### 2）安装 CUDA 扩展（跑完整算法前）

需要：VS C++ Build Tools、与 PyTorch 匹配的 CUDA Toolkit。

```bat
python scripts\install_cuda_ext.py
pip install -r requirements-cuda.txt
```

模型权重首次运行会从 Hugging Face 下载（Stable Diffusion Inpainting 等），请保证网络畅通与磁盘空间。

### 3）显存建议

- **≥16GB**：可较稳跑完整一键生成  
- **12GB**：可尝试，步数调低  
- **≤8GB（含 1650 4GB）**：请用演示模式；完整算法会加载失败并降级演示  

## 服务器 CUDA Docker

宿主机需安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)。

```bash
docker compose -f docker-compose.cuda.yml up -d --build
```

无 GPU 的服务器请继续用默认：

```bash
docker compose up -d --build
```
