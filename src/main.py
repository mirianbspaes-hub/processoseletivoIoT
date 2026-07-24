from machine import Pin, ADC
import time

LIMIAR = 2000
TEMPO_MICROPARADA = 3000
TEMPO_DEBOUNCE = 50

ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
botao = Pin(32, Pin.IN, Pin.PULL_UP)

total_pecas = 0
estava_bloqueado = False
inicio_bloqueio = 0
alerta_enviado = False

estado_botao = 1
ultimo_estado_lido = 1
ultima_mudanca = 0

print("Contador de Producao Inicializado")

while True:
    leitura = ldr.read()
    bloqueado_agora = leitura > LIMIAR

    # Contagem: peça passou (luz voltou)
    if estava_bloqueado and not bloqueado_agora:
        total_pecas = total_pecas + 1
        print("Peca detectada! Total:", total_pecas)

    # Micro-parada: cronometra o bloqueio contínuo
    if bloqueado_agora:
        if not estava_bloqueado:
            inicio_bloqueio = time.ticks_ms()
            alerta_enviado = False
        tempo_parado = time.ticks_diff(time.ticks_ms(), inicio_bloqueio)
        if tempo_parado > TEMPO_MICROPARADA and not alerta_enviado:
            print("Alerta: Micro-parada detectada!")
            alerta_enviado = True

    estava_bloqueado = bloqueado_agora

    # Reset: botão com debounce
    leitura_botao = botao.value()
    if leitura_botao != ultimo_estado_lido:
        ultima_mudanca = time.ticks_ms()
        ultimo_estado_lido = leitura_botao

    if time.ticks_diff(time.ticks_ms(), ultima_mudanca) > TEMPO_DEBOUNCE:
        if leitura_botao != estado_botao:
            estado_botao = leitura_botao
            if estado_botao == 0:
                total_pecas = 0
                print("Turno resetado com sucesso. Contadores zerados.")