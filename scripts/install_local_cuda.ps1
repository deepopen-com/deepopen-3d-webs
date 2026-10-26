# GuangYu ZaoJing - install local CUDA deps (Windows)
# Usage from repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\install_local_cuda.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "==== Install local CUDA deps ====" -ForegroundColor Cyan
Write-Host "Root: $Root"

# 1) CUDA torch (cu118; use 2.5.1 — 2.1.x 对较新 Python 已无 wheel)
Write-Host "[1/4] Installing PyTorch CUDA 11.8 ..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip uninstall -y torch torchvision torchaudio 2>$null
python -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu118

# 2) Algorithm + web deps
Write-Host "[2/4] Installing requirements-cuda.txt ..." -ForegroundColor Yellow
python -m pip install -r requirements-cuda.txt

# 3) CUDA extensions（--no-build-isolation 才能在编译环境里看到已装的 torch）
Write-Host "[3/4] Building CUDA extensions ..." -ForegroundColor Yellow
$extOk = $true
try {
    Push-Location (Join-Path $Root "submodules\simple-knn")
    python -m pip install --no-build-isolation .
    Pop-Location
} catch {
    $extOk = $false
    Write-Host "[WARN] simple-knn build failed: $_" -ForegroundColor Yellow
    if (Get-Location | Out-String) { Pop-Location -ErrorAction SilentlyContinue }
}
try {
    Push-Location (Join-Path $Root "submodules\depth-diff-gaussian-rasterization-min")
    python -m pip install --no-build-isolation .
    Pop-Location
} catch {
    $extOk = $false
    Write-Host "[WARN] gaussian rasterization build failed: $_" -ForegroundColor Yellow
    if (Get-Location | Out-String) { Pop-Location -ErrorAction SilentlyContinue }
}

# 4) Verify
Write-Host "[4/4] Verify ..." -ForegroundColor Yellow
python -c @"
import torch
print('torch', torch.__version__)
print('cuda', torch.cuda.is_available())
if torch.cuda.is_available():
    print('gpu', torch.cuda.get_device_name(0))
    print('vram_gb', round(torch.cuda.get_device_properties(0).total_memory/1024**3, 1))
try:
    import simple_knn
    print('simple_knn OK')
except Exception as e:
    print('simple_knn FAIL', e)
try:
    import depth_diff_gaussian_rasterization_min
    print('gaussian_rasterization OK')
except Exception as e:
    print('gaussian_rasterization FAIL', e)
"@

Write-Host ""
Write-Host "Done. Start with: scripts\start_local_cuda.bat" -ForegroundColor Green
if (-not $extOk) {
    Write-Host "Extensions failed: install VS C++ Build Tools, or keep demo mode." -ForegroundColor Yellow
}
