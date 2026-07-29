Stop-Process -Name "AETHER_Wallet", "aether" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
robocopy "C:\Users\Shadow\Documents\aether-wallet\dist\AETHER_Wallet" "C:\Program Files\AETHER Wallet" /E /IS /IT /R:0 /NFL /NDL
if ($?) { Start-Process "C:\Program Files\AETHER Wallet\AETHER_Wallet.exe" }
