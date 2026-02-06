import subprocess

print("=== TESTE DE DETECÇÃO DE GPU ===\n")

# Teste 1: Lista todos os nomes de GPUs
print("1. Nomes das GPUs detectadas:")
print("-" * 50)
try:
    result = subprocess.run(
        ['wmic', 'path', 'win32_VideoController', 'get', 'Name'],
        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    print(result.stdout)
except Exception as e:
    print(f"Erro: {e}")

# Teste 2: Lista VRAM
print("\n2. VRAM das GPUs:")
print("-" * 50)
try:
    result = subprocess.run(
        ['wmic', 'path', 'win32_VideoController', 'get', 'AdapterRAM'],
        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    print(result.stdout)
except Exception as e:
    print(f"Erro: {e}")

# Teste 3: Lista completa
print("\n3. Informações completas:")
print("-" * 50)
try:
    result = subprocess.run(
        ['wmic', 'path', 'win32_VideoController', 'get', 'Name,AdapterRAM,PNPDeviceID'],
        capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
    )
    print(result.stdout)
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "=" * 50)
print("Copie e cole toda essa saída para análise")
input("\nPressione Enter para fechar...")
