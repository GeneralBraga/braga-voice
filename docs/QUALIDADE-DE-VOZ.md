# Qualidade e naturalidade

## Padrão atual

- `Natural`, `Comercial` e `Institucional`: Eleven v4;
- `Urgente`: Eleven v4 Turbo;
- `Teste rápido`: Eleven Flash v2.5, priorizando custo e velocidade;
- idioma explícito `pt` e normalização de texto em modo automático;
- no Eleven v4, apenas estabilidade e similaridade são enviadas; estilo e
  velocidade ficam no padrão nativo do modelo;
- linhas e parágrafos visuais convertidos em pontuação falada, sem silêncio
  proporcional ao número de quebras.

## Como escrever para soar natural

- escreva como a pessoa realmente falaria;
- use frases curtas e pontuação comum;
- evite reticências, linhas vazias repetidas e palavras inteiras em caixa alta;
- escreva siglas, números, datas e valores da forma como devem ser falados;
- use `Preparar narração` antes de gerar e leia a versão dirigida;
- confira a lista de ajustes: pausas, pontuação, espaçamento, formatação,
  abreviações e divisão de frases longas são tratadas localmente;
- o texto processado exibido é exatamente o texto usado na síntese.

## Quando a voz ainda soar robótica

O modelo não corrige uma amostra de clonagem ruim. Verifique, nesta ordem:

1. se a voz foi criada com gravação limpa, sem música, eco ou redução de ruído
   agressiva;
2. se a amostra está em português brasileiro e representa o ritmo desejado;
3. se o preset Natural e o modelo Eleven v4 estão selecionados;
4. se o roteiro contém pausas artificiais ou escrita pouco conversada;
5. se outra regeneração do mesmo texto resolve uma variação pontual.

Referências oficiais: [Text to Speech](https://elevenlabs.io/docs/overview/capabilities/text-to-speech)
e [boas práticas](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices).
