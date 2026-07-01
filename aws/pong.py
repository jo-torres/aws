import pygame
import sys

pygame.init()

ANCHO = 800
ALTO = 500

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pong")

reloj = pygame.time.Clock()

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

paleta_ancho = 15
paleta_alto = 100

jugador = pygame.Rect(30, ALTO // 2 - 50, paleta_ancho, paleta_alto)
cpu = pygame.Rect(ANCHO - 45, ALTO // 2 - 50, paleta_ancho, paleta_alto)

pelota = pygame.Rect(ANCHO // 2 - 10, ALTO // 2 - 10, 20, 20)

vel_jugador = 0
vel_cpu = 5

vel_pelota_x = 5
vel_pelota_y = 5

puntaje_jugador = 0
puntaje_cpu = 0

fuente = pygame.font.SysFont(None, 50)

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                vel_jugador = -6
            if evento.key == pygame.K_DOWN:
                vel_jugador = 6

        if evento.type == pygame.KEYUP:
            if evento.key in (pygame.K_UP, pygame.K_DOWN):
                vel_jugador = 0

    jugador.y += vel_jugador

    if jugador.top < 0:
        jugador.top = 0
    if jugador.bottom > ALTO:
        jugador.bottom = ALTO

    if cpu.centery < pelota.centery:
        cpu.y += vel_cpu
    if cpu.centery > pelota.centery:
        cpu.y -= vel_cpu

    if cpu.top < 0:
        cpu.top = 0
    if cpu.bottom > ALTO:
        cpu.bottom = ALTO

    pelota.x += vel_pelota_x
    pelota.y += vel_pelota_y

    if pelota.top <= 0 or pelota.bottom >= ALTO:
        vel_pelota_y *= -1

    if pelota.colliderect(jugador) or pelota.colliderect(cpu):
        vel_pelota_x *= -1

    if pelota.left <= 0:
        puntaje_cpu += 1
        pelota.center = (ANCHO // 2, ALTO // 2)
        vel_pelota_x *= -1

    if pelota.right >= ANCHO:
        puntaje_jugador += 1
        pelota.center = (ANCHO // 2, ALTO // 2)
        vel_pelota_x *= -1

    pantalla.fill(NEGRO)

    pygame.draw.rect(pantalla, BLANCO, jugador)
    pygame.draw.rect(pantalla, BLANCO, cpu)
    pygame.draw.ellipse(pantalla, BLANCO, pelota)
    pygame.draw.aaline(pantalla, BLANCO, (ANCHO // 2, 0), (ANCHO // 2, ALTO))

    texto = fuente.render(f"{puntaje_jugador}   {puntaje_cpu}", True, BLANCO)
    pantalla.blit(texto, (ANCHO // 2 - 60, 20))

    pygame.display.flip()
    reloj.tick(60)