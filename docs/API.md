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
| `GET` | `/api/audio/{id}` | Baixar uma geração local |

Agentes devem usar esta API interna em vez de receber a chave ElevenLabs. Uma
geração é uma ação com custo no provedor e exige pedido explícito do usuário.
