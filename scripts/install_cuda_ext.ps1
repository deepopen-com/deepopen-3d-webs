# 安装高斯光栅化 / simple-knn CUDA 扩展（Windows 需 VS Build Tools + CUDA Toolkit）
# 用法：在项目根目录执行
#   .\scripts\install_cuda_ext.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "安装光域造景 CUDA 扩展…" -ForegroundColor Cyan
Write-Host "需要：Visual Studio C++ Build Tools、与 PyTorch 匹配的 CUDA Toolkit" -ForegroundColor DarkYellow

# 可选：补齐第三方依赖
$glm = Join-Path $Root "submodules\depth-diff-gaussian-rasterization-min\third_party\glm"
if (-not (Test-Path $glm)) {
    Write-Host "克隆 glm…" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path (Split-Path $glm) | Out-Null
    git clone --depth 1 https://github.com/g-truc/glm.git $glm
}

Write-Host "安装 simple-knn…" -ForegroundColor Cyan
Push-Location (Join-Path $Root "submodules\simple-knn")
python setup.py install
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "simple-knn 安装失败" }
Pop-Location

Write-Host "安装 depth-diff-gaussian-rasterization-min…" -ForegroundColor Cyan
Push-Location (Join-Path $Root "submodules\depth-diff-gaussian-rasterization-min")
python setup.py install
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "高斯光栅化扩展安装失败" }
Pop-Location

Write-Host "校验导入…" -ForegroundColor Cyan
python -c "import simple_knn; import depth_diff_gaussian_rasterization_min; print('OK', simple_knn, depth_diff_gaussian_rasterization_min)"

Write-Host "完成。可用 .\scripts\start_local_cuda.ps1 -ForceCuda 启动。" -ForegroundColor Green
