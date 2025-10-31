# morfologia_pura.py
from PIL import Image
import sys

# -------------------------
# Funções auxiliares (puro Python)
# -------------------------

def carregar_imagem_binaria(caminho, limiar=127):
    """
    Lê a imagem com Pillow, converte para escala de cinza e retorna
    uma matriz 2D (lista de listas) com valores 0 ou 1.
    """
    img = Image.open(caminho).convert('L')  # escala de cinza
    largura, altura = img.size
    px = img.load()
    matriz = [[0]*largura for _ in range(altura)]
    for y in range(altura):
        for x in range(largura):
            matriz[y][x] = 1 if px[x, y] > limiar else 0
    return matriz

def salvar_imagem_binaria(matriz, caminho):
    """
    Salva uma matriz 2D (0/1) como imagem (0 -> preto, 1 -> branco).
    """
    altura = len(matriz)
    largura = len(matriz[0]) if altura > 0 else 0
    img = Image.new('L', (largura, altura))
    px = img.load()
    for y in range(altura):
        for x in range(largura):
            px[x, y] = 255 if matriz[y][x] == 1 else 0
    img.save(caminho)

def pad_image(matriz, pad_top, pad_bottom, pad_left, pad_right, pad_value=0):
    """Retorna uma nova matriz com preenchimento (padding)."""
    altura = len(matriz)
    largura = len(matriz[0]) if altura > 0 else 0
    nova_alt = pad_top + altura + pad_bottom
    nova_lar = pad_left + largura + pad_right
    nova = [[pad_value]*nova_lar for _ in range(nova_alt)]
    for y in range(altura):
        for x in range(largura):
            nova[y + pad_top][x + pad_left] = matriz[y][x]
    return nova

# -------------------------
# Elemento estruturante: formato (lista de listas) de 0/1
# Ex.: cruze 3x3:
# B = [
#   [0,1,0],
#   [1,1,1],
#   [0,1,0]
# ]
# -------------------------

def dilatacao(A, B):
    """
    Dilatação morfológica (puro Python).
    A: matriz 2D binária (listas) - formato [linha][coluna]
    B: elemento estruturante (listas 2D) com 0/1
    Retorna nova matriz dilatada (mesmas dimensões de A).
    """
    altura_B = len(B)
    largura_B = len(B[0])
    origem_r = altura_B // 2
    origem_c = largura_B // 2

    pad_top = origem_r
    pad_bottom = altura_B - origem_r - 1
    pad_left = origem_c
    pad_right = largura_B - origem_c - 1

    A_pad = pad_image(A, pad_top, pad_bottom, pad_left, pad_right, pad_value=0)
    altura_A = len(A)
    largura_A = len(A[0]) if altura_A>0 else 0

    saida = [[0]*largura_A for _ in range(altura_A)]

    for r in range(altura_A):
        for c in range(largura_A):
            # subjanela de A_pad com tamanho do ES
            encontrou = False
            for br in range(altura_B):
                if encontrou:
                    break
                for bc in range(largura_B):
                    if B[br][bc] == 1:
                        if A_pad[r + br][c + bc] == 1:
                            encontrou = True
                            break
            if encontrou:
                saida[r][c] = 1
            # else já é zero
    return saida

def erosao(A, B):
    """
    Erosão morfológica (puro Python).
    Todos os pixels do ES que forem 1 devem coincidir com 1 na janela de A.
    """
    altura_B = len(B)
    largura_B = len(B[0])
    origem_r = altura_B // 2
    origem_c = largura_B // 2

    pad_top = origem_r
    pad_bottom = altura_B - origem_r - 1
    pad_left = origem_c
    pad_right = largura_B - origem_c - 1

    A_pad = pad_image(A, pad_top, pad_bottom, pad_left, pad_right, pad_value=0)
    altura_A = len(A)
    if altura_A > 0:
        largura_A = len(A[0])
    else:
        largura_A = 0

    saida = [[0]*largura_A for _ in range(altura_A)]

    for r in range(altura_A):
        for c in range(largura_A):
            cabe = True
            for br in range(altura_B):
                if not cabe:
                    break
                for bc in range(largura_B):
                    if B[br][bc] == 1:
                        if A_pad[r + br][c + bc] != 1:
                            cabe = False
                            break
            if cabe:
                saida[r][c] = 1
    return saida

def abertura(A, B):
    """Abertura = erosão seguida de dilatação"""
    return dilatacao(erosao(A, B), B)

def fechamento(A, B):
    """Fechamento = dilatação seguida de erosão"""
    return erosao(dilatacao(A, B), B)

# -------------------------
# Função utilitária para imprimir progresso simples
# -------------------------
def mostrar_info_operacao(nome):
    print(f"[INFO] Executando: {nome}")

# -------------------------
# Exemplo de uso (main)
# -------------------------
if __name__ == "__main__":
    # Caminho fixo da imagem dentro da pasta "imagens"
    caminho = "imagens/masqueico.jpg"
    print(f"Carregando e binarizando: {caminho}")
    img = carregar_imagem_binaria(caminho, limiar=127)

    # Defina aqui o elemento estruturante (ex.: cruze 3x3)
    B = [[0,1,0],
         [1,1,1],
         [0,1,0]]
    
    #Quadrado 3x3 Expansão/contração em todas as direções, mais suave.
    # B = [[1,1,1],
    #      [1,1,1],
    #      [1,1,1]]
    # Linha horizontal Afeta somente no eixo X.
    # B = [[0,0,0],
    #      [1,1,1],
    #      [0,0,0]]
    
    # Linha vertical Afeta somente no eixo Y.
    # B = [[0,1,0],
    #      [0,1,0],
    #      [0,1,0]]

    mostrar_info_operacao("Dilatação")
    dil = dilatacao(img, B)
    salvar_imagem_binaria(dil, "imagens/resultado_dilatacao.jpg")
    print("  -> resultado_dilatacao.png salvo.")

    mostrar_info_operacao("Erosão")
    ero = erosao(img, B)
    salvar_imagem_binaria(ero, "imagens/resultado_erosao.jpg")
    print("  -> resultado_erosao.png salvo.")

    mostrar_info_operacao("Abertura")
    abi = abertura(img, B)
    salvar_imagem_binaria(abi, "imagens/resultado_abertura.jpg")
    print("  -> resultado_abertura.png salvo.")

    mostrar_info_operacao("Fechamento")
    fec = fechamento(img, B)
    salvar_imagem_binaria(fec, "imagens/resultado_fechamento.jpg")
    print("  -> resultado_fechamento.png salvo.")

    print("Processamento concluído. Verifique os arquivos gerados.")
