# 一時的スリープ抑止（SetThreadExecutionState）。プロセス終了で自動解除。
$sig = @"
[DllImport("kernel32.dll", SetLastError=true)]
public static extern uint SetThreadExecutionState(uint esFlags);
"@
$P = Add-Type -MemberDefinition $sig -Name PW -Namespace Win32 -PassThru
# ES_CONTINUOUS(0x80000000)|ES_SYSTEM_REQUIRED(0x1)|ES_AWAYMODE_REQUIRED(0x40)
$KEEP = [uint32]2147483713   # 0x80000041
$CLEAR= [uint32]2147483648   # 0x80000000
$deadline = (Get-Date).AddHours(12)
try {
    while ((Get-Date) -lt $deadline) {
        [void]$P::SetThreadExecutionState($KEEP)
        Start-Sleep -Seconds 60
    }
} finally {
    [void]$P::SetThreadExecutionState($CLEAR)
}
