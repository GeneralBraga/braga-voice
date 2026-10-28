# Arquitetura inicial

## Princípio

Separar o produto BRAGA VOICE dos motores de síntese. A interface e os fluxos
pertencem ao produto; cada motor entra por um adaptador substituível.

```text
Interface BRAGA VOICE
        |
Shell nativo macOS (Swift + WebKit)
        |
Orquestrador e fila de geração
        |
Adaptadores de voz
        |
ElevenLabs (primeiro provedor)
        |
Arquivos e metadados locais
```

## Componentes previstos

### 1. Interface

- editor com Diretor de Narração e prévia exata do texto para TTS;
- seleção de projeto, voz e estilo;
- histórico e player;
- download do arquivo gerado.

No macOS, a interface é apresentada por um shell nativo Swift/AppKit com
WebKit. O shell inicia e encerra o backend empacotado junto com o ciclo de vida
do aplicativo.

### 2. Orquestrador

- normaliza texto em PT-BR sem reescrever seu significado;
- transforma quebras visuais em fluxo falado sem criar silêncios longos;
- corrige espaçamento e pontuação, fecha fragmentos, prepara abreviações e
  divide frases excessivamente longas apenas em pausas já escritas pelo autor;
- registra e exibe cada categoria de ajuste antes de qualquer consumo;
- escolhe motor conforme qualidade, privacidade, custo e velocidade;
- registra status, duração, modelo e parâmetros;
- nunca publica automaticamente.

### 3. Motores

- `elevenlabs-cloud`: primeiro adaptador, depende de credencial local;
- outros motores entram somente após benchmark e revisão de licença.

### 4. Dados

- gravações, áudios e metadados fora do Git;
- metadados com origem, consentimento, licença e finalidade;
- exclusão controlada e trilha de auditoria;
- caminhos locais configuráveis.

## Fases

### Fase 0 — base local concluída

- interface e API local;
- Diretor de Narração local com relatório de ajustes;
- presets de direção;
- adaptador ElevenLabs;
- armazenamento fora do Git;
- testes automatizados.

### Fase 1 — MVP local

- [x] conectar conta e voz ElevenLabs;
- [x] gerar e ouvir áudio real;
- [x] aplicativo nativo instalado no macOS;
- [x] exportar MP3 e manter histórico local;
- [x] download nativo do MP3 para a pasta Downloads no aplicativo macOS;
- [ ] biblioteca visual de projetos e histórico dentro da interface.

### Fase 2 — produto multimotor

- skill compartilhada entre projetos;
- segundo adaptador de voz opcional;
- filas e lotes;
- API interna e integração com agentes.

### Fase 3 — produção

- autenticação e controle de acesso;
- política de consentimento e retenção;
- custos, limites e observabilidade;
- revisão jurídica/licenças;
- deploy somente após aprovação explícita.

## Decisões abertas

- plano ElevenLabs inicial: Starter ou Creator;
- clonagem instantânea ou profissional;
- prioridades iniciais de integração entre projetos consumidores;
- integração futura de LLM para criação do roteiro dentro da própria tela.
