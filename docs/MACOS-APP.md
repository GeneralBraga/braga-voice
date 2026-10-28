# Aplicativo macOS

## Compatibilidade atual

- macOS 14 ou superior;
- Apple Silicon (`arm64`) ou Intel de 64 bits (`x86_64`);
- bundle ID: `com.bragavoice.desktop`;
- dados privados: `~/Library/Application Support/BRAGA VOICE/`;
- logs locais: `~/Library/Logs/BRAGA VOICE/backend.log`.

## Arquitetura

O executável nativo usa Swift/AppKit e apresenta a interface em WebKit. Ao
abrir, ele inicia o backend FastAPI empacotado em `127.0.0.1:8765`. Ao encerrar
o aplicativo, o backend também é encerrado.

Enquanto o núcleo inicia, uma tela nativa usa a mesma marca oficial do app em
fundo preto, com estado de carregamento discreto. A marca é empacotada como
recurso local; a abertura não depende de internet nem de arquivo externo.

A credencial ElevenLabs não entra no bundle. Quando o usuário conecta a conta
pela tela, a chave é validada e gravada no suporte local do aplicativo com
permissão `600`. A API nunca devolve a chave.

## Instalar pelo código-fonte

```bash
./scripts/install.sh
```

O instalador cria o ambiente Python, executa os testes, constrói o bundle e
instala `/Applications/BRAGA VOICE.app`.

Para colaboradores e usuários finais, prefira o aplicativo pronto da página
de Releases. Consulte [Instalar no Mac](INSTALAR-NO-MAC.md).

Para construir e instalar manualmente:

```bash
./scripts/build-macos-app.sh
./scripts/install-macos-app.sh --replace
```

## Distribuição

O script abaixo cria um ZIP versionado e um checksum SHA-256:

```bash
./scripts/package-release.sh
```

O pacote é nativo da arquitetura do computador que realiza o build. A esteira
do GitHub compila e verifica separadamente `arm64` em runner Apple Silicon e
`x86_64` em runner Intel.

Sem Developer ID e notarização, o macOS pode solicitar autorização manual na
primeira abertura. A versão pública atual informa esse limite e orienta a
abertura manual. Developer ID e notarização serão necessários para uma
instalação sem alertas.

## Checklist de validação

- `./scripts/check.sh` passa;
- `codesign --verify --deep --strict` passa;
- o app abre sem Terminal;
- `/health` responde `ok`;
- a tela de configuração não mostra nem devolve a chave;
- a conta conectada lista somente as vozes daquele usuário;
- o encerramento libera a porta `8765`.
