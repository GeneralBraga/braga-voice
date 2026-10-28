---
name: braga-voice
description: Instale, configure, opere ou diagnostique o BRAGA VOICE; prepare roteiros para TTS em português, liste vozes autorizadas e gere áudio pela API local conectada à conta ElevenLabs do próprio usuário. Use quando o pedido mencionar BRAGA VOICE, voz com IA, ElevenLabs local, síntese de roteiro ou integração de um projeto com a central de voz.
---

# BRAGA VOICE

Use o BRAGA VOICE como central local de síntese. Outros projetos e agentes
devem falar com a API em `127.0.0.1`; nunca devem receber a chave ElevenLabs.

## Escolha o modo

- Para instalar ou atualizar, leia [references/installation.md](references/installation.md).
- Para preparar, listar vozes ou gerar áudio, leia [references/api.md](references/api.md)
  e prefira `scripts/braga_voice_client.py`.
- Para diagnosticar, verifique primeiro `/health`, depois configuração, vozes e
  somente então uma prévia sem custo.

## Regras essenciais

- Use somente voz própria ou com autorização verificável.
- Nunca peça ao usuário para colar chave em chat, prompt, issue ou commit.
- A configuração da conta deve ser feita na tela local do aplicativo.
- Preparar texto não consome créditos; gerar áudio envia texto à ElevenLabs e
  pode consumir créditos. Gere somente quando o usuário pedir a geração.
- Não publique, envie ou compartilhe áudio automaticamente.
- Mantenha áudios, roteiros privados e histórico fora do repositório.
- Ao concluir, informe voz, preset, caracteres e caminho local do arquivo, sem
  revelar credenciais ou dados de outras gerações.

## Roteiros

Ajude a escrever e revisar o roteiro no chat. Antes da síntese, use a prévia
local para remover Markdown, emojis, links e marcadores visuais. Preserve
pontuação útil à interpretação e revise nomes, siglas, números, datas e valores.

## Integrações

Integre sistemas consumidores somente pela API local documentada. Não acople
um projeto diretamente à ElevenLabs e não copie `.env` entre computadores.
Cada instalação deve conectar a conta e as vozes do seu próprio usuário.
