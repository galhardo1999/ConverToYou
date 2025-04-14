import pystray
from PIL import Image
from pystray import MenuItem as item

def on_quit(icon, item):
    """Função para encerrar o aplicativo."""
    icon.stop()

def on_click(icon, item):
    """Função para uma ação qualquer."""
    print("Item clicado!")

# Tentar carregar o ícone
try:
    image = Image.open("icon.png")  # Verifique se o arquivo está na pasta do script
except FileNotFoundError:
    print("Ícone não encontrado. Criando um ícone padrão.")
    image = Image.new('RGB', (64, 64), color='gray')  # Ícone padrão

# Definir o menu de contexto
menu = (
    item("Mostrar Mensagem", on_click),
    item("Sair", on_quit)
)

# Criar o objeto do System Tray
icon = pystray.Icon("nome_do_app", image, "ConverToYou", menu)

# Iniciar o ícone
icon.run()