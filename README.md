# BluePC - Monitor de Sistema

Aplicativo de monitoramento de sistema que exibe informações sobre processador, memória, adaptador de vídeo e armazenamento.

## 📋 Características

- Interface moderna com tema azul escuro
- Transparência e bordas arredondadas
- Ícone personalizado na bandeja do sistema
- Inicia minimizado na bandeja (system tray)
- Atualização automática do uso de CPU
- Totalmente responsivo e redimensionável

## 🚀 Como Criar o Executável

1. Execute o arquivo `criar_executavel.bat`
2. Aguarde a criação do executável
3. O arquivo `BluePC.exe` será criado na pasta `dist\`

## 📦 Como Instalar no Startup

### Opção 1: Usando o executável (recomendado)
1. Primeiro, crie o executável usando `criar_executavel.bat`
2. Copie o arquivo `BluePC.exe` da pasta `dist\` para a pasta principal
3. **Execute `instalar_executavel.bat` como ADMINISTRADOR** (botão direito → Executar como administrador)
4. O aplicativo será instalado com **PRIORIDADE ALTA** e configurado para ser um dos primeiros a iniciar

**Configurações aplicadas:**
- Tarefa agendada do Windows com prioridade HIGHEST
- Registro no sistema para inicialização automática
- Prioridade de execução elevada
- Janela abre automaticamente ao iniciar (não fica minimizada)

### Opção 2: Usando Python
1. Execute `instalar_startup.bat`
2. Requer Python instalado no sistema

### Desinstalar do Startup
- Execute `desinstalar_startup.bat` como administrador para remover completamente do startup

## 💻 Requisitos para Desenvolvimento

- Python 3.8 ou superior
- Bibliotecas: psutil, Pillow, pystray

Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🎯 Como Usar

- O aplicativo inicia minimizado na bandeja do sistema
- Clique no ícone azul na bandeja para abrir o menu
- Duplo clique para mostrar a janela
- Clique no X para minimizar (não fecha o app)
- Use "Sair" no menu da bandeja para fechar completamente

## 📝 Informações Exibidas

- **Processador**: Nome, velocidade e uso atual
- **Memória**: Total instalado e tipo (DDR3/DDR4/etc)
- **Adaptador de Vídeo**: GPU, VRAM e versão do driver
- **Armazenamento**: Total e uso de cada partição

## 👨‍💻 Desenvolvedor

GitHub: https://github.com/Neexll
