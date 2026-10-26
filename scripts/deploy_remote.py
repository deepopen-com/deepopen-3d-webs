"""将项目同步到远程服务器并用 Docker 部署（密码仅运行时传入，不入库）。"""
from __future__ import annotations

import os
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = os.environ.get("DEPLOY_HOST", "106.75.171.235")
USER = os.environ.get("DEPLOY_USER", "ubuntu")
PASSWORD = os.environ.get("DEPLOY_PASSWORD", "")
REMOTE_DIR = os.environ.get("DEPLOY_DIR", "/home/ubuntu/hzq-lucid-dreamer")
PORT = os.environ.get("DEPLOY_PORT", "8090")

INCLUDE = [
    "web_app.py",
    "app.py",
    "app_mini.py",
    "Dockerfile",
    "docker-compose.yml",
    "requirements-web.txt",
    "webui",
    "examples",
    "assets",
    "PROGRESS.md",
]


def make_archive() -> Path:
    tmp = Path(tempfile.mkdtemp()) / "payload.tar.gz"
    with tarfile.open(tmp, "w:gz") as tar:
        for name in INCLUDE:
            path = ROOT / name
            if path.exists():
                tar.add(path, arcname=name)
    return tmp


def main():
    if not PASSWORD:
        print("请设置环境变量 DEPLOY_PASSWORD", file=sys.stderr)
        sys.exit(1)
    try:
        import paramiko
    except ImportError:
        os.system(f"{sys.executable} -m pip install -q paramiko")
        import paramiko

    archive = make_archive()
    print(f"打包完成: {archive} ({archive.stat().st_size} bytes)")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print(f"已连接 {USER}@{HOST}")

    def run(cmd: str, check=True):
        print(f"$ {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        out = stdout.read().decode("utf-8", errors="ignore")
        err = stderr.read().decode("utf-8", errors="ignore")
        code = stdout.channel.recv_exit_status()
        if out.strip():
            print(out)
        if err.strip():
            print(err)
        if check and code != 0:
            raise RuntimeError(f"命令失败({code}): {cmd}")
        return code, out, err

    run(f"mkdir -p {REMOTE_DIR}")
    sftp = client.open_sftp()
    remote_tar = f"{REMOTE_DIR}/payload.tar.gz"
    sftp.put(str(archive), remote_tar)
    sftp.close()
    print("上传完成")

    run(f"cd {REMOTE_DIR} && tar -xzf payload.tar.gz && rm -f payload.tar.gz")
    run(f"mkdir -p {REMOTE_DIR}/data {REMOTE_DIR}/outputs {REMOTE_DIR}/results")

    # 安装 docker（若缺失）
    run("command -v docker >/dev/null 2>&1 || (curl -fsSL https://get.docker.com | sudo sh)", check=False)
    run("sudo usermod -aG docker ubuntu", check=False)
    run("sudo systemctl enable --now docker", check=False)

    # 释放 8090：停掉占用该端口的其它容器，避免本项目卡在 Created
    run(
        "sudo docker ps --format '{{.ID}} {{.Names}} {{.Ports}}' | "
        f"awk '/:{PORT}->|: {PORT}/ {{print $1}}' | "
        "while read id; do sudo docker stop \"$id\"; done",
        check=False,
    )
    run("sudo docker rm -f hzq-lucid-dreamer >/dev/null 2>&1 || true", check=False)

    # docker 重建（默认用缓存；需要全量重建时设 DEPLOY_NO_CACHE=1）
    no_cache = "--no-cache" if os.environ.get("DEPLOY_NO_CACHE", "").strip() in ("1", "true", "yes") else ""
    run(
        f"cd {REMOTE_DIR} && "
        f"(sudo docker compose version >/dev/null 2>&1 && "
        f"sudo docker compose build {no_cache} && sudo docker compose up -d --force-recreate) || "
        f"(sudo docker-compose version >/dev/null 2>&1 && "
        f"sudo docker-compose build {no_cache} && sudo docker-compose up -d --force-recreate) || "
        f"(sudo docker build {no_cache} -t hzq-lucid-dreamer . && "
        f"sudo docker rm -f hzq-lucid-dreamer >/dev/null 2>&1; "
        f"sudo docker run -d --name hzq-lucid-dreamer -p {PORT}:8090 "
        f"-e LD_DEMO_MODE=1 -v {REMOTE_DIR}/data:/app/data "
        f"-v {REMOTE_DIR}/outputs:/app/outputs -v {REMOTE_DIR}/results:/app/results "
        f"-v {REMOTE_DIR}/examples:/app/examples --restart unless-stopped hzq-lucid-dreamer)"
    )

    run(f"sudo docker ps --filter name=hzq-lucid-dreamer")
    run(f"curl -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1:{PORT}/ || true", check=False)
    client.close()
    print(f"\n部署完成，请访问: http://{HOST}:{PORT}")


if __name__ == "__main__":
    main()
