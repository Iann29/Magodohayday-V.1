# Magodohayday V.1

O código apresentado é um script em Python que utiliza as bibliotecas PySimpleGUI, pyautogui, os, keyboard, re, cv2, numpy, time, collections e unidecode para criar uma interface gráfica e automatizar ações no jogo Hay Day, O objetivo do script é identificar itens específicos em caixas do jogo e realizar ações de venda de itens com base na posição do item na tela.

A interface gráfica permite ao usuário definir as coordenadas dos campos de valor, venda e região do jogo, assim como o caminho para as imagens dos itens que serão usadas para a identificação. O usuário também pode salvar e importar arquivos de configuração contendo as coordenadas e o caminho das imagens.

O script possui funções para atualizar e salvar as coordenadas, carregar configurações, selecionar um item, iniciar o processo de venda para todas as caixas ou apenas uma caixa específica e navegar até um arquivo de configuração. Além disso, a interface gráfica fornece botões para realizar essas ações e exibir informações relacionadas.



# English

The code snippet provided is a Python script used to automate some game-related tasks. It uses libraries like PySimpleGUI, pyautogui, os, keyboard, re, cv2, numpy, time, collections, and unidecode to perform its functions. The script has several components, such as updating coordinates, selecting items, and starting the automation process.

The script allows users to update the coordinates of various game elements, such as the value, sale, and region, by clicking on the respective buttons. Users can also update the path of the images folder to use for image recognition. The program saves and loads configuration files that contain the settings, making it easy for users to reuse their configurations.

The automation process involves searching for a specific item in the game and performing actions such as clicking on the item, its value, and its sale. Users can select the item to automate, and the program will use image recognition to find it within the specified region. The script supports processing multiple game boxes, and users can set the number of repetitions to perform the automation process.

Overall, this script helps users automate repetitive tasks in a game, saving time and effort.
