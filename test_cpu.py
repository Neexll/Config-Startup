import winreg
import subprocess

print("=== Teste 1: Registro do Windows ===")
try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                        r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
    cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    winreg.CloseKey(key)
    print(f"Nome do registro: {cpu_name}")
except Exception as e:
    print(f"Erro no registro: {e}")

print("\n=== Teste 2: WMIC ===")
try:
    result = subprocess.run(
        ['wmic', 'cpu', 'get', 'Name'],
        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        cpu_name = lines[1].strip()
        print(f"Nome do WMIC: {cpu_name}")
except Exception as e:
    print(f"Erro no WMIC: {e}")

print("\n=== Teste 3: platform.processor() ===")
import platform
print(f"Nome do platform: {platform.processor()}")
