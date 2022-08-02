import subprocess, time

# Connect to OpenVPN


openVpnPath = "C:\\Program Files\\OpenVPN\\bin\\openvpn.exe"
vpnCompanyName = "su" #bedzie brane z .toml
vpnCompanyFile = f"vpn\{vpnCompanyName}.ovpn"
vpnCompanyCred = f"vpn\{vpnCompanyName}.txt"

command = [openVpnPath, "--config", vpnCompanyFile, "--auth-user-pass", vpnCompanyCred]

with open('vpnlog\output.txt', 'w') as file: proc = subprocess.Popen(command, stdout=file)


for i in range(2):
    print("PID:", proc.pid)
    time.sleep(10)
    print("Czekamy juz", i*5)

file = open('vpnlog\output.txt', 'r')
for line in file:
    print(line)

#zabije proces 
proc.terminate()





