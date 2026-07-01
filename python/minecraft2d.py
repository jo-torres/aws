import pygame
import sys

pygame.init()

ANCHO = 900
ALTO = 600
TAM_BLOQUE = 40

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Minecraft 2D")

reloj = pygame.time.Clock()

CIELO = (120, 190, 255)
PASTO = (80, 180, 80)
TIERRA = (140, 90, 45)
PIEDRA = (120, 120, 120)
JUGADOR = (255, 220, 80)

mundo = []

filas = ALTO // TAM_BLOQUE
columnas = ANCHO // TAM_BLOQUE

for fila in range(filas):
    linea = []
    for columna in range(columnas):
        if fila == 10:
            linea.append("pasto")
        elif fila > 10 and fila < 13:
            linea.append("tierra")
        elif fila >= 13:
            linea.append("piedra")
        else:
            linea.append("aire")
    mundo.append(linea)

jugador = pygame.Rect(100, 100, 30, 50)
vel_x = 0
vel_y = 0
gravedad = 0.8
en_suelo = False

bloque_actual = "tierra"

def color_bloque(tipo):
    if tipo == "pasto":
        return PASTO
    if tipo == "tierra":
        return TIERRA
    if tipo == "piedra":
        return PIEDRA
    return None

def obtener_bloques_solidos():
    bloques = []
    for fila in range(filas):
        for columna in range(columnas):
            if mundo[fila][columna] != "aire":
                rect = pygame.Rect(
                    columna * TAM_BLOQUE,
                    fila * TAM_BLOQUE,
                    TAM_BLOQUE,
                    TAM_BLOQUE
                )
                bloques.append(rect)
    return bloques

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_1:
                bloque_actual = "pasto"
            if evento.key == pygame.K_2:
                bloque_actual = "tierra"
            if evento.key == pygame.K_3:
                bloque_actual = "piedra"

            if evento.key == pygame.K_SPACE and en_suelo:
                vel_y = -15

        if evento.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            columna = x // TAM_BLOQUE
            fila = y // TAM_BLOQUE

            if 0 <= fila < filas and 0 <= columna < columnas:
                if evento.button == 1:
                    mundo[fila][columna] = "aire"

                if evento.button == 3:
                    rect_bloque = pygame.Rect(
                        columna * TAM_BLOQUE,
                        fila * TAM_BLOQUE,
                        TAM_BLOQUE,
                        TAM_BLOQUE
                    )

                    if not rect_bloque.colliderect(jugador):
                        mundo[fila][columna] = bloque_actual

    teclas = pygame.key.get_pressed()

    vel_x = 0

    if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
        vel_x = -5
    if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
        vel_x = 5

    jugador.x += vel_x

    for bloque in obtener_bloques_solidos():
        if jugador.colliderect(bloque):
            if vel_x > 0:
                jugador.right = bloque.left
            elif vel_x < 0:
                jugador.left = bloque.right

    vel_y += gravedad
    jugador.y += vel_y
    en_suelo = False

    for bloque in obtener_bloques_solidos():
        if jugador.colliderect(bloque):
            if vel_y > 0:
                jugador.bottom = bloque.top
                vel_y = 0
                en_suelo = True
            elif vel_y < 0:
                jugador.top = bloque.bottom
                vel_y = 0

    pantalla.fill(CIELO)

    for fila in range(filas):
        for columna in range(columnas):
            tipo = mundo[fila][columna]

            if tipo != "aire":
                rect = pygame.Rect(
                    columna * TAM_BLOQUE,
                    fila * TAM_BLOQUE,
                    TAM_BLOQUE,
                    TAM_BLOQUE
                )

                pygame.draw.rect(pantalla, color_bloque(tipo), rect)
                pygame.draw.rect(pantalla, (80, 80, 80), rect, 1)

    pygame.draw.rect(pantalla, JUGADOR, jugador)

    fuente = pygame.font.SysFont(None, 28)
    texto = fuente.render(
        f"Bloque: {bloque_actual} | 1 Pasto  2 Tierra  3 Piedra | Click izq rompe | Click der coloca",
        True,
        (0, 0, 0)
    )
    pantalla.blit(texto, (15, 15))

    pygame.display.flip()
    reloj.tick(60)