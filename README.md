## Relatório final do desafio técnico

---

### Identificação do Candidato

- **Nome completo: Mirian Brasilino de Souza Paes
- **GitHub: mirianbspaes-hub

---

## Visão Geral do Projeto

**O objetivo desse projeto é contar as peças que passam numa esteira de fábrica que não tem contagem automática. Ele conta sozinho as peças que passam, sem ninguém precisar anotar na mão.
**O sistema embarcado simulado funciona com um sensor de luz: quando a peça passa, ela bloqueia a luz do sensor, e o sistema conta a peça quando a luz volta, porque aí a peça já passou inteira. Se a luz ficar bloqueada tempo demais, o sistema entende que a esteira travou e manda um aviso.
**O usuário interage com ele apertando um botão para zerar o contador quando o turno acaba.

---

## Arquitetura do Sistema Embarcado

- Fluxo principal do programa (main.py): Quando o sistema liga, ele prepara os pinos e imprime a mensagem "Contador de Producao Inicializado". Depois entra num loop que roda sem parar. A cada volta, o programa faz três verificações:
1. Olha o sensor de luz para ver se está livre ou bloqueado. Se na volta anterior estava bloqueado e agora está livre, conta mais uma peça.
2. Vê há quanto tempo a luz está bloqueada. Se passar do tempo limite, avisa que a esteira travou. [essa é a micro-parada]
3. Lê o botão. Se foi apertado, zera a contagem.

- Estrutura de estados, loops e temporizações:
1. Loop que nunca trava: o programa roda dentro de um laço que repete sem parar e sem ficar parado esperando. Isso é importante porque, se ele travasse, não ia perceber quando algo mudasse (o botão apertado ou a luz voltando) na hora certa.
2. Memória do estado anterior: para contar a peça só na volta da luz, o programa guarda como o sensor estava na volta anterior (livre ou bloqueado). Assim ele compara com o estado de agora e sabe quando a luz voltou, que é o momento de contar.
3. Relógio para os tempos: em vez de ficar parado esperando, o programa vai conferindo e anotando o tempo. Ele usa isso em duas partes: para saber se a luz ficou bloqueada tempo demais (esteira travada) e para o debounce do botão, confirmando o aperto só quando o estado continua o mesmo por um tempinho. 

- Como os componentes interagem entre si:
1. O ESP32 é o cérebro do sistema. Ele fica lendo o sensor e o botão o tempo todo, decide o que fazer e manda as mensagens pela saída serial.
2. O sensor de luz (LDR) manda informação para o ESP32 pelo pino 34. Ele avisa se a luz está passando (esteira livre) ou bloqueada (peça na frente).
3. O botão manda informação para o ESP32 pelo pino 32. Com o pull-up interno ligado, ele lê 1 quando está solto e 0 quando está apertado.
O sensor e o botão são as entradas: os dois só mandam informação. Quem decide tudo (contar peça, avisar da micro-parada, zerar o contador) é o ESP32, que responde mostrando as mensagens na tela.

---


## Componentes Utilizados na Simulação

- Placa ESP32 DevKit C v4: é o microcontrolador que roda o programa. Lê o sensor e o botão e manda as mensagens pela saída serial.
- Sensor de luz (LDR) — ldr1: mede a luz que chega nele. É ligado no pino 34 (entrada analógica). Quando uma peça passa, ela bloqueia a luz, e é assim que o sistema percebe a passagem da peça.
- Botão (pushbutton) — btn1: serve para o operador zerar o contador. É ligado no pino 32, com pull-up interno, então lê 1 quando está solto e 0 quando está apertado.

---

## Decisões Técnicas Relevantes

- Limiar da luz: simulei valores no sensor e vi que com luz alta a leitura fica em torno de 32 e com luz baixa em torno de 4063. Escolhi o limiar 2000 por ficar longe dos dois extremos, evitando leituras trêmulas quando a luz varia.
- Constantes no topo: coloquei os valores importantes como constantes no topo do código (o limiar da luz, o tempo da micro-parada e o tempo do debounce), com nomes em maiúsculas. Assim, se eu precisar mudar algum, é fácil achar num lugar só, em vez de procurar espalhado pelo código.
- Tempo da micro-parada: usei 3 segundos porque esse tempo tinha que ficar no meio: maior que o tempo de uma peça normal passando (uns 300 milissegundos), pra não confundir peça com travamento, e menor que o tempo de uma esteira travada de verdade (5 segundos), pra conseguir avisar a tempo.
- Programa que não trava: em vez de travar o programa esperando (com um sleep, por exemplo), usei um jeito de anotar o tempo e ir conferindo a cada volta do loop. Assim o programa nunca para e continua percebendo a mudança de estado do sensor e do botão na hora que acontece. Usei isso tanto para a micro-parada quanto para o debounce do botão.

---

## Resultados Obtidos

Testei os três comportamentos do sistema no simulador do Wokwi e todos funcionaram como esperado:
- Inicialização: ao ligar, o sistema imprime "Contador de Producao Inicializado".
- Contagem de peças: ao bloquear e depois liberar a luz do sensor, o contador incrementa e mostra "Peca detectada! Total: X". Testei várias peças em sequência e a contagem subiu corretamente, contando cada peça uma única vez, no momento em que a luz volta.
- Micro-parada: ao manter a luz bloqueada por mais de 3 segundos, o sistema imprime "Alerta: Micro-parada detectada!", uma única vez.
- Reset: ao apertar o botão, o contador zera e o sistema imprime "Turno resetado com sucesso. Contadores zerados.".
Todos os requisitos do cenário LIGHT foram atendidos: inicialização, contagem por borda de subida, detecção de micro-parada com temporizador não-bloqueante e reset com debounce.

Na validação automática (GitHub Actions), os testes de contagem e de reset são atendidos pelo firmware. O teste de micro-parada (test_2) apresenta um "Timeout: simulation did not finish in 10000ms": o log confirma que a mensagem "Alerta: Micro-parada detectada!" é impressa corretamente, mas a soma do tempo de boot do MicroPython com o delay de 5 segundos previsto no próprio cenário ultrapassa o limite padrão de 10 segundos do wokwi-ci-action. Como esse limite é definido no arquivo de workflow (ci.yml), que não deve ser alterado, o firmware está correto mas a simulação é encerrada antes de o cenário concluir.

---

## Comentários Adicionais (Opcional)

A maior dificuldade não foi no código, e sim na validação automática do teste de micro-parada (test_2).
O firmware funciona: quando testei manualmente no Wokwi, a mensagem "Alerta: Micro-parada detectada!" aparece certinho depois do tempo de bloqueio. No GitHub Actions, o log também mostra a mensagem sendo impressa corretamente. Mas o teste falha com "Timeout: simulation did not finish in 10000ms".
Investigando, descobri o motivo: o test_2 tem um "delay: 5s" fixo, e somado ao tempo de boot do MicroPython no ESP32, a simulação passa dos 10 segundos que o wokwi-ci-action usa como limite padrão. Esse limite fica no arquivo ci.yml (workflow), que as regras pedem para não alterar. Tentei resolver mudando o tempo de micro-parada no meu código, mas não adianta, porque o delay de 5s está no próprio arquivo de teste, não no firmware. Também verifiquei o wokwi.toml e o diagram.json, mas nenhum deles permite mudar esse timeout.
Ou seja, o firmware está correto, mas a simulação é encerrada antes do cenário terminar por uma limitação do ambiente de teste. Os testes de contagem (test_1) e de reset (test_3) não têm esse problema.

---
