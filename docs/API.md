# API local

Base padrão: `http://127.0.0.1:8765`.

| Método | Rota | Finalidade |
|---|---|---|
| `GET` | `/health` | Saúde e versão |
| `GET` | `/api/config/status` | Estado sem expor a chave |
| `POST` | `/api/config` | Validar e salvar a própria chave local |
| `GET` | `/api/voices` | Listar vozes da conta conectada |
| `GET` | `/api/presets` | Listar direções vocais |
| `POST` | `/api/preview` | Limpar e validar o texto |
| `POST` | `/api/generate` | Gerar áudio autorizado |
| `GET` | `/api/audio/{id}` | Reproduzir uma geração local (`inline`) |
| `GET` | `/api/audio/{id}/download` | Baixar o MP3 (`attachment`) |

Agentes devem usar esta API interna em vez de receber a chave ElevenLabs. Uma
geração é uma ação com custo no provedor e exige pedido explícito do usuário.

O retorno de `/api/generate` separa `audio_url`, `download_url` e `filename`.
O texto é enviado com idioma português e normalização automática. O preset
Natural usa Eleven v4; o preset Teste rápido permanece no Flash v2.5.
