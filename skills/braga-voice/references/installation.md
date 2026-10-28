# Instalação e configuração

## Localizar uma instalação existente

1. teste `http://127.0.0.1:8765/health`;
2. no macOS, procure `/Applications/BRAGA VOICE.app`;
3. para código-fonte, use um checkout explícito fornecido pelo usuário ou clone
   `https://github.com/GeneralBraga/braga-voice.git`.

## Instalar no macOS Apple Silicon

Na raiz do checkout:

```bash
./scripts/install.sh
```

Depois, abra o aplicativo. O usuário deve clicar em **Configurar** e inserir a
própria chave ElevenLabs na tela local. Não solicite a chave no chat.

## Instalar a skill

```bash
./scripts/install-agent-skill.sh
```

O script instala em `~/.codex/skills/braga-voice` e
`~/.claude/skills/braga-voice`. Use `--replace` somente para uma atualização
explicitamente solicitada.

## Limites atuais

- macOS 14+;
- Apple Silicon;
- bundle ad hoc; distribuição sem alertas exige Developer ID e notarização.
