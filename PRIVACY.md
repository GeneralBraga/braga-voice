# Privacidade

## Isolamento por instalação

O BRAGA VOICE não distribui chaves, vozes, áudios ou histórico. Cada usuário
conecta a própria ElevenLabs e os dados são salvos somente no computador local.

## Dados enviados ao provedor

Ao solicitar uma geração, o aplicativo envia à ElevenLabs:

- texto preparado pelo usuário;
- identificador da voz selecionada;
- modelo, formato e parâmetros de voz.

O aplicativo não envia automaticamente arquivos locais, contatos, histórico
de outros projetos ou credenciais a qualquer outro serviço.

## Dados locais

Chave, histórico, áudios e logs ficam em pastas locais ignoradas pelo Git. A
chave recebe permissão de arquivo `600` e nunca é retornada pelos endpoints.

## Analytics

Não há analytics, rastreamento ou telemetria remota no MVP.
