import tkinter as tk
from tkinter import ttk
import subprocess
import psutil
import platform
import os
import ctypes
import winreg
import pystray
from PIL import Image, ImageDraw
import sys


def get_ram_info():
    """Retorna informações da RAM."""
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)
    
    # Arredonda para o valor mais próximo (ex: 15.4 GB -> 16 GB)
    # Valores comuns: 4, 8, 16, 32, 64 GB
    common_sizes = [2, 4, 6, 8, 12, 16, 20, 24, 32, 48, 64, 96, 128]
    rounded_gb = min(common_sizes, key=lambda x: abs(x - total_gb))
    
    # Tenta obter o tipo de memória via PowerShell (mais confiável)
    mem_type = None
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-WmiObject Win32_PhysicalMemory | Select-Object -First 1 -ExpandProperty SMBIOSMemoryType'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5
        )
        
        memory_types = {
            '0': 'Unknown', '1': 'Other', '2': 'DRAM',
            '3': 'Synchronous DRAM', '4': 'Cache DRAM', '5': 'EDO',
            '6': 'EDRAM', '7': 'VRAM', '8': 'SRAM', '9': 'RAM',
            '10': 'ROM', '11': 'Flash', '12': 'EEPROM',
            '13': 'FEPROM', '14': 'EPROM', '15': 'CDRAM',
            '16': '3DRAM', '17': 'SDRAM', '18': 'SGRAM',
            '19': 'RDRAM', '20': 'DDR', '21': 'DDR2',
            '22': 'DDR2 FB-DIMM', '23': 'DDR2', '24': 'DDR3',
            '25': 'FBD2', '26': 'DDR4', '27': 'LPDDR',
            '28': 'LPDDR2', '29': 'LPDDR3', '30': 'LPDDR4',
            '31': 'Logical non-volatile device', '32': 'HBM',
            '33': 'HBM2', '34': 'DDR5', '35': 'LPDDR5'
        }
        
        code = result.stdout.strip()
        if code and code in memory_types:
            mem_type = memory_types[code]
            # Se for tipo genérico, tenta usar DDR3 como padrão mais comum
            if mem_type in ['Unknown', 'Other', 'DRAM', 'RAM']:
                mem_type = None
    except:
        pass
    
    # Se PowerShell falhou, tenta WMIC como fallback
    if not mem_type:
        try:
            result = subprocess.run(
                ['wmic', 'memorychip', 'get', 'SMBIOSMemoryType'],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            memory_types = {
                '20': 'DDR', '21': 'DDR2', '22': 'DDR2',
                '24': 'DDR3', '26': 'DDR4', '34': 'DDR5'
            }
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:
                code = line.strip()
                if code in memory_types:
                    mem_type = memory_types[code]
                    break
        except:
            pass
    
    # Se ainda não conseguiu detectar, usa DDR3 como padrão (mais comum)
    if not mem_type:
        mem_type = "DDR3"
    
    return f"{rounded_gb} GB", mem_type


def get_motherboard_info():
    """Retorna informações da placa mãe."""
    manufacturer = "N/A"
    product = "N/A"
    
    try:
        # Tenta obter fabricante
        result = subprocess.run(
            ['wmic', 'baseboard', 'get', 'Manufacturer'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            manufacturer = lines[1].strip()
        
        # Tenta obter modelo
        result = subprocess.run(
            ['wmic', 'baseboard', 'get', 'Product'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            product = lines[1].strip()
    except:
        pass
    
    if manufacturer != "N/A" and product != "N/A":
        return f"{manufacturer} {product}"
    elif manufacturer != "N/A":
        return manufacturer
    elif product != "N/A":
        return product
    
    return "Placa mãe não detectada"


def get_cpu_info():
    """Retorna informações do processador."""
    cpu_name = None
    clock_ghz = 0
    
    # Tenta obter o nome do registro do Windows primeiro (nome comercial)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Erro ao ler registro: {e}")
    
    # Se não conseguiu do registro, tenta WMIC
    if not cpu_name:
        try:
            name_result = subprocess.run(
                ['wmic', 'cpu', 'get', 'Name'],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            lines = name_result.stdout.strip().split('\n')
            if len(lines) > 1:
                cpu_name = lines[1].strip()
        except Exception as e:
            print(f"Erro ao ler WMIC: {e}")
    
    # Se ainda não tem nome, usa platform
    if not cpu_name:
        cpu_name = platform.processor()
    
    # Tenta obter clock speed via PowerShell (mais confiável)
    try:
        speed_result = subprocess.run(
            ['powershell', '-Command', 'Get-WmiObject Win32_Processor | Select-Object -First 1 -ExpandProperty MaxClockSpeed'],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5
        )
        max_speed = speed_result.stdout.strip()
        if max_speed:
            clock_ghz = float(max_speed) / 1000
    except:
        pass
    
    # Se PowerShell falhou, tenta WMIC como fallback
    if clock_ghz == 0:
        try:
            speed_result = subprocess.run(
                ['wmic', 'cpu', 'get', 'MaxClockSpeed'],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            max_speed = speed_result.stdout.strip().split('\n')[1].strip()
            clock_ghz = float(max_speed) / 1000
        except:
            pass
    
    # Se ainda não conseguiu, tenta extrair do nome da CPU
    if clock_ghz == 0 and ' @ ' in cpu_name:
        parts = cpu_name.split(' @ ')
        try:
            clock_str = parts[1].replace('GHz', '').strip()
            clock_ghz = float(clock_str)
        except:
            pass
    
    # Como última alternativa, tenta psutil
    if clock_ghz == 0:
        try:
            freq = psutil.cpu_freq()
            if freq and freq.max > 0:
                clock_ghz = freq.max / 1000
        except:
            pass
    
    # Se o nome já tem @ e clock, retorna como está
    if ' @ ' in cpu_name and 'GHz' in cpu_name:
        return cpu_name, f"{clock_ghz:.2f} GHz" if clock_ghz > 0 else "N/A"
    
    # Senão, adiciona o clock
    if clock_ghz > 0:
        full_name = f"{cpu_name} @ {clock_ghz:.2f}GHz"
        return full_name, f"{clock_ghz:.2f} GHz"
    
    return cpu_name, "N/A"


def get_cpu_usage():
    """Retorna uso atual da CPU."""
    return psutil.cpu_percent(interval=0.1)


def get_gpu_info():
    """Retorna informações da placa de vídeo (GPU) pelo chip instalado."""
    gpus = []
    
    try:
        # Usa PowerShell para obter informações das GPUs (mais confiável que WMIC)
        ps_command = "Get-WmiObject Win32_VideoController | Select-Object Name, AdapterRAM | ForEach-Object { $_.Name + '|' + $_.AdapterRAM }"
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10
        )
        
        # Processa a saída
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    vram = parts[1].strip()
                    if name:
                        gpu = {'Name': name}
                        if vram and vram != '':
                            gpu['AdapterRAM'] = vram
                        gpus.append(gpu)
            
    except Exception as e:
        # Se PowerShell falhar, tenta WMIC como fallback
        try:
            name_result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'Name'],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            vram_result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'AdapterRAM'],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            names = []
            for line in name_result.stdout.strip().split('\n')[1:]:
                name = line.strip()
                if name:
                    names.append(name)
            
            vrams = []
            for line in vram_result.stdout.strip().split('\n')[1:]:
                vram_str = line.strip()
                if vram_str:
                    vrams.append(vram_str)
            
            for i, name in enumerate(names):
                gpu = {'Name': name}
                if i < len(vrams):
                    gpu['AdapterRAM'] = vrams[i]
                gpus.append(gpu)
        except:
            pass
    
    # Se não encontrou nenhuma GPU, retorna valores padrão
    if not gpus:
        return "Nenhuma GPU detectada", "N/A", "N/A"
    
    # Prioriza GPUs dedicadas (NVIDIA, AMD Radeon, Intel Arc)
    # mas mantém integradas (AMD Radeon Graphics, Intel UHD/HD Graphics)
    dedicated_gpu = None
    integrated_gpu = None
    other_gpu = None
    
    for gpu in gpus:
        name = gpu.get('Name', '')
        
        # Ignora apenas "Standard VGA Graphics Adapter" que é placeholder
        if 'Standard VGA' in name:
            continue
        
        # Identifica GPU dedicada NVIDIA
        if any(x in name for x in ['GeForce', 'GTX', 'RTX', 'Quadro', 'NVIDIA', ' GT ', ' G ']):
            dedicated_gpu = gpu
        # AMD Radeon dedicadas (qualquer Radeon que não seja "Graphics")
        elif 'Radeon' in name and 'Graphics' not in name:
            dedicated_gpu = gpu
        # Intel Arc
        elif 'Intel Arc' in name:
            dedicated_gpu = gpu
        # Identifica GPU integrada AMD (Ryzen)
        elif ('AMD' in name or 'Radeon' in name) and 'Graphics' in name:
            integrated_gpu = gpu
        elif any(x in name for x in ['Vega', 'Radeon Vega']):
            integrated_gpu = gpu
        # Identifica GPU integrada Intel
        elif any(x in name for x in ['Intel(R) UHD', 'Intel(R) HD', 'Intel(R) Iris', 'Intel UHD', 'Intel HD']):
            integrated_gpu = gpu
        # Qualquer outra GPU válida (incluindo Microsoft Basic Display)
        else:
            if not other_gpu:
                other_gpu = gpu
    
    # Prioriza: GPU dedicada > GPU integrada > Outra GPU
    selected_gpu = dedicated_gpu or integrated_gpu or other_gpu
    
    if not selected_gpu:
        return "Nenhuma GPU detectada", "N/A", "N/A"
    
    # Extrai informações da GPU selecionada
    gpu_name = selected_gpu.get('Name', 'GPU não identificada')
    
    # Verifica se é um nome genérico (português e inglês)
    # Remove acentos para comparação
    import unicodedata
    gpu_name_normalized = ''.join(
        c for c in unicodedata.normalize('NFD', gpu_name.lower())
        if unicodedata.category(c) != 'Mn'
    )
    
    generic_keywords = ['basic', 'basico', 'microsoft', 'adapter', 'adaptador', 'display', 'video', 'standard']
    is_generic = any(x in gpu_name_normalized for x in generic_keywords)
    
    # Se for adaptador básico/genérico ou não identificado, tenta identificar via PCI ID
    if is_generic or gpu_name == 'GPU não identificada':
        try:
            # Busca TODAS as GPUs e seus PCI IDs
            ps_cmd = "Get-WmiObject Win32_VideoController | ForEach-Object { $_.PNPDeviceID }"
            result = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5
            )
            
            # Processa cada PCI ID encontrado
            for line in result.stdout.strip().split('\n'):
                pnp_id = line.strip()
                
                if pnp_id and 'VEN_' in pnp_id:
                    # Identifica fabricante pelo Vendor ID
                    if 'VEN_10DE' in pnp_id:  # NVIDIA
                        # Tenta identificar modelo NVIDIA específico pelo Device ID
                        # GT 730
                        if 'DEV_1287' in pnp_id or 'DEV_0FC6' in pnp_id or 'DEV_1288' in pnp_id or 'DEV_0F02' in pnp_id:
                            gpu_name = "NVIDIA GeForce GT 730"
                        # GTX 750 Ti
                        elif 'DEV_1380' in pnp_id:
                            gpu_name = "NVIDIA GeForce GTX 750 Ti"
                        # GTX 750
                        elif 'DEV_1381' in pnp_id:
                            gpu_name = "NVIDIA GeForce GTX 750"
                        # GT 710
                        elif 'DEV_128B' in pnp_id or 'DEV_1288' in pnp_id:
                            gpu_name = "NVIDIA GeForce GT 710"
                        # GT 1030
                        elif 'DEV_1D01' in pnp_id:
                            gpu_name = "NVIDIA GeForce GT 1030"
                        # GTX 1050
                        elif 'DEV_1C81' in pnp_id or 'DEV_1C82' in pnp_id:
                            gpu_name = "NVIDIA GeForce GTX 1050"
                        # GTX 1050 Ti
                        elif 'DEV_1C8C' in pnp_id:
                            gpu_name = "NVIDIA GeForce GTX 1050 Ti"
                        # GTX 1060
                        elif 'DEV_1C03' in pnp_id or 'DEV_1C02' in pnp_id:
                            gpu_name = "NVIDIA GeForce GTX 1060"
                        # GTX 1650
                        elif 'DEV_1F82' in pnp_id:
                            gpu_name = "NVIDIA GeForce GTX 1650"
                        # GTX 1660
                        elif 'DEV_2184' in pnp_id:
                            gpu_name = "NVIDIA GeForce GTX 1660"
                        else:
                            gpu_name = "NVIDIA GPU"
                        break
                    elif 'VEN_1002' in pnp_id:  # AMD
                        # Tenta identificar modelo AMD específico pelo Device ID
                        if 'DEV_699F' in pnp_id or 'DEV_67FF' in pnp_id:
                            gpu_name = "AMD Radeon RX 550"
                        elif 'DEV_67DF' in pnp_id:
                            gpu_name = "AMD Radeon RX 560"
                        elif 'DEV_67EF' in pnp_id:
                            gpu_name = "AMD Radeon RX 570"
                        elif 'DEV_6FDF' in pnp_id:
                            gpu_name = "AMD Radeon RX 580"
                        elif 'DEV_67C4' in pnp_id:
                            gpu_name = "AMD Radeon RX 590"
                        else:
                            gpu_name = "AMD Radeon GPU"
                        break
                    elif 'VEN_8086' in pnp_id:  # Intel
                        gpu_name = "Intel GPU"
                        break
        except:
            pass
    
    # VRAM - tenta obter de múltiplas fontes
    vram = ""
    adapter_ram = selected_gpu.get('AdapterRAM', '')
    
    # Identifica o VRAM real via Registro do Windows (evita limite de 4GB do WMI)
    try:
        base_key = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_key) as key:
            for i in range(256):
                try:
                    sub_key_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, sub_key_name) as sub_key:
                        try:
                            driver_desc = winreg.QueryValueEx(sub_key, "DriverDesc")[0]
                            if driver_desc == gpu_name:
                                try:
                                    # Pega o valor em 64 bits se disponivel
                                    mem_size = winreg.QueryValueEx(sub_key, "HardwareInformation.qwMemorySize")[0]
                                    adapter_ram = str(mem_size)
                                    break
                                except FileNotFoundError:
                                    try:
                                        mem_size_bytes = winreg.QueryValueEx(sub_key, "HardwareInformation.MemorySize")[0]
                                        if isinstance(mem_size_bytes, bytes):
                                            mem_size = int.from_bytes(mem_size_bytes, "little")
                                        else:
                                            mem_size = mem_size_bytes
                                        
                                        # So atualiza caso o adapter_ram esteja negativo (bug WMI) ou vazio
                                        if not adapter_ram or int(adapter_ram) < 0 or int(adapter_ram) == 4293918720:
                                            adapter_ram = str(mem_size)
                                        break
                                    except FileNotFoundError:
                                        pass
                        except FileNotFoundError:
                            pass
                except OSError:
                    break
    except Exception:
        pass
    
    # Detecta se é GPU integrada Intel
    is_intel_integrated = 'Intel' in gpu_name and any(x in gpu_name for x in ['HD Graphics', 'UHD Graphics', 'Iris'])
    
    # Detecta se é GPU integrada AMD (Ryzen)
    is_amd_integrated = 'AMD' in gpu_name and 'Radeon' in gpu_name and 'Graphics' in gpu_name and not any(x in gpu_name for x in ['RX', 'HD', 'R7', 'R9'])
    
    if adapter_ram:
        try:
            vram_bytes = int(adapter_ram)
            if vram_bytes > 0:
                vram_mb = vram_bytes / (1024 ** 2)
                vram_gb = vram_bytes / (1024 ** 3)
                
                # Para GPUs integradas Intel, ajusta valores para padrões realistas
                if is_intel_integrated:
                    # Se reportar mais que 256 MB, é memória compartilhada
                    if vram_mb > 256:
                        if 'HD Graphics 2' in gpu_name or 'HD Graphics 3' in gpu_name:
                            vram = "32 MB VRAM"
                        elif 'HD Graphics 4' in gpu_name or 'HD Graphics 5' in gpu_name:
                            vram = "128 MB VRAM"
                        elif 'HD Graphics 6' in gpu_name or 'HD Graphics 7' in gpu_name:
                            vram = "128 MB VRAM"
                        elif 'UHD' in gpu_name:
                            vram = "128 MB VRAM"
                        else:
                            # Valor padrão para Intel HD Graphics sem número (geralmente gerações antigas)
                            vram = "32 MB VRAM"
                    # Se reportar entre 100-128 MB, arredonda para 128 MB (HD Graphics 4xxx/5xxx)
                    elif 100 <= vram_mb <= 128 and ('HD Graphics 4' in gpu_name or 'HD Graphics 5' in gpu_name):
                        vram = "128 MB VRAM"
                    # Se reportar entre 25-40 MB, arredonda para 32 MB (HD Graphics 2xxx/3xxx)
                    elif 25 <= vram_mb <= 40 and ('HD Graphics 2' in gpu_name or 'HD Graphics 3' in gpu_name):
                        vram = "32 MB VRAM"
                    # Senão, usa o valor reportado
                    else:
                        vram = f"{vram_mb:.0f} MB VRAM"
                # Para GPUs integradas AMD, ajusta para valor padrão de 512 MB
                elif is_amd_integrated and vram_mb < 1024:
                    # Se reportar entre 400-600 MB, arredonda para 512 MB
                    if 400 <= vram_mb <= 600:
                        vram = "512 MB VRAM"
                    # Se reportar menos de 400 MB, também usa 512 MB
                    elif vram_mb < 400:
                        vram = "512 MB VRAM"
                    else:
                        vram = f"{vram_mb:.0f} MB VRAM"
                # Se for menos de 512 MB, mostra em MB
                elif vram_mb < 512:
                    vram = f"{vram_mb:.0f} MB VRAM"
                # Se for 512 MB ou mais, mostra em GB
                else:
                    vram = f"{vram_gb:.0f} GB VRAM"
        except:
            pass
    
    # Correção específica: RX 580 2048SP da Haoqing tem 8 GB mas o WMI reporta ~4 GB
    RX580_2048SP_VRAM_GB = 8
    if 'RX 580 2048SP' in gpu_name and vram and '4 GB' in vram:
        vram = f"{RX580_2048SP_VRAM_GB} GB VRAM"
    
    # Se não conseguiu obter VRAM e é GPU integrada AMD, usa valor padrão
    if not vram and is_amd_integrated:
        vram = "512 MB VRAM"
    
    # Se não conseguiu obter VRAM, tenta via DXGI (para GPUs integradas)
    if not vram:
        try:
            result = subprocess.run(
                ['powershell', '-Command', 
                 f"(Get-WmiObject Win32_VideoController | Where-Object {{$_.Name -eq '{gpu_name}'}}).AdapterRAM"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=3
            )
            if result.stdout.strip():
                vram_bytes = int(result.stdout.strip())
                if vram_bytes > 0:
                    vram_gb = vram_bytes / (1024 ** 3)
                    if vram_gb >= 1:
                        vram = f"{vram_gb:.0f} GB VRAM"
                    else:
                        vram_mb = vram_bytes / (1024 ** 2)
                        vram = f"{vram_mb:.0f} MB VRAM"
        except:
            pass
    
    # Se ainda não tem VRAM, mostra "Compartilhada" para integradas
    if not vram:
        # Verifica se é GPU integrada AMD ou Intel
        if ('AMD' in gpu_name and 'Radeon' in gpu_name and 'Graphics' in gpu_name) or \
           any(x in gpu_name for x in ['Vega', 'Intel(R) UHD', 'Intel(R) HD', 'Intel UHD', 'Intel HD']):
            vram = "Memória Compartilhada"
        else:
            vram = "N/A"
    
    # Linha adicional (N/A)
    driver = "N/A"
    
    return gpu_name, vram, driver


def get_storage_info():
    """Retorna informações de armazenamento."""
    partitions_info = []
    
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total_gb = usage.total / (1024 ** 3)
            used_gb = usage.used / (1024 ** 3)
            partitions_info.append({
                'mountpoint': partition.mountpoint,
                'total': total_gb,
                'used': used_gb
            })
        except:
            continue
    
    # Retorna lista de partições
    return partitions_info


class SystemInfoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BluePC")
        self.root.configure(bg='#0a0a1a')
        self.root.geometry("420x780")
        self.root.minsize(420, 780)
        self.root.resizable(True, True)
        
        # Define ícone da janela
        try:
            self.create_icon()
        except:
            pass
        
        # Bind para redimensionamento
        self.root.bind('<Configure>', self.on_resize)
        
        # Transparência da janela (0.0 = invisível, 1.0 = opaco)
        self.root.attributes('-alpha', 0.88)
        
        # Altera a cor da barra de título para dark (Windows 10/11)
        try:
            # Para Windows 11
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 
                                                       ctypes.byref(value), ctypes.sizeof(value))
            
            # Adiciona bordas arredondadas (Windows 11)
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWM_WINDOW_CORNER_ROUND = 2
            corner_value = ctypes.c_int(DWM_WINDOW_CORNER_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                                                       ctypes.byref(corner_value), ctypes.sizeof(corner_value))
        except:
            pass
        
        # Cores
        self.bg_color = '#0a0a1a'
        self.card_bg = '#0d1525'
        self.accent_color = '#00a8ff'
        self.text_color = '#ffffff'
        self.subtext_color = '#7a8899'
        
        self.widgets = {}
        self.last_width = 420
        self.last_height = 780
        
        # Centralizar na tela
        self.center_window()
        
        self.create_widgets()
        self.update_dynamic_info()
        
    def create_icon(self):
        """Cria e define o ícone da janela."""
        from PIL import Image, ImageDraw
        import os
        
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        
        # Cria uma imagem 256x256 com fundo transparente
        img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Cor azul ciano do logo
        color = (102, 204, 255)
        
        # Desenha o logo BluePC (formato L invertido) - proporções corretas
        # Margem de 20 pixels
        margin = 20
        
        # Barra horizontal superior (larga)
        draw.rectangle([margin, margin, 236, margin + 60], fill=color)
        
        # Barra vertical direita (conectada à horizontal)
        draw.rectangle([176, margin, 236, 176], fill=color)
        
        # Quadrado pequeno inferior esquerdo
        draw.rectangle([margin, 116, margin + 80, 196], fill=color)
        
        # Salva como .ico
        img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        
        # Define o ícone
        self.root.iconbitmap(icon_path)
    
    def center_window(self):
        """Posiciona a janela no canto superior direito."""
        self.root.update_idletasks()
        width = 420
        height = 780
        screen_width = self.root.winfo_screenwidth()
        x = screen_width - width - 10  # 10 pixels de margem da borda direita
        y = 10  # 10 pixels de margem do topo
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def format_cpu_name(self, cpu_name):
        """Formata o nome do CPU em múltiplas linhas para melhor visualização."""
        # Remove "CPU @" se existir e separa a velocidade
        cpu_name_clean = cpu_name.replace(' CPU @ ', ' @ ')
        
        # Divide pelo @ para separar modelo e velocidade
        if ' @ ' in cpu_name_clean:
            parts = cpu_name_clean.split(' @ ')
            model = parts[0].strip()
            speed = parts[1].strip()
            
            # Para processadores Intel Core i3/i5/i7/i9
            if ' i' in model and ('Core' in model or 'CORE' in model):
                core_parts = model.split(' i', 1)
                line1 = core_parts[0].strip()
                line2 = 'i' + core_parts[1].strip() + ' @ ' + speed
                return f"{line1}\n{line2}"
            # Para outros processadores
            else:
                # Tenta dividir em 2 linhas de forma inteligente
                words = model.split()
                if len(words) >= 4:
                    # Primeira linha: primeiras palavras (marca)
                    line1 = ' '.join(words[:2])
                    # Segunda linha: resto do modelo + @ + velocidade
                    line2 = ' '.join(words[2:]) + ' @ ' + speed
                    return f"{line1}\n{line2}"
                else:
                    return f"{model} @ {speed}"
        
        # Se não tem @, retorna como está
        return cpu_name
    
    def get_font_size(self, base_size):
        """Calcula tamanho da fonte baseado no tamanho da janela."""
        width = self.root.winfo_width()
        scale = max(0.7, min(1.5, width / 420))
        return int(base_size * scale)
    
    def on_resize(self, event):
        """Callback para redimensionamento da janela."""
        if event.widget == self.root and hasattr(self, 'last_width'):
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            # Evita múltiplas atualizações
            if abs(current_width - self.last_width) > 10 or abs(current_height - self.last_height) > 10:
                self.last_width = current_width
                self.last_height = current_height
                self.update_fonts()
    
    def update_fonts(self):
        """Atualiza tamanhos de fonte baseado no tamanho da janela."""
        if not hasattr(self, 'widgets') or not self.widgets:
            return
        
        # Atualiza título principal
        if 'title' in self.widgets:
            self.widgets['title'].config(font=('Segoe UI', self.get_font_size(18), 'bold'))
        
        # Atualiza subtítulo
        if 'subtitle' in self.widgets:
            self.widgets['subtitle'].config(font=('Segoe UI', self.get_font_size(11)))
        
        # Atualiza GitHub link
        if 'github_link' in self.widgets:
            self.widgets['github_link'].config(font=('Segoe UI', self.get_font_size(9), 'underline'))
        
        # Atualiza cards
        for key, widget in self.widgets.items():
            if 'card_title' in key:
                widget.config(font=('Segoe UI', self.get_font_size(12), 'bold'))
            elif 'ram_value' in key:
                widget.config(font=('Segoe UI', self.get_font_size(24), 'bold'))
            elif 'ram_type' in key or 'cpu_clock' in key or 'storage_used' in key:
                widget.config(font=('Segoe UI', self.get_font_size(10)))
            elif 'cpu_name' in key:
                widget.config(font=('Segoe UI', self.get_font_size(14), 'bold'))
            elif 'cpu_usage' in key:
                widget.config(font=('Segoe UI', self.get_font_size(10)))
            elif 'gpu_name' in key:
                widget.config(font=('Segoe UI', self.get_font_size(16), 'bold'))
            elif 'gpu_vram' in key:
                widget.config(font=('Segoe UI', self.get_font_size(10)))
            elif 'gpu_driver' in key:
                widget.config(font=('Segoe UI', self.get_font_size(9)))
            elif 'storage_total' in key:
                widget.config(font=('Segoe UI', self.get_font_size(24), 'bold'))
            elif 'storage_info' in key:
                widget.config(font=('Segoe UI', self.get_font_size(10)))
    
    def open_github(self):
        """Abre o link do GitHub no navegador."""
        import webbrowser
        webbrowser.open('https://github.com/Neexll')
    
    def create_card(self, parent, title, row):
        """Cria um card estilizado usando grid."""
        card = tk.Frame(parent, bg=self.card_bg, highlightbackground='#1a2a40',
                       highlightthickness=1)
        card.grid(row=row, column=0, padx=20, pady=5, sticky='ew')
        
        # Borda superior azul
        border = tk.Frame(card, bg=self.accent_color, height=3)
        border.pack(fill='x', side='top')
        
        # Container interno com padding
        inner = tk.Frame(card, bg=self.card_bg)
        inner.pack(fill='both', expand=True, padx=12, pady=8)
        
        # Título do card
        title_label = tk.Label(inner, text=title, font=('Segoe UI', self.get_font_size(12), 'bold'),
                              fg=self.accent_color, bg=self.card_bg, anchor='w')
        title_label.pack(anchor='w')
        
        self.widgets[f'card_title_{row}'] = title_label
        
        return card, inner
    
    def create_widgets(self):
        # Container do cabeçalho
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(pady=(15, 5))
        
        # Título principal
        title = tk.Label(header_frame, text="BluePC",
                        font=('Segoe UI', self.get_font_size(18), 'bold'), fg=self.accent_color,
                        bg=self.bg_color)
        title.pack()
        self.widgets['title'] = title
        
        # Subtítulo
        subtitle = tk.Label(header_frame, text="Configurações do sistema",
                           font=('Segoe UI', self.get_font_size(14), 'bold'), fg=self.subtext_color,
                           bg=self.bg_color)
        subtitle.pack()
        self.widgets['subtitle'] = subtitle
        
        # Container principal com scroll
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=10)
        container.grid_columnconfigure(0, weight=1)
        
        # === CARD CPU ===
        cpu_card, cpu_inner = self.create_card(container, "PROCESSADOR", 0)
        cpu_name, cpu_clock = get_cpu_info()
        cpu_name_formatted = self.format_cpu_name(cpu_name)
        
        self.cpu_name = tk.Label(cpu_inner, text=cpu_name_formatted, 
                                font=('Segoe UI', self.get_font_size(14), 'bold'),
                                fg=self.text_color, bg=self.card_bg, justify='left', anchor='w')
        self.cpu_name.pack(anchor='w', pady=(5, 0))
        self.widgets['cpu_name'] = self.cpu_name
        
        cpu_info_frame = tk.Frame(cpu_inner, bg=self.card_bg)
        cpu_info_frame.pack(anchor='w', pady=(5, 0), fill='x')
        
        self.cpu_clock = tk.Label(cpu_info_frame, text=cpu_clock, 
                                 font=('Segoe UI', self.get_font_size(10)),
                                 fg=self.subtext_color, bg=self.card_bg)
        self.cpu_clock.pack(side='left')
        self.widgets['cpu_clock'] = self.cpu_clock
        
        self.cpu_usage = tk.Label(cpu_info_frame, text="Uso: 0%", 
                                 font=('Segoe UI', self.get_font_size(10)),
                                 fg=self.accent_color, bg=self.card_bg)
        self.cpu_usage.pack(side='left', padx=(20, 0))
        self.widgets['cpu_usage'] = self.cpu_usage
        
        # === CARD MEMÓRIA ===
        ram_card, ram_inner = self.create_card(container, "MEMÓRIA", 1)
        ram_total, ram_type = get_ram_info()
        
        self.ram_value = tk.Label(ram_inner, text=ram_total, 
                                 font=('Segoe UI', self.get_font_size(24), 'bold'),
                                 fg=self.text_color, bg=self.card_bg, anchor='w')
        self.ram_value.pack(anchor='w', pady=(5, 0))
        self.widgets['ram_value'] = self.ram_value
        
        self.ram_type = tk.Label(ram_inner, text=ram_type, 
                                font=('Segoe UI', self.get_font_size(10)),
                                fg=self.subtext_color, bg=self.card_bg, anchor='w')
        self.ram_type.pack(anchor='w', pady=(5, 0))
        self.widgets['ram_type'] = self.ram_type
        
        # === CARD ADAPTADOR DE VÍDEO ===
        gpu_card, gpu_inner = self.create_card(container, "ADAPTADOR DE VÍDEO", 2)
        gpu_name, gpu_vram, gpu_driver = get_gpu_info()
        
        self.gpu_name = tk.Label(gpu_inner, text=gpu_name, 
                                font=('Segoe UI', self.get_font_size(16), 'bold'),
                                fg=self.text_color, bg=self.card_bg, anchor='w', wraplength=350)
        self.gpu_name.pack(anchor='w', pady=(5, 0))
        self.widgets['gpu_name'] = self.gpu_name
        
        self.gpu_vram = tk.Label(gpu_inner, text=gpu_vram, 
                                font=('Segoe UI', self.get_font_size(10)),
                                fg=self.subtext_color, bg=self.card_bg, anchor='w')
        self.gpu_vram.pack(anchor='w', pady=(5, 0))
        self.widgets['gpu_vram'] = self.gpu_vram
        
        self.gpu_driver = tk.Label(gpu_inner, text=gpu_driver, 
                                  font=('Segoe UI', self.get_font_size(9)),
                                  fg=self.accent_color, bg=self.card_bg, anchor='w')
        self.gpu_driver.pack(anchor='w', pady=(5, 0))
        self.widgets['gpu_driver'] = self.gpu_driver
        
        # === CARD ARMAZENAMENTO ===
        storage_card, storage_inner = self.create_card(container, "ARMAZENAMENTO", 3)
        partitions = get_storage_info()
        
        # Calcula total de todos os discos
        total_all = sum(p['total'] for p in partitions)
        
        # Linha 1: Total de todos os discos
        total_label = tk.Label(storage_inner, text=f"{total_all:.0f} GB",
                              font=('Segoe UI', self.get_font_size(24), 'bold'),
                              fg=self.text_color, bg=self.card_bg, anchor='w')
        total_label.pack(anchor='w', pady=(5, 0))
        self.widgets['storage_total'] = total_label
        
        # Linha 2+: Diretório, total e uso de cada partição
        self.storage_labels = []
        for i, partition in enumerate(partitions):
            info_text = f"{partition['mountpoint']} - {partition['used']:.0f} GB de {partition['total']:.0f} GB usados"
            info_label = tk.Label(storage_inner, text=info_text,
                                 font=('Segoe UI', self.get_font_size(10)),
                                 fg=self.subtext_color, bg=self.card_bg, anchor='w',
                                 wraplength=350)
            info_label.pack(anchor='w', pady=(2, 0))
            self.storage_labels.append(info_label)
            self.widgets[f'storage_info_{i}'] = info_label
        
        # Rodapé com GitHub
        footer_frame = tk.Frame(self.root, bg=self.bg_color)
        footer_frame.pack(pady=10)
        
        github_label = tk.Label(footer_frame, text="GitHub: ",
                               font=('Segoe UI', self.get_font_size(9)),
                               fg=self.subtext_color, bg=self.bg_color)
        github_label.pack(side='left')
        
        github_link = tk.Label(footer_frame, text="https://github.com/Neexll",
                              font=('Segoe UI', self.get_font_size(9), 'underline'),
                              fg=self.accent_color, bg=self.bg_color,
                              cursor='hand2')
        github_link.pack(side='left')
        github_link.bind('<Button-1>', lambda e: self.open_github())
        self.widgets['github_link'] = github_link
    
    def update_dynamic_info(self):
        """Atualiza informações dinâmicas (uso de CPU)."""
        cpu_usage = get_cpu_usage()
        self.cpu_usage.config(text=f"Uso: {cpu_usage:.0f}%")
        
        # Atualiza a cada 2 segundos
        self.root.after(2000, self.update_dynamic_info)
    
    def create_tray_icon(self):
        """Cria ícone para a bandeja do sistema."""
        # Cria imagem para o ícone da bandeja
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Cor azul ciano do logo
        color = (102, 204, 255)
        
        # Desenha o logo BluePC simplificado
        margin = 8
        draw.rectangle([margin, margin, 56, margin + 15], fill=color)
        draw.rectangle([41, margin, 56, 41], fill=color)
        draw.rectangle([margin, 26, margin + 20, 46], fill=color)
        
        return image
    
    def show_window(self, icon=None, item=None):
        """Mostra a janela do aplicativo."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide_window(self):
        """Esconde a janela para a bandeja."""
        self.root.withdraw()
    
    def quit_app(self, icon=None, item=None):
        """Fecha o aplicativo completamente."""
        if icon:
            icon.stop()
        self.root.quit()
    
    def setup_tray(self):
        """Configura o ícone da bandeja do sistema."""
        menu = pystray.Menu(
            pystray.MenuItem('Mostrar', self.show_window, default=True),
            pystray.MenuItem('Sair', self.quit_app)
        )
        
        self.tray_icon = pystray.Icon(
            'BluePC',
            self.create_tray_icon(),
            'BluePC - Configurações do Sistema',
            menu
        )
    
    def on_closing(self):
        """Minimiza para a bandeja ao invés de fechar."""
        self.hide_window()
    
    def run(self):
        """Inicia o aplicativo."""
        # Configura o comportamento ao fechar
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        # Configura a bandeja do sistema
        self.setup_tray()
        
        # Inicia o ícone da bandeja em thread separada
        import threading
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
        
        # Garante que a janela apareça em primeiro plano
        self.root.deiconify()
        self.root.withdraw()
        self.root.deiconify()
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        self.root.mainloop()


def add_to_startup():
    """Adiciona o programa ao startup do Windows."""
    script_path = os.path.abspath(__file__)
    pythonw_path = os.path.join(os.path.dirname(os.sys.executable), 'pythonw.exe')
    
    startup_folder = os.path.join(
        os.environ['APPDATA'],
        'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
    )
    
    # Cria um arquivo .bat para iniciar o programa
    bat_path = os.path.join(startup_folder, 'SystemInfo.bat')
    
    with open(bat_path, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'start "" "{pythonw_path}" "{script_path}"\n')
    
    print(f"Adicionado ao startup: {bat_path}")


def check_single_instance():
    """Verifica se já existe uma instância do programa rodando."""
    try:
        current_process = psutil.Process()
        current_pid = current_process.pid
        current_exe = current_process.exe()
        
        for proc in psutil.process_iter(['pid', 'exe']):
            try:
                # Pula o próprio processo
                if proc.info['pid'] == current_pid:
                    continue
                    
                # Verifica se é outro processo BluePC com o mesmo caminho
                if proc.info['exe'] and proc.info['exe'] == current_exe:
                    print(f"Outra instância encontrada: {proc.info['exe']} (PID: {proc.info['pid']})")
                    return False
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return True
    except Exception as e:
        print(f"Erro ao verificar instância única: {e}")
        return True


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--startup":
            add_to_startup()
            print("Programa adicionado ao startup do Windows!")
        else:
            app = SystemInfoApp()
            app.run()
    except Exception as e:
        print(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para fechar...")
