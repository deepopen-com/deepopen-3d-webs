# 光域造景 · 本机启动（优先 CUDA 完整算法，不够则自动演示）
# 用法：
#   .\scripts\start_local_cuda.ps1
#   .\scripts\start_local_cuda.ps1 -ForceCuda
#   .\scripts\start_local_cuda.ps1 -DemoOnly
param(
    [switch]$ForceCuda,
    [switch]$DemoOnly,
    [int]$Port = 8090
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$env:GRADIO_SERVER_NAME = "0.0.0.0"
$env:GRADIO_SERVER_PORT = "$Port"
$env:PORT = "$Port"
$env:GRADIO_ANALYTICS_ENABLED = "False"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 光域造景 · 本机启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "目录: $Root"
Write-Host "端口: $Port"

$mode = "auto"
if ($DemoOnly) { $mode = "demo" }
elseif ($ForceCuda) { $mode = "cuda" }

$probeFile = Join-Path $env:TEMP "hzq_cuda_probe.py"
@"
cuda = False
vram_gb = 0.0
ext_ok = False
try:
    import torch
    cuda = bool(torch.cuda.is_available())
    if cuda:
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
except Exception as e:
    print('TORCH_ERR', e)
try:
    import simple_knn  # noqa: F401
    import depth_diff_gaussian_rasterization_min  # noqa: F401
    ext_ok = True
except Exception:
    ext_ok = False
print('CUDA=%d' % int(cuda))
print('VRAM=%.2f' % vram_gb)
print('EXT=%d' % int(ext_ok))
"@ | Set-Content -Path $probeFile -Encoding UTF8

$probeOut = & python $probeFile 2>&1 | Out-String
Write-Host $probeOut

$hasCuda = $probeOut -match "CUDA=1"
$vram = 0.0
if ($probeOut -match "VRAM=([0-9.]+)") { $vram = [double]$Matches[1] }
$extOk = $probeOut -match "EXT=1"

if ($mode -eq "demo") {
    $env:LD_DEMO_MODE = "1"
    Write-Host '[模式] 强制演示模式' -ForegroundColor Yellow
}
elseif ($mode -eq "cuda") {
    $env:LD_DEMO_MODE = "0"
    Write-Host '[模式] 强制完整算法 (LD_DEMO_MODE=0)' -ForegroundColor Green
    if (-not $hasCuda) { Write-Host '[警告] 未检测到 CUDA' -ForegroundColor Red }
    if ($vram -gt 0 -and $vram -lt 10) {
        Write-Host ("[警告] 显存约 {0:N2}GB，完整算法通常需要 >=12GB，可能 OOM 后降级演示" -f $vram) -ForegroundColor Yellow
    }
    if (-not $extOk) {
        Write-Host '[警告] CUDA 扩展未安装，请先运行: .\scripts\install_cuda_ext.ps1' -ForegroundColor Yellow
    }
}
else {
    if ($hasCuda -and $extOk -and $vram -ge 10) {
        $env:LD_DEMO_MODE = "0"
        Write-Host '[模式] 自动选择完整算法（CUDA+扩展+显存充足）' -ForegroundColor Green
    }
    else {
        $env:LD_DEMO_MODE = "1"
        Write-Host '[模式] 自动演示模式（原因见下）' -ForegroundColor Yellow
        if (-not $hasCuda) { Write-Host '  - 无可用 CUDA' -ForegroundColor DarkYellow }
        if (-not $extOk) { Write-Host '  - 缺少 simple-knn / 高斯光栅化扩展' -ForegroundColor DarkYellow }
        if ($vram -gt 0 -and $vram -lt 10) {
            Write-Host ("  - 显存 {0:N2}GB < 10GB" -f $vram) -ForegroundColor DarkYellow
        }
        Write-Host '  提示: 安装扩展后可用 -ForceCuda 强制尝试完整算法' -ForegroundColor DarkYellow
    }
}

Write-Host ""
Write-Host ("启动中… 浏览器访问 http://127.0.0.1:{0}" -f $Port) -ForegroundColor Cyan
Write-Host ""

& python web_app.py
