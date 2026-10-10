param(
    [Parameter(Mandatory = $true)][string]$InJson,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [Parameter(Mandatory = $true)][ValidateSet("a", "b")][string]$Style
)

Add-Type -AssemblyName System.Drawing
$items = Get-Content $InJson -Raw -Encoding UTF8 | ConvertFrom-Json
New-Item -ItemType Directory -Force $OutDir | Out-Null

# a: plain document screenshot. b: typewriter text on a tinted background.
if ($Style -eq "a") {
    $fontName = "Arial"; $size = 22
    $bg = [System.Drawing.Color]::White; $fg = [System.Drawing.Color]::Black
} else {
    $fontName = "Courier New"; $size = 20
    $bg = [System.Drawing.Color]::FromArgb(245, 240, 225); $fg = [System.Drawing.Color]::FromArgb(40, 40, 90)
}

$width = 900; $pad = 30
$font = New-Object System.Drawing.Font($fontName, $size)
$brush = New-Object System.Drawing.SolidBrush($fg)
$probe = New-Object System.Drawing.Bitmap 1, 1
$measure = [System.Drawing.Graphics]::FromImage($probe)

foreach ($it in $items) {
    $path = Join-Path $OutDir "$($it.id).png"
    if (Test-Path $path) { continue }
    $sz = $measure.MeasureString($it.text, $font, $width - 2 * $pad)
    $h = [int][Math]::Ceiling($sz.Height) + 2 * $pad
    $bmp = New-Object System.Drawing.Bitmap $width, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear($bg)
    $rect = New-Object System.Drawing.RectangleF $pad, $pad, ($width - 2 * $pad), ($h - 2 * $pad)
    $g.DrawString($it.text, $font, $brush, $rect)
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
}
