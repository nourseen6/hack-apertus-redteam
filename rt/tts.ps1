param(
    [Parameter(Mandatory = $true)][string]$InJson,
    [Parameter(Mandatory = $true)][string]$OutDir,
    [Parameter(Mandatory = $true)][ValidateSet("m", "f")][string]$Voice
)

Add-Type -AssemblyName System.Speech
$items = Get-Content $InJson -Raw -Encoding UTF8 | ConvertFrom-Json
New-Item -ItemType Directory -Force $OutDir | Out-Null

# m: Microsoft David (male). f: Microsoft Zira (female). 16 kHz mono 16-bit WAV.
$name = if ($Voice -eq "m") { "Microsoft David Desktop" } else { "Microsoft Zira Desktop" }
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000,
    [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)

foreach ($it in $items) {
    $path = Join-Path $OutDir "$($it.id).wav"
    if (Test-Path $path) { continue }
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SelectVoice($name)
    $synth.SetOutputToWaveFile($path, $fmt)
    $synth.Speak($it.text)
    $synth.Dispose()
}
