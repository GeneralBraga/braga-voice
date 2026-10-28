# API local

Base: `http://127.0.0.1:8765`.

## Ordem segura

1. `GET /health` — núcleo disponível;
2. `GET /api/config/status` — provedor conectado sem revelar chave;
3. `GET /api/voices` — identidades pertencentes à conta atual;
4. `POST /api/preview` — limpeza local, sem consumo;
5. `POST /api/generate` — geração externa com possível consumo.

## Cliente da skill

```bash
python scripts/braga_voice_client.py health
python scripts/braga_voice_client.py voices
python scripts/braga_voice_client.py preview --text 'Meu roteiro.' --preset natural
python scripts/braga_voice_client.py generate \
  --text 'Meu roteiro autorizado.' \
  --voice-id ID_DA_VOZ \
  --preset natural \
  --project geral \
  --output /caminho/privado/master.mp3
```

Não inclua chave ElevenLabs em nenhuma chamada. O cliente aceita somente API
local por padrão e salva o arquivo no caminho explícito fornecido.
