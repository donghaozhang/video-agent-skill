# Ralph Loop Stop Hook - PowerShell Wrapper
# Calls Git Bash to execute stop-hook.sh

$ErrorActionPreference = "Stop"

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Convert Windows path to Git Bash format (/c/Users/... instead of C:\Users\...)
$BashPath = $ScriptDir -replace '\\', '/'
$BashPath = $BashPath -replace '^([A-Za-z]):', '/$1'
$BashPath = $BashPath.ToLower().Substring(0,2) + $BashPath.Substring(2)

# Path to Git Bash
$GitBash = "C:\Program Files\Git\usr\bin\bash.exe"

# Read stdin and pass to bash script
$input_data = [Console]::In.ReadToEnd()

# Execute the bash script using Git Bash
$process = New-Object System.Diagnostics.Process
$process.StartInfo.FileName = $GitBash
$process.StartInfo.Arguments = "$BashPath/stop-hook.sh"
$process.StartInfo.UseShellExecute = $false
$process.StartInfo.RedirectStandardInput = $true
$process.StartInfo.RedirectStandardOutput = $true
$process.StartInfo.RedirectStandardError = $true
$process.StartInfo.CreateNoWindow = $true
$process.StartInfo.Environment["PATH"] = "C:\Program Files\Git\usr\bin;C:\Users\zdhpe\bin;" + $env:PATH

$process.Start() | Out-Null

# Write input to stdin
$process.StandardInput.Write($input_data)
$process.StandardInput.Close()

# Read output
$stdout = $process.StandardOutput.ReadToEnd()
$stderr = $process.StandardError.ReadToEnd()

$process.WaitForExit()

# Output results
if ($stdout) { Write-Output $stdout }
if ($stderr) { Write-Error $stderr }

exit $process.ExitCode
