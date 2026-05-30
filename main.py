import pygame
import random
import sys
import math
import array

pygame.init()

# =========================
# CONFIGURACIÓN GENERAL
# =========================
ANCHO = 1200
ALTO = 760
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Casino Cards - Mayor o Menor")

RELOJ = pygame.time.Clock()
FPS = 60

# =========================
# COLORES
# =========================
VERDE_FONDO = (6, 55, 34)
VERDE_MESA = (9, 95, 54)
VERDE_PANEL = (5, 45, 28)

DORADO = (224, 184, 68)
DORADO_CLARO = (255, 220, 120)
DORADO_OSCURO = (130, 100, 30)

BLANCO = (245, 245, 245)
NEGRO = (20, 20, 20)
ROJO = (205, 35, 45)

AZUL = (35, 95, 220)
AZUL_HOVER = (65, 125, 255)
ROJO_BOTON = (190, 45, 45)
ROJO_HOVER = (230, 70, 70)
GRIS = (90, 90, 90)
GRIS_HOVER = (130, 130, 130)

# =========================
# FUENTES
# =========================
FUENTE_LOGO = pygame.font.SysFont("georgia", 54, bold=True)
FUENTE_TITULO = pygame.font.SysFont("georgia", 44, bold=True)
FUENTE_SUBTITULO = pygame.font.SysFont("georgia", 28, bold=True)
FUENTE_MEDIA = pygame.font.SysFont("arial", 25, bold=True)
FUENTE_NORMAL = pygame.font.SysFont("arial", 21)
FUENTE_PEQUENA = pygame.font.SysFont("arial", 17)
FUENTE_CARTA_GRANDE = pygame.font.SysFont("timesnewroman", 72, bold=True)
FUENTE_CARTA_MEDIA = pygame.font.SysFont("timesnewroman", 36, bold=True)
FUENTE_SIMBOLO = pygame.font.SysFont("segoe ui symbol", 46, bold=True)

# =========================
# ESTADOS
# =========================
MENU = "menu"
CONFIG = "config"
JUGANDO = "jugando"
ANIMANDO = "animando"
FINAL = "final"

estado = MENU

# =========================
# DATOS DEL JUEGO
# =========================
PALOS = ["♥", "♦", "♣", "♠"]
VALORES = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]

cantidad_jugadores = 2
tipos_jugadores = ["humano", "pc", "pc", "pc"]
nombres_jugadores = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]
nombre_activo = None

jugadores = []
jugador_actual = 0
ronda = 1
max_rondas = 5

baraja = []
carta_actual = None
siguiente_carta = None

mensaje = "Bienvenido"
mostrar_siguiente = False
esperando_click = True

animacion_progreso = 0
resultado_turno = None
eleccion_turno = None

# =========================
# SONIDOS
# =========================
sonido_acierto = None
sonido_fallo = None


def crear_sonido(frecuencia=440, duracion=0.18, volumen=0.4):
    sample_rate = 44100
    cantidad_muestras = int(sample_rate * duracion)
    buffer = array.array("h")

    for i in range(cantidad_muestras):
        tiempo = i / sample_rate
        onda = math.sin(2 * math.pi * frecuencia * tiempo)
        valor = int(onda * 32767 * volumen)
        buffer.append(valor)

    return pygame.mixer.Sound(buffer=buffer)


try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    sonido_acierto = crear_sonido(760, 0.18, 0.35)
    sonido_fallo = crear_sonido(180, 0.25, 0.35)
except pygame.error:
    sonido_acierto = None
    sonido_fallo = None


def reproducir_sonido_acierto():
    if sonido_acierto:
        sonido_acierto.play()


def reproducir_sonido_fallo():
    if sonido_fallo:
        sonido_fallo.play()


# =========================
# UTILIDADES
# =========================
def dibujar_texto(texto, fuente, color, x, y, centrado=True):
    superficie = fuente.render(str(texto), True, color)
    rect = superficie.get_rect()

    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    VENTANA.blit(superficie, rect)


def color_palo(palo):
    if palo in ["♥", "♦"]:
        return ROJO
    return NEGRO


def valor_numerico(carta):
    valor = carta["valor"]

    if valor == "J":
        return 11
    if valor == "Q":
        return 12
    if valor == "K":
        return 13
    if valor == "A":
        return 14

    return valor


def crear_baraja():
    nueva_baraja = []

    for palo in PALOS:
        for valor in VALORES:
            nueva_baraja.append({
                "valor": valor,
                "palo": palo
            })

    random.shuffle(nueva_baraja)
    return nueva_baraja


# =========================
# DISEÑO CASINO
# =========================
def dibujar_fondo_casino():
    VENTANA.fill(VERDE_FONDO)

    # Marco exterior
    pygame.draw.rect(VENTANA, DORADO_OSCURO, (20, 20, ANCHO - 40, ALTO - 40), 6, border_radius=32)
    pygame.draw.rect(VENTANA, DORADO, (32, 32, ANCHO - 64, ALTO - 64), 3, border_radius=28)

    # Mesa
    pygame.draw.rect(VENTANA, VERDE_MESA, (70, 80, ANCHO - 140, ALTO - 140), border_radius=40)
    pygame.draw.rect(VENTANA, DORADO, (70, 80, ANCHO - 140, ALTO - 140), 3, border_radius=40)

    # Líneas decorativas
    pygame.draw.arc(VENTANA, DORADO_OSCURO, (260, 455, 680, 170), 3.4, 6.0, 4)
    pygame.draw.arc(VENTANA, DORADO, (280, 470, 640, 140), 3.4, 6.0, 2)


def dibujar_panel(x, y, ancho, alto):
    sombra = pygame.Rect(x + 8, y + 10, ancho, alto)
    pygame.draw.rect(VENTANA, (0, 0, 0), sombra, border_radius=28)

    rect = pygame.Rect(x, y, ancho, alto)
    pygame.draw.rect(VENTANA, VERDE_PANEL, rect, border_radius=28)
    pygame.draw.rect(VENTANA, DORADO, rect, 3, border_radius=28)


def dibujar_logo(x, y):
    # Emblema izquierdo con trébol
    pygame.draw.circle(VENTANA, DORADO_OSCURO, (x, y), 54)
    pygame.draw.circle(VENTANA, DORADO, (x, y), 48)
    pygame.draw.circle(VENTANA, VERDE_PANEL, (x, y), 39)

    dibujar_texto("♣", FUENTE_SIMBOLO, BLANCO, x, y - 3)

    # Emblema derecho con diamante
    x_derecha = ANCHO - x

    pygame.draw.circle(VENTANA, DORADO_OSCURO, (x_derecha, y), 54)
    pygame.draw.circle(VENTANA, DORADO, (x_derecha, y), 48)
    pygame.draw.circle(VENTANA, VERDE_PANEL, (x_derecha, y), 39)

    dibujar_texto("♦", FUENTE_SIMBOLO, ROJO, x_derecha, y - 3)

    # Texto central del logo
    dibujar_texto("CASINO CARDS", FUENTE_TITULO, BLANCO, ANCHO // 2, y - 10)
    dibujar_texto("Mayor o Menor", FUENTE_SUBTITULO, DORADO_CLARO, ANCHO // 2, y + 34)


# =========================
# BOTÓN
# =========================
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_hover, color_texto=BLANCO):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover
        self.color_texto = color_texto

    def dibujar(self):
        mouse = pygame.mouse.get_pos()
        encima = self.rect.collidepoint(mouse)
        color = self.color_hover if encima else self.color

        sombra = self.rect.move(0, 6)
        pygame.draw.rect(VENTANA, (0, 0, 0), sombra, border_radius=18)

        pygame.draw.rect(VENTANA, color, self.rect, border_radius=18)
        pygame.draw.rect(VENTANA, DORADO, self.rect, 2, border_radius=18)

        if encima:
            pygame.draw.rect(VENTANA, DORADO_CLARO, self.rect, 2, border_radius=18)

        dibujar_texto(self.texto, FUENTE_NORMAL, self.color_texto, self.rect.centerx, self.rect.centery)

    def click(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)
# =========================
# CAJA DE TEXTO PARA NOMBRES
# =========================
class CajaTexto:
    def __init__(self, x, y, ancho, alto, texto=""):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.activa = False

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            self.activa = self.rect.collidepoint(evento.pos)

        if evento.type == pygame.KEYDOWN and self.activa:
            if evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif evento.key == pygame.K_RETURN:
                self.activa = False
            else:
                if len(self.texto) < 12:
                    self.texto += evento.unicode

    def dibujar(self):
        color_borde = DORADO_CLARO if self.activa else DORADO_OSCURO

        pygame.draw.rect(VENTANA, (8, 65, 40), self.rect, border_radius=10)
        pygame.draw.rect(VENTANA, color_borde, self.rect, 2, border_radius=10)

        texto_mostrar = self.texto
        if self.activa:
            texto_mostrar += "|"

        dibujar_texto(texto_mostrar, FUENTE_PEQUENA, BLANCO, self.rect.x + 10, self.rect.y + 9, centrado=False)

# =========================
# CARTAS MEJORADAS
# =========================
def dibujar_carta(carta, x, y, visible=True, escala_x=1.0):
    ancho_base = 170
    alto = 245
    ancho = max(8, int(ancho_base * escala_x))

    x_centro = x + ancho_base // 2
    x_real = x_centro - ancho // 2

    rect = pygame.Rect(x_real, y, ancho, alto)

    # sombra
    pygame.draw.rect(VENTANA, (0, 0, 0), (x_real + 8, y + 10, ancho, alto), border_radius=18)

    # cuando la carta se está volteando y queda muy delgada
    if escala_x < 0.15:
        pygame.draw.rect(VENTANA, DORADO, rect, border_radius=18)
        return

    if visible and carta is not None:
        # base de la carta
        pygame.draw.rect(VENTANA, (248, 248, 245), rect, border_radius=18)
        pygame.draw.rect(VENTANA, NEGRO, rect, 2, border_radius=18)

        # doble borde elegante
        borde1 = pygame.Rect(x_real + 8, y + 8, ancho - 16, alto - 16)
        borde2 = pygame.Rect(x_real + 14, y + 14, ancho - 28, alto - 28)

        pygame.draw.rect(VENTANA, DORADO, borde1, 2, border_radius=14)
        pygame.draw.rect(VENTANA, (225, 225, 225), borde2, 1, border_radius=12)

        valor = str(carta["valor"])
        palo = carta["palo"]
        color = color_palo(palo)

        if ancho > 80:
            # decoración central elegante
            pygame.draw.circle(VENTANA, (242, 242, 242), (x_real + ancho // 2, y + alto // 2), 46)
            pygame.draw.circle(VENTANA, DORADO, (x_real + ancho // 2, y + alto // 2), 46, 2)

            # valor y palo arriba izquierda
            dibujar_texto(valor, FUENTE_CARTA_MEDIA, color, x_real + 28, y + 28)
            dibujar_texto(palo, FUENTE_CARTA_MEDIA, color, x_real + 28, y + 62)

            # símbolo grande central
            dibujar_texto(palo, FUENTE_CARTA_GRANDE, color, x_real + ancho // 2, y + alto // 2 + 3)

            # valor y palo abajo derecha
            dibujar_texto(valor, FUENTE_CARTA_MEDIA, color, x_real + ancho - 28, y + alto - 62)
            dibujar_texto(palo, FUENTE_CARTA_MEDIA, color, x_real + ancho - 28, y + alto - 28)

            # detalle decorativo horizontal
            pygame.draw.line(
                VENTANA,
                DORADO,
                (x_real + 42, y + alto // 2 + 55),
                (x_real + ancho - 42, y + alto // 2 + 55),
                2
            )

    else:
        # reverso premium de la carta
        pygame.draw.rect(VENTANA, (13, 35, 110), rect, border_radius=18)
        pygame.draw.rect(VENTANA, BLANCO, rect, 2, border_radius=18)

        borde1 = pygame.Rect(x_real + 8, y + 8, ancho - 16, alto - 16)
        borde2 = pygame.Rect(x_real + 16, y + 16, ancho - 32, alto - 32)
        borde3 = pygame.Rect(x_real + 25, y + 25, ancho - 50, alto - 50)

        pygame.draw.rect(VENTANA, DORADO, borde1, 2, border_radius=14)
        pygame.draw.rect(VENTANA, DORADO_CLARO, borde2, 1, border_radius=12)
        pygame.draw.rect(VENTANA, (35, 75, 170), borde3, 2, border_radius=10)

        if ancho > 80:
            cx = x_real + ancho // 2
            cy = y + alto // 2

            # patrón elegante
            for fila in range(7):
                for col in range(4):
                    px = x_real + 28 + col * 38
                    py = y + 35 + fila * 28

                    if px < x_real + ancho - 20:
                        pygame.draw.circle(VENTANA, DORADO_CLARO, (px, py), 2)
                        pygame.draw.circle(VENTANA, BLANCO, (px, py), 5, 1)

            # medallón central
            pygame.draw.circle(VENTANA, (8, 25, 85), (cx, cy), 46)
            pygame.draw.circle(VENTANA, DORADO, (cx, cy), 46, 3)
            pygame.draw.circle(VENTANA, DORADO_CLARO, (cx, cy), 34, 1)

            # símbolo central
            dibujar_texto("♠", FUENTE_SIMBOLO, BLANCO, cx, cy - 3)

            # diamantes decorativos
            diamante_arriba = [
                (cx, y + 45),
                (cx + 12, y + 57),
                (cx, y + 69),
                (cx - 12, y + 57)
            ]

            diamante_abajo = [
                (cx, y + alto - 69),
                (cx + 12, y + alto - 57),
                (cx, y + alto - 45),
                (cx - 12, y + alto - 57)
            ]

            pygame.draw.polygon(VENTANA, DORADO, diamante_arriba, 2)
            pygame.draw.polygon(VENTANA, DORADO, diamante_abajo, 2)

            dibujar_texto("CASINO", FUENTE_PEQUENA, BLANCO, cx, y + 82)
            dibujar_texto("CARDS", FUENTE_PEQUENA, BLANCO, cx, y + alto - 82)


# =========================
# LÓGICA DEL JUEGO
# =========================
def crear_jugadores():
    global jugadores

    jugadores = []

    for i in range(cantidad_jugadores):
        tipo = tipos_jugadores[i]
        nombre = nombres_jugadores[i].strip()

        if nombre == "":
            if tipo == "humano":
                nombre = f"Jugador {i + 1}"
            else:
                nombre = f"PC {i + 1}"

        jugadores.append({
            "nombre": nombre,
            "tipo": tipo,
            "puntaje": 0
        })

def iniciar_juego():
    global baraja, carta_actual, siguiente_carta
    global jugador_actual, ronda, mensaje, mostrar_siguiente, esperando_click
    global animacion_progreso, resultado_turno, eleccion_turno

    crear_jugadores()

    baraja = crear_baraja()
    carta_actual = baraja.pop()
    siguiente_carta = None

    jugador_actual = 0
    ronda = 1
    mostrar_siguiente = False
    esperando_click = True

    animacion_progreso = 0
    resultado_turno = None
    eleccion_turno = None

    mensaje = f"Turno de {jugadores[jugador_actual]['nombre']}"


def elegir_pc():
    valor = valor_numerico(carta_actual)

    if valor <= 7:
        return "mayor"
    if valor >= 10:
        return "menor"

    return random.choice(["mayor", "menor"])


def preparar_turno(eleccion):
    global siguiente_carta, estado
    global animacion_progreso, eleccion_turno, resultado_turno

    if len(baraja) == 0:
        estado = FINAL
        return

    siguiente_carta = baraja.pop()
    eleccion_turno = eleccion
    resultado_turno = None
    animacion_progreso = 0
    estado = ANIMANDO


def procesar_resultado_turno():
    global resultado_turno, mensaje, esperando_click, mostrar_siguiente

    va = valor_numerico(carta_actual)
    vs = valor_numerico(siguiente_carta)

    acierto = False

    if eleccion_turno == "mayor" and vs > va:
        acierto = True
    elif eleccion_turno == "menor" and vs < va:
        acierto = True

    jugador = jugadores[jugador_actual]

    if acierto:
        jugador["puntaje"] += 1
        mensaje = f"{jugador['nombre']} eligió {eleccion_turno.upper()} y acertó"
        reproducir_sonido_acierto()
    else:
        mensaje = f"{jugador['nombre']} eligió {eleccion_turno.upper()} y falló"
        reproducir_sonido_fallo()

    resultado_turno = acierto
    mostrar_siguiente = True
    esperando_click = False


def siguiente_turno():
    global carta_actual, siguiente_carta
    global jugador_actual, ronda, estado
    global mensaje, mostrar_siguiente, esperando_click
    global resultado_turno, eleccion_turno

    carta_actual = siguiente_carta
    siguiente_carta = None
    mostrar_siguiente = False

    jugador_actual += 1

    if jugador_actual >= len(jugadores):
        jugador_actual = 0
        ronda += 1

    if ronda > max_rondas:
        estado = FINAL
        return

    resultado_turno = None
    eleccion_turno = None

    mensaje = f"Turno de {jugadores[jugador_actual]['nombre']}"
    esperando_click = True
    estado = JUGANDO


def obtener_ganadores():
    mejor = max(jugador["puntaje"] for jugador in jugadores)
    ganadores = []

    for jugador in jugadores:
        if jugador["puntaje"] == mejor:
            ganadores.append(jugador["nombre"])

    return ganadores, mejor


# =========================
# BOTONES
# =========================
boton_jugar = Boton(400, 585, 180, 58, "JUGAR", AZUL, AZUL_HOVER)
boton_salir = Boton(620, 585, 180, 58, "SALIR", ROJO_BOTON, ROJO_HOVER)

# Botones para cantidad de jugadores
boton_menos = Boton(390, 285, 60, 48, "-", GRIS, GRIS_HOVER)
boton_mas = Boton(750, 285, 60, 48, "+", GRIS, GRIS_HOVER)

# Botones para cantidad de rondas
boton_menos_rondas = Boton(390, 360, 60, 48, "-", GRIS, GRIS_HOVER)
boton_mas_rondas = Boton(750, 360, 60, 48, "+", GRIS, GRIS_HOVER)

boton_empezar = Boton(400, 650, 180, 58, "EMPEZAR", AZUL, AZUL_HOVER)
boton_volver = Boton(620, 650, 180, 58, "VOLVER", ROJO_BOTON, ROJO_HOVER)

boton_mayor = Boton(405, 650, 180, 58, "MAYOR", AZUL, AZUL_HOVER)
boton_menor = Boton(615, 650, 180, 58, "MENOR", ROJO_BOTON, ROJO_HOVER)
boton_continuar = Boton(500, 650, 200, 58, "CONTINUAR", (180, 130, 25), (225, 170, 35))

boton_menu = Boton(500, 650, 200, 58, "MENÚ", AZUL, AZUL_HOVER)

botones_tipo = []
cajas_nombre = []


def actualizar_botones_tipo():
    global botones_tipo, cajas_nombre

    botones_tipo = []
    cajas_nombre = []

    y_inicial = 470

    for i in range(4):
        y = y_inicial + i * 40

        boton = Boton(680, y - 10, 130, 34, tipos_jugadores[i].upper(), AZUL, AZUL_HOVER)
        botones_tipo.append(boton)

        caja = CajaTexto(470, y - 10, 180, 34, nombres_jugadores[i])
        cajas_nombre.append(caja)

actualizar_botones_tipo()


# =========================
# PANTALLAS
# =========================
def pantalla_menu(eventos):
    global estado

    dibujar_fondo_casino()
    dibujar_logo(210, 155)

    dibujar_panel(170, 225, 860, 405)

    dibujar_carta({"valor": "A", "palo": "♠"}, 330, 310, True)
    dibujar_carta({"valor": "K", "palo": "♥"}, 700, 310, True)

    dibujar_texto("Elige si la próxima carta será mayor o menor", FUENTE_MEDIA, BLANCO, ANCHO // 2, 275)
    dibujar_texto("Modo casino multijugador", FUENTE_NORMAL, DORADO_CLARO, ANCHO // 2, 555)

    boton_jugar.dibujar()
    boton_salir.dibujar()

    for evento in eventos:
        if boton_jugar.click(evento):
            estado = CONFIG
        elif boton_salir.click(evento):
            pygame.quit()
            sys.exit()


def pantalla_config(eventos):
    global estado, cantidad_jugadores, max_rondas

    dibujar_fondo_casino()
    dibujar_logo(210, 115)

    dibujar_panel(170, 190, 860, 520)

    dibujar_texto("CONFIGURACIÓN DE PARTIDA", FUENTE_SUBTITULO, DORADO_CLARO, ANCHO // 2, 225)

    # Cantidad de jugadores
    dibujar_texto("Cantidad de jugadores", FUENTE_NORMAL, BLANCO, ANCHO // 2, 270)

    boton_menos.dibujar()
    boton_mas.dibujar()

    dibujar_texto(str(cantidad_jugadores), FUENTE_TITULO, DORADO_CLARO, ANCHO // 2, 310)

    # Cantidad de rondas
    dibujar_texto("Cantidad de rondas", FUENTE_NORMAL, BLANCO, ANCHO // 2, 345)

    boton_menos_rondas.dibujar()
    boton_mas_rondas.dibujar()

    dibujar_texto(str(max_rondas), FUENTE_TITULO, DORADO_CLARO, ANCHO // 2, 385)

    pygame.draw.line(VENTANA, DORADO_OSCURO, (300, 425), (900, 425), 2)

    # Encabezados
    dibujar_texto("Jugador", FUENTE_PEQUENA, DORADO_CLARO, 355, 445, centrado=False)
    dibujar_texto("Nombre", FUENTE_PEQUENA, DORADO_CLARO, 550, 445, centrado=True)
    dibujar_texto("Tipo", FUENTE_PEQUENA, DORADO_CLARO, 745, 445, centrado=True)

    y_inicio = 470
    espacio = 40

    for i in range(4):
        y = y_inicio + i * espacio

        activo = i < cantidad_jugadores

        if activo:
            color_nombre = BLANCO
            color_fondo = (8, 65, 40)
            color_borde = DORADO_OSCURO
        else:
            color_nombre = (110, 110, 110)
            color_fondo = (20, 45, 35)
            color_borde = (70, 70, 70)

        pygame.draw.rect(
            VENTANA,
            color_fondo,
            (330, y - 12, 540, 36),
            border_radius=12
        )

        pygame.draw.rect(
            VENTANA,
            color_borde,
            (330, y - 12, 540, 36),
            1,
            border_radius=12
        )

        dibujar_texto(
            f"Jugador {i + 1}",
            FUENTE_PEQUENA,
            color_nombre,
            355,
            y - 2,
            centrado=False
        )

        if activo:
            cajas_nombre[i].rect.topleft = (470, y - 10)
            cajas_nombre[i].dibujar()

            botones_tipo[i].rect.topleft = (680, y - 10)
            botones_tipo[i].texto = tipos_jugadores[i].upper()
            botones_tipo[i].dibujar()
        else:
            dibujar_texto("INACTIVO", FUENTE_PEQUENA, color_nombre, 745, y + 5)

    boton_empezar.dibujar()
    boton_volver.dibujar()

    for evento in eventos:
        for i in range(cantidad_jugadores):
            cajas_nombre[i].manejar_evento(evento)
            nombres_jugadores[i] = cajas_nombre[i].texto

        if boton_menos.click(evento) and cantidad_jugadores > 2:
            cantidad_jugadores -= 1

        elif boton_mas.click(evento) and cantidad_jugadores < 4:
            cantidad_jugadores += 1

        elif boton_menos_rondas.click(evento) and max_rondas > 1:
            max_rondas -= 1

        elif boton_mas_rondas.click(evento) and max_rondas < 20:
            max_rondas += 1

        elif boton_empezar.click(evento):
            iniciar_juego()
            estado = JUGANDO

        elif boton_volver.click(evento):
            estado = MENU

        for i in range(cantidad_jugadores):
            if botones_tipo[i].click(evento):
                if tipos_jugadores[i] == "humano":
                    tipos_jugadores[i] = "pc"
                else:
                    tipos_jugadores[i] = "humano"


def dibujar_panel_puntajes():
    pygame.draw.rect(VENTANA, (0, 0, 0), (100, 235, 245, 300), border_radius=24)
    pygame.draw.rect(VENTANA, VERDE_PANEL, (92, 225, 245, 300), border_radius=24)
    pygame.draw.rect(VENTANA, DORADO, (92, 225, 245, 300), 2, border_radius=24)

    dibujar_texto("PUNTAJES", FUENTE_MEDIA, DORADO_CLARO, 215, 260)

    for i, jugador in enumerate(jugadores):
        y = 305 + i * 48

        if i == jugador_actual:
            pygame.draw.rect(VENTANA, (40, 95, 55), (115, y - 18, 195, 36), border_radius=12)
            pygame.draw.rect(VENTANA, DORADO, (115, y - 18, 195, 36), 1, border_radius=12)

        texto = f"{jugador['nombre']}: {jugador['puntaje']}"
        color = DORADO_CLARO if i == jugador_actual else BLANCO
        dibujar_texto(texto, FUENTE_NORMAL, color, 130, y - 12, centrado=False)


def dibujar_encabezado_juego(subtitulo):
    pygame.draw.rect(VENTANA, (0, 0, 0), (365, 70, 470, 110), border_radius=24)
    pygame.draw.rect(VENTANA, VERDE_PANEL, (357, 62, 470, 110), border_radius=24)
    pygame.draw.rect(VENTANA, DORADO, (357, 62, 470, 110), 2, border_radius=24)

    dibujar_texto("CASINO CARDS", FUENTE_TITULO, BLANCO, ANCHO // 2, 95)
    dibujar_texto(subtitulo, FUENTE_SUBTITULO, DORADO_CLARO, ANCHO // 2, 135)
    for i, jugador in enumerate(jugadores):
        y = 280 + i * 48

        if i == jugador_actual:
            pygame.draw.rect(VENTANA, (40, 95, 55), (115, y - 18, 195, 36), border_radius=12)
            pygame.draw.rect(VENTANA, DORADO, (115, y - 18, 195, 36), 1, border_radius=12)

        texto = f"{jugador['nombre']}: {jugador['puntaje']}"
        color = DORADO_CLARO if i == jugador_actual else BLANCO
        dibujar_texto(texto, FUENTE_NORMAL, color, 130, y - 12, centrado=False)


def dibujar_tablero_juego():
    dibujar_fondo_casino()

    # encabezado nuevo, más ordenado
    dibujar_encabezado_juego(f"RONDA {ronda} DE {max_rondas}")
    dibujar_texto(mensaje, FUENTE_MEDIA, BLANCO, ANCHO // 2, 190)

    # paneles
    dibujar_panel(370, 225, 500, 380)
    dibujar_panel_puntajes()

    # títulos de cartas
    dibujar_texto("Carta actual", FUENTE_NORMAL, BLANCO, 510, 255)
    dibujar_texto("Siguiente carta", FUENTE_NORMAL, BLANCO, 730, 255)

    # cartas
    dibujar_carta(carta_actual, 425, 295, True)
    dibujar_carta(siguiente_carta, 645, 295, mostrar_siguiente)


def pantalla_juego(eventos):
    dibujar_tablero_juego()

    jugador = jugadores[jugador_actual]

    if esperando_click:
        if jugador["tipo"] == "humano":
            boton_mayor.dibujar()
            boton_menor.dibujar()

            for evento in eventos:
                if boton_mayor.click(evento):
                    preparar_turno("mayor")
                elif boton_menor.click(evento):
                    preparar_turno("menor")
        else:
            pygame.time.delay(700)
            eleccion = elegir_pc()
            preparar_turno(eleccion)
    else:
        boton_continuar.dibujar()

        for evento in eventos:
            if boton_continuar.click(evento):
                siguiente_turno()

def pantalla_animacion():
    global animacion_progreso, estado, mostrar_siguiente

    dibujar_fondo_casino()

    # encabezado nuevo, más ordenado
    dibujar_encabezado_juego(f"RONDA {ronda} DE {max_rondas}")
    dibujar_texto(
        f"{jugadores[jugador_actual]['nombre']} eligió {eleccion_turno.upper()}",
        FUENTE_MEDIA,
        BLANCO,
        ANCHO // 2,
        190
    )

    # paneles
    dibujar_panel(370, 225, 500, 380)
    dibujar_panel_puntajes()

    # títulos
    dibujar_texto("Carta actual", FUENTE_NORMAL, BLANCO, 510, 255)
    dibujar_texto("Siguiente carta", FUENTE_NORMAL, BLANCO, 730, 255)

    # carta actual
    dibujar_carta(carta_actual, 425, 295, True)

    # animación de volteo
    animacion_progreso += 0.045

    if animacion_progreso < 0.5:
        escala = 1 - animacion_progreso * 2
        dibujar_carta(None, 645, 295, False, escala)
    else:
        escala = (animacion_progreso - 0.5) * 2
        dibujar_carta(siguiente_carta, 645, 295, True, escala)

    if animacion_progreso >= 1:
        animacion_progreso = 1
        mostrar_siguiente = True
        procesar_resultado_turno()
        estado = JUGANDO


def pantalla_final(eventos):
    global estado

    dibujar_fondo_casino()
    dibujar_logo(210, 135)
    dibujar_panel(220, 230, 760, 380)

    ganadores, puntos = obtener_ganadores()

    dibujar_texto("FIN DEL JUEGO", FUENTE_TITULO, BLANCO, ANCHO // 2, 270)

    if len(ganadores) == 1:
        dibujar_texto(f"Ganador: {ganadores[0]}", FUENTE_SUBTITULO, DORADO_CLARO, ANCHO // 2, 335)
    else:
        dibujar_texto("Empate entre:", FUENTE_SUBTITULO, DORADO_CLARO, ANCHO // 2, 335)
        dibujar_texto(", ".join(ganadores), FUENTE_NORMAL, BLANCO, ANCHO // 2, 375)

    dibujar_texto(f"Puntaje ganador: {puntos}", FUENTE_MEDIA, BLANCO, ANCHO // 2, 415)

    y = 465
    for jugador in jugadores:
        dibujar_texto(f"{jugador['nombre']}: {jugador['puntaje']} puntos", FUENTE_NORMAL, BLANCO, ANCHO // 2, y)
        y += 32

    boton_menu.dibujar()

    for evento in eventos:
        if boton_menu.click(evento):
            estado = MENU


# =========================
# BUCLE PRINCIPAL
# =========================
while True:
    eventos = pygame.event.get()

    for evento in eventos:
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if estado == MENU:
        pantalla_menu(eventos)

    elif estado == CONFIG:
        pantalla_config(eventos)

    elif estado == JUGANDO:
        pantalla_juego(eventos)

    elif estado == ANIMANDO:
        pantalla_animacion()

    elif estado == FINAL:
        pantalla_final(eventos)

    pygame.display.update()
    RELOJ.tick(FPS)