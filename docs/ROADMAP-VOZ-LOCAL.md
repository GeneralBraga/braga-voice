# Roadmap — BRAGA VOICE local

## Objetivo

Adicionar ao BRAGA VOICE um motor de síntese que funcione no próprio Mac,
sem consumo por caractere e sem depender da ElevenLabs para cada geração,
preservando português brasileiro, naturalidade, identidade vocal e o fluxo
atual de preparação, reprodução e download.

O produto continuará multimotor:

- **Local — Qwen3-TTS:** padrão para produção diária e testes sem créditos;
- **ElevenLabs:** referência de qualidade, contingência e trabalhos escolhidos
  explicitamente pelo usuário.

## Decisões já tomadas

- motor inicial: `Qwen3-TTS-12Hz-1.7B-Base`;
- runtime no Mac: MLX/Metal;
- primeira variante: 8-bit, adequada ao Mac M3 Pro com 18 GB;
- idioma prioritário: português brasileiro;
- saída final padrão: MP3 mono, 44,1 kHz, 128 kbps;
- WAV será usado somente como intermediário interno de processamento;
- licença do modelo: Apache 2.0;
- nenhuma voz, gravação, transcrição ou peso personalizado entra no Git;
- referências de voz são aceitas somente quando próprias ou autorizadas;
- o modelo não será incluído dentro do aplicativo: será baixado e removido
  pelo Gerenciador de Modelos;
- ElevenLabs permanece disponível, mas nunca será acionada automaticamente
  quando o usuário escolher geração local.

Fontes técnicas:

- modelo oficial: <https://github.com/QwenLM/Qwen3-TTS>;
- conversão MLX 8-bit: <https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit>;
- runtime MLX-Audio: <https://github.com/Blaizzy/mlx-audio>.

## O que significa migrar uma voz

A ElevenLabs não exporta o clone como um arquivo de modelo. A migração será
feita criando um perfil local a partir de áudio pertencente ao usuário:

1. importar uma ou mais referências de áudio;
2. registrar a transcrição exata de cada referência;
3. preparar e validar o áudio;
4. criar um perfil local reutilizável;
5. testar o mesmo roteiro no motor local e na ElevenLabs;
6. manter somente as referências que melhor preservarem identidade e estilo.

Prioridade das fontes:

1. gravação humana original, limpa e autorizada;
2. gravação humana autorizada tratada, sem música ou efeitos;
3. áudio sintético pertencente ao usuário, apenas como referência auxiliar e
   sempre com origem registrada.

Não será usado download em massa da ElevenLabs como atalho de treinamento.
Isso aumenta custo, incorpora artefatos do motor e dificulta provar a origem
da identidade vocal.

## Armazenamento privado

```text
~/Library/Application Support/BRAGA VOICE/
├── models/
│   └── qwen3-tts-1.7b-base-8bit/
├── voices/
│   └── <id-da-voz>/
│       ├── profile.json
│       ├── reference.wav
│       ├── transcript.txt
│       └── consent.json
├── audio/
└── history/
```

`profile.json` registra nome, idioma, origem, data, checksum e configuração.
`consent.json` registra propriedade ou autorização sem armazenar documento
pessoal no Git ou nos logs.

## Fase 0 — inventário e padrão de qualidade

### Entregas

- listar as vozes que serão migradas;
- localizar as melhores referências pertencentes ao usuário;
- criar roteiro-padrão PT-BR para comparação;
- definir a ficha de avaliação auditiva;
- fazer backup privado das referências, fora do repositório.

### Roteiro de benchmark

O conjunto deve testar:

- fala natural e conversada;
- chamada comercial com energia controlada;
- texto institucional;
- nomes próprios e marcas;
- datas, horários, telefones, percentuais e valores;
- siglas e palavras estrangeiras;
- frases longas e mudanças de emoção.

### Gate de conclusão

Cada voz possui referência, transcrição, origem e autorização verificáveis.

## Fase 1 — laboratório local isolado

### Entregas

- instalar MLX-Audio em ambiente separado do aplicativo distribuído;
- baixar o Qwen3-TTS 1.7B Base 8-bit;
- gerar voz em português usando referência + transcrição;
- medir tempo de carregamento, memória, geração e tamanho do áudio;
- comparar 0.6B e 1.7B somente se o 1.7B ficar lento demais;
- documentar versões exatas, licença, tamanho e checksum do modelo.

### Gate de conclusão

- geração funciona sem internet após o download do modelo;
- nenhuma chamada é enviada à ElevenLabs;
- o áudio é inteligível, estável e reconhecível como a identidade de referência;
- o processo não deixa o Mac sem memória utilizável.

## Fase 2 — adaptador `qwen-local`

### Entregas

- criar um adaptador separado de `elevenlabs-cloud`;
- preservar o mesmo contrato de preparação e geração;
- adicionar fila única para impedir duas gerações pesadas simultâneas;
- carregar o modelo apenas quando necessário;
- descarregar modelo e limpar cache pela interface;
- registrar motor, modelo, tempo e parâmetros no histórico;
- nunca expor caminhos privados ou referências na API pública.

### API prevista

```text
GET    /api/engines
GET    /api/models
POST   /api/models/qwen-local/install
DELETE /api/models/qwen-local
GET    /api/local-voices
POST   /api/local-voices
DELETE /api/local-voices/{id}
POST   /api/generate   engine=qwen-local|elevenlabs-cloud
```

### Gate de conclusão

Os testes automatizados comprovam que selecionar `qwen-local` não lê nem
consome a chave ElevenLabs.

## Fase 3 — experiência dentro do aplicativo

### Entregas

- seletor **Local / ElevenLabs / Automático**;
- tela **Modelos locais** com download, progresso, tamanho e remoção;
- assistente **Criar voz local**;
- importação de áudio e transcrição;
- prévia da referência antes de salvar;
- biblioteca visual de vozes locais;
- indicador claro `100% LOCAL — SEM CRÉDITOS`;
- mensagem honesta em Macs Intel quando o motor MLX não estiver disponível.

O modo **Automático** só poderá usar ElevenLabs após confirmação explícita;
nunca haverá fallback pago silencioso.

### Gate de conclusão

Uma pessoa sem Terminal consegue instalar o modelo, criar uma voz local,
gerar, ouvir e baixar o MP3.

## Fase 4 — Diretor de Narração local

### Entregas

- aproveitar a higienização de texto existente;
- dividir textos longos por sentido, sem criar pausas artificiais;
- unir os trechos com silêncio controlado;
- dicionário de pronúncia por voz e por projeto;
- controle de velocidade, energia e estabilidade compatível com o motor;
- normalização de volume, remoção de silêncio excedente e exportação MP3;
- seed configurável para repetir uma tomada aprovada quando possível.

### Gate de conclusão

O mesmo roteiro produz tomadas consistentes, sem palavras comidas,
duplicações, alucinações ou pausas anormais.

## Fase 5 — benchmark contra ElevenLabs

Cada voz será avaliada às cegas, usando os mesmos roteiros:

| Critério | Nota mínima desejada |
|---|---:|
| Semelhança da identidade | 4/5 |
| Naturalidade | 4/5 |
| Português brasileiro | 4/5 |
| Nomes, números e siglas | 4/5 |
| Ritmo e pausas | 4/5 |
| Ausência de artefatos | 4/5 |

Também serão medidos:

- tempo até o primeiro áudio;
- tempo total por 100 e 1.000 caracteres;
- memória máxima;
- tamanho dos modelos;
- quantidade de tentativas necessárias para uma tomada aprovada;
- créditos ElevenLabs economizados.

### Gate de conclusão

O motor local vira padrão apenas para as vozes que atingirem a nota mínima.
As demais continuam com ElevenLabs enquanto recebem novas referências ou
ajuste de qualidade.

## Fase 6 — ajuste fino opcional

O ajuste fino só começa se a clonagem por referência não atingir a meta.

### Dataset recomendado

- 30 a 60 minutos de fala humana limpa para o primeiro experimento;
- um único locutor por perfil;
- transcrição exata;
- variação de fonemas, ritmo, emoção, números e nomes;
- arquivos WAV mono consistentes;
- sem música, reverberação, compressão forte ou redução de ruído agressiva.

O treinamento pode exigir GPU externa temporária. Nesse caso, o dataset será
criptografado, o provedor será aprovado antes do envio e os arquivos remotos
serão apagados após a validação. A inferência final continuará local no Mac.

### Gate de conclusão

O modelo ajustado precisa superar o perfil por referência no teste cego. Se
não superar, ele é descartado e não entra no produto.

## Fase 7 — empacotamento e distribuição

### Apple Silicon

- BRAGA VOICE instala o runtime e o modelo sob demanda;
- app continua pequeno;
- modelo pode ser atualizado ou removido sem reinstalar o app.

### Intel

- ElevenLabs continua funcionando normalmente;
- motor MLX local aparece como indisponível;
- um motor CPU só será adicionado após benchmark próprio de qualidade e tempo.

### Releases planejadas

- `0.2.0-alpha.1`: laboratório Qwen local pela API;
- `0.2.0-beta.1`: vozes locais e gerenciador de modelos na interface;
- `0.2.0`: geração local aprovada, documentação e instalador;
- `0.2.x`: qualidade, dicionário e otimizações;
- `0.3.0`: ajuste fino, somente se o benchmark justificar.

## Definição de concluído

O projeto de voz local estará concluído quando:

- [ ] o usuário instalar o modelo sem Terminal;
- [ ] pelo menos uma voz autorizada atingir a nota mínima do benchmark;
- [ ] uma geração de 1.000 caracteres terminar sem consumir créditos;
- [ ] o app funcionar sem internet depois do modelo instalado;
- [ ] player e download MP3 funcionarem como no motor ElevenLabs;
- [ ] referências, modelos personalizados e áudios permanecerem fora do Git;
- [ ] cada áudio registrar qual motor e versão foram usados;
- [ ] o fallback pago exigir confirmação;
- [ ] testes, privacidade, empacotamento e instalação real passarem;
- [ ] uma pessoa não técnica conseguir completar o fluxo inteiro.

## Ordem de execução

1. selecionar uma única voz piloto;
2. separar uma referência limpa e sua transcrição;
3. executar a Fase 1 sem alterar o aplicativo instalado;
4. aprovar ou rejeitar a qualidade do Qwen;
5. somente depois integrar o adaptador ao BRAGA VOICE;
6. concluir todas as fases com a voz piloto;
7. migrar as demais vozes uma por vez.

Essa ordem evita gastar tempo migrando toda a biblioteca antes de provar que
o motor local atende ao padrão de qualidade esperado.
