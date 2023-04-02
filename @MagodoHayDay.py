import PySimpleGUI as sg
import pyautogui as pg
import os
import keyboard
import re
import cv2
import numpy as np
import time
from collections import namedtuple
from unidecode import unidecode

Coord = namedtuple("Coord", ["x", "y"])

valor_coords = None
venda_coords = None
regiao_coords = None
imagens_path = None
caixa_coords = [None] * 10

def update_value():
    sg.popup("Aperte espaço no campo de valor da loja", auto_close=False, non_blocking=False)
    keyboard.wait('space')
    coords = pg.position()
    return f"{coords.x}, {coords.y}"

def update_sale():
    sg.popup("Aperte espaço no campo de venda da loja", auto_close=False, non_blocking=False)
    keyboard.wait('space')
    coords = pg.position()
    return f"{coords.x}, {coords.y}"

def update_region():
    sg.popup("Mantenha 'ctrl' pressionado e selecione a região", auto_close=False, non_blocking=False)

    while True:
        if keyboard.is_pressed('ctrl'):
            start_coords = pg.position()
            break

    while True:
        if not keyboard.is_pressed('ctrl'):
            end_coords = pg.position()
            break

    x1, y1 = max(0, start_coords.x), max(0, start_coords.y)
    x2, y2 = max(0, end_coords.x), max(0, end_coords.y)

    return f"{x1}, {y1}, {x2}, {y2}"

def update_coords(coords, coords_type):
    global valor_coords, venda_coords, regiao_coords

    coords_tuple = tuple(map(int, coords.split(', ')))

    if coords_type == "valor":
        valor_coords = coords_tuple
    elif coords_type == "venda":
        venda_coords = coords_tuple
    elif coords_type == "regiao":
        regiao_coords = coords_tuple
        
def update_images(path):
    global imagens_path
    imagens_path = path
    
def update_caixa_coords(caixa_num):
    global caixa_coords
    sg.popup(f"Aperte espaço na posição da caixa {caixa_num + 1}", auto_close=False, non_blocking=False)
    keyboard.wait('space')
    coords = pg.position()
    caixa_coords[caixa_num] = coords
    print(f"Caixa {caixa_num + 1} coordenadas: {coords}")
    
def save_config(file_name):
    global valor_coords, venda_coords, regiao_coords, imagens_path, caixa_coords

    formatted_caixa_coords = ",".join(f"{c.x},{c.y}" for c in caixa_coords if c is not None)
    config_data = {
        "valor_coords": valor_coords,
        "venda_coords": venda_coords,
        "regiao_coords": regiao_coords,
        "imagens_path": imagens_path,
        "caixa_coords": formatted_caixa_coords
    }

    with open(file_name, 'w') as f:
        for key, value in config_data.items():
            if value is None:
                continue
            if key in ["valor_coords", "venda_coords", "regiao_coords"]:
                f.write(f"{key}=" + ", ".join(map(str, value)) + "\n")
            elif key == "caixa_coords":
                formatted_caixa_coords = ", ".join(f"c{i + 1}(x={c.x}, y={c.y})" for i, c in enumerate(caixa_coords) if c is not None)
                f.write(f"{key}={formatted_caixa_coords}\n")
            else:
                f.write(f"{key}: {value}\n")

    sg.Popup(f"Configuração salva no arquivo {file_name}")
    
def load_config(file_path, window):
    global valor_coords, venda_coords, regiao_coords, imagens_path, caixa_coords

    with open(file_path, "r") as f:
        config_data = {}
        for line in f.readlines():
            if "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            config_data[key] = value.strip()

    try:
        valor_coords = tuple(map(int, config_data["valor_coords"].split(",")))
        venda_coords = tuple(map(int, config_data["venda_coords"].split(",")))
        regiao_coords = tuple(map(int, config_data["regiao_coords"].split(",")))

        if "imagens_path" in config_data:
            imagens_path = config_data["imagens_path"]
            print("imagens_path: concluído")
        else:
            imagens_path = ""

        pattern = re.compile(r'c\d+\(x=(\d+), y=(\d+)\)')
        caixa_coords = [Coord(int(x), int(y)) for x, y in pattern.findall(config_data["caixa_coords"])]

        window["valor_coords"].update(", ".join(map(str, valor_coords)))
        window["venda_coords"].update(", ".join(map(str, venda_coords)))
        window["regiao_coords"].update(", ".join(map(str, regiao_coords)))
        window["imagens_path"].update(imagens_path)  # Adicione esta linha
        window["caixa_coords"].update(", ".join(f"c{i + 1}(x={c.x}, y={c.y})" for i, c in enumerate(caixa_coords)))

        # Adicione a linha abaixo para exibir as coordenadas carregadas
        print(f"Coordenadas carregadas: valor_coords={valor_coords}, venda_coords={venda_coords}, regiao_coords={regiao_coords}, caixa_coords={caixa_coords}")
        
    except Exception as e:
        print(f"Erro ao carregar as coordenadas do arquivo de configuração: {e}")

def select_item(item):
    global imagens_path, item_image

    if imagens_path is None or item is None:
        print("Caminho das imagens não definido ou item não selecionado.")
        return
    
    item_filename = unidecode(item) + ".png"
    
    item_image_path = os.path.join(imagens_path, f"{unidecode(item)}.png")
    item_image = cv2.imread(item_image_path, cv2.IMREAD_UNCHANGED)
    
    if item_image is None:
        print(f"Imagem do item não encontrada: {item_image_path}")
    else:
        if item_image.shape[2] == 4:
            item_image = cv2.cvtColor(item_image, cv2.COLOR_RGBA2RGB)
        print(f"Imagem do item carregada: {item_image_path}")

def start_process(repetitions, item):
    global regiao_coords, valor_coords, venda_coords, caixa_coords, item_image

    if item_image is None:
        print("A imagem do item não foi carregada.")
        return

    for i in range(repetitions):
        if caixa_coords[i] is None:
            print(f"Coordenadas da caixa {i + 1} não definidas.")
            continue

        pg.click(caixa_coords[i].x, caixa_coords[i].y)
        time.sleep(0.15)  # Adicione esta linha
        screenshot = pg.screenshot(region=regiao_coords)
        screenshot_np = np.array(screenshot)
        screenshot_cv = screenshot_np[:, :, ::-1].copy()

        result = cv2.matchTemplate(screenshot_cv, item_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.9:
            item_position = (regiao_coords[0] + max_loc[0] + item_image.shape[1] // 2, regiao_coords[1] + max_loc[1] + item_image.shape[0] // 2)
            pg.click(item_position[0], item_position[1])
            pg.click(valor_coords[0], valor_coords[1])
            pg.click(venda_coords[0], venda_coords[1])
        else:
            print(f"Item {item} não encontrado na caixa {i + 1}.")
            
def start_process_single_box(box_num, item):
    global regiao_coords, valor_coords, venda_coords, caixa_coords, item_image

    if item_image is None:
        print("A imagem do item não foi carregada.")
        return

    if caixa_coords[box_num - 1] is None:
        print(f"Coordenadas da caixa {box_num} não definidas.")
        return

    pg.click(caixa_coords[box_num - 1].x, caixa_coords[box_num - 1].y)
    time.sleep(0.15)
    screenshot = pg.screenshot(region=regiao_coords)
    screenshot_np = np.array(screenshot)
    screenshot_cv = screenshot_np[:, :, ::-1].copy()

    result = cv2.matchTemplate(screenshot_cv, item_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val > 0.9:
        item_position = (regiao_coords[0] + max_loc[0] + item_image.shape[1] // 2, regiao_coords[1] + max_loc[1] + item_image.shape[0] // 2)
        pg.click(item_position[0], item_position[1])
        pg.click(valor_coords[0], valor_coords[1])
        pg.click(venda_coords[0], venda_coords[1])
    else:
        print(f"Item {item} não encontrado na caixa {box_num}.")

def browse_file():
    file_path = sg.PopupGetFile("Escolha o arquivo de configuração", file_types=(("Text Files", "*.txt"),))
    return file_path

def main():
    
    sg.theme('DarkBlue')
    sg.set_options(element_padding=(0, 10))
    
    layout = [
        [sg.Text("Valor:", font=("Helvetica", 12)), sg.Text("", pad=(5, 0)), sg.Input(key="valor_coords", size=(15, 1)), sg.Text("", pad=(10, 0)), sg.Button("Procurar", key="procurar_valor"), sg.Text("", pad=(5, 0)), sg.Button("Atualizar", key="atualizar_valor")],
        [sg.Text("Venda:", font=("Helvetica", 12)), sg.Text("", pad=(2, 0)), sg.Input(key="venda_coords", size=(15, 1)), sg.Text("", pad=(10, 0)), sg.Button("Procurar", key="procurar_venda"), sg.Text("", pad=(5, 0)), sg.Button("Atualizar", key="atualizar_venda")],
        [sg.Text("Região:", font=("Helvetica", 12)), sg.Input(key="regiao_coords", size=(15, 1)), sg.Text("", pad=(10, 0)), sg.Button("Procurar", key="procurar_regiao"), sg.Text("", pad=(5, 0)), sg.Button("Atualizar", key="atualizar_regiao")],
        [sg.Text("Imagens:", font=("Helvetica", 12)), sg.Input(key="imagens_path", size=(15, 1)), sg.Text("", pad=(10, 0)), sg.FolderBrowse("Procurar", key="procurar_imagens", target="imagens_path"), sg.Text("", pad=(5, 0)), sg.Button("Atualizar", key="atualizar_imagens")],
        [sg.Text("Escolha o item:", font=("Helvetica", 12)), sg.Text("", pad=(5, 0)), sg.Button("Anel"), sg.Text("", pad=(5, 0)), sg.Button("Pernas de Lã"), sg.Text("", pad=(5, 0)), sg.Button("Bacon e Ovos")],
        [sg.Text("Repetições:", font=("Helvetica", 12)), sg.Spin([i for i in range(1, 11)], initial_value=1, key="repeticoes")],
        [sg.Text("Individual:", font=("Helvetica", 12)), sg.Spin([i for i in range(1, 11)], initial_value=1, key="individual"), sg.Text("", pad=(5, 0)), sg.Button("Iniciar Individual", font=("Helvetica", 12))],
        [sg.Text("Caixa Coords:", font=("Helvetica", 12)), sg.Input(key="caixa_coords", size=(30, 1)), sg.Button("Procurar", key="procurar_caixa"), sg.Button("Atualizar", key="atualizar_caixa")],
        [sg.Button("Iniciar", font=("Helvetica", 12)), sg.Text("", pad=(10, 0)), sg.Button("Sair", font=("Helvetica", 12))],
        [sg.Button("Salvar CFG", font=("Helvetica", 12)), sg.Button("Importar CFG", font=("Helvetica", 12)), sg.Text("", pad=(17, 0)), sg.Button("Valor -", font=("Helvetica", 12)), sg.Button("Valor +", font=("Helvetica", 12))],
        [sg.Text("Criado by Iann#1001:", font=("Helvetica", 12))]
    ]
    
    window = sg.Window("@Magodohayday", layout, size=(450, 500))

    item_selected = None
    previous_item_button = None
    file_path = None

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Sair":
            break

        elif event == "procurar_valor":
            window["valor_coords"].update(update_value())

        elif event == "procurar_venda":
            window["venda_coords"].update(update_sale())

        elif event == "procurar_regiao":
            window["regiao_coords"].update(update_region())

        elif event.startswith("procurar_"):
            coord = pg.position()
            window[event.replace("procurar_", "") + "_coords"].update(f"{coord.x}, {coord.y}")

        elif event.startswith("atualizar_"):
            if event == "atualizar_imagens":
                path_key = "imagens_path"
                path = values[path_key]
                update_images(path)
                print(f"O parâmetro {path_key.capitalize()} foi Atualizado")
                window[event].update(button_color=('white', 'green'))
            else:
                coords_key = event.replace("atualizar_", "")
                coords = values[f"{coords_key}_coords"]
                update_coords(coords, coords_key)
                print(f"O parâmetro {coords_key.capitalize()} foi Atualizado")
                window[event].update(button_color=('white', 'green'))

        elif event == "procurar_imagens":
            path = values["imagens_path"]
            update_images(path)

        elif event in ["Anel", "Pernas de Lã", "Bacon e Ovos"]:
            if previous_item_button:
                window[previous_item_button].update(button_color=('white', '#283b5b'))
            item_selected = event
            select_item(event)
            window[event].update(button_color=('white', 'green'))
            print(f"Item {item_selected} selecionado para o processo.")
            previous_item_button = event
            
        if event == "procurar_caixa":
            layout_popup = [
                [sg.Button(f"Caixa {i+1}") for i in range(10)],
            ]
            window_popup = sg.Window("Escolha a caixa", layout_popup)
            while True:
                event_popup, _ = window_popup.read()
                if event_popup in [sg.WIN_CLOSED, "Exit"]:
                    break
                elif event_popup.startswith("Caixa"):
                    caixa_num = int(event_popup.split(" ")[1]) - 1
                    update_caixa_coords(caixa_num)
                    formatted_coords = ' '.join(f"c{i + 1}(x={c.x}, y={c.y})" for i, c in enumerate(caixa_coords) if c is not None)
                    window["caixa_coords"].update(formatted_coords)

        elif event == "atualizar_caixa":
            coords_list = values["caixa_coords"].split(', ')
            for i in range(0, len(coords_list), 2):
                x = int(coords_list[i])
                y = int(coords_list[i + 1])
                caixa_coords[i // 2] = (x, y)
            print("Caixas coordenadas atualizadas.")
            window["atualizar_caixa"].update(button_color=('white', 'green'))
            
        elif event == "Iniciar Individual":
            if item_selected is not None:
                start_process_single_box(int(values["individual"]), item_selected)

        elif event == "Iniciar":
            if item_selected is not None:
                start_process(int(values["repeticoes"]), item_selected)
            else:
                sg.Popup("Por favor, selecione um item antes de iniciar o processo.")
        
        elif event == "Salvar CFG":
            save_method = sg.PopupGetText("Escolha o método", "Escolha o método (Valor - ou Valor +)")
            if save_method in ["Valor -", "Valor +"]:
                file_name = "valormenos.txt" if save_method == "Valor -" else "valormais.txt"
                save_config(file_name)
            else:
                sg.Popup("Método inválido. Por favor, escolha entre 'Valor -' ou 'Valor +'.")

        elif event == "Importar CFG":
            file_path = sg.popup_get_file("Selecione o arquivo de configuração", file_types=(("Text Files", "*.txt"),))
            if file_path:
                load_config(file_path, window)


    window.close()

if __name__ == "__main__":
    main()
