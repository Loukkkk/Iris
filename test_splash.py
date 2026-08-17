import subprocess

ps_script = """
Add-Type -AssemblyName System.Windows.Forms
$f = New-Object System.Windows.Forms.Form
$f.Text = 'Test Splash'
$f.ShowDialog()
"""
p = subprocess.Popen(['powershell', '-NoProfile', '-WindowStyle', 'Hidden', '-Command', '-'], stdin=subprocess.PIPE, creationflags=0x08000000)
p.stdin.write(ps_script.encode())
p.stdin.close()
print("Waiting for splash...")
try:
    p.wait(timeout=5)
except subprocess.TimeoutExpired:
    p.kill()
    print("Killed after 5s")
