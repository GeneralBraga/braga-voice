# Instalar o BRAGA VOICE no Mac

## Compatibilidade

- macOS 14 Sonoma ou superior;
- Mac com Apple Silicon: M1, M2, M3, M4 ou posterior;
- conexão com a internet para usar a ElevenLabs.

O aplicativo pronto já inclui seu núcleo local. O colaborador não precisa
instalar Python, Xcode, Homebrew nem usar o Terminal.

## Instalação

1. abra a página de
   [Releases](https://github.com/GeneralBraga/braga-voice/releases/latest);
2. baixe `BRAGA-VOICE-0.1.3-macOS-arm64.zip`;
3. abra o ZIP;
4. arraste **BRAGA VOICE.app** para a pasta **Aplicativos**;
5. na primeira vez, clique no app com o botão direito e escolha
   **Abrir → Abrir**.

Essa confirmação adicional acontece porque a versão atual ainda não possui
notarização Apple. Depois da primeira autorização, o app abre normalmente.

## Conectar a conta ElevenLabs

1. crie uma chave restrita em **ElevenLabs → API Keys**;
2. permita Text to Speech e leitura de vozes/modelos;
3. abra o BRAGA VOICE e clique em **Configurar**;
4. cole a chave e escolha uma voz da sua própria conta.

Cada instalação começa vazia e isolada. O pacote público não contém chave,
voz, áudio, roteiro nem histórico de outra pessoa. A configuração fica somente
naquele Mac em `~/Library/Application Support/BRAGA VOICE/`.

## Atualizar

Baixe a versão mais recente, encerre o BRAGA VOICE e substitua o aplicativo
antigo na pasta **Aplicativos**. A configuração e o histórico local permanecem
na pasta de suporte do usuário.

## Conferir o download

Cada release inclui um arquivo `.sha256`. Quem desejar validar o pacote pode
executar, na pasta Downloads:

```bash
shasum -a 256 -c BRAGA-VOICE-0.1.3-macOS-arm64.zip.sha256
```

O resultado esperado é `OK`.

## Remover

Mova **BRAGA VOICE.app** de Aplicativos para o Lixo. Para apagar também a
chave, os áudios e o histórico local, remova a pasta
`~/Library/Application Support/BRAGA VOICE/`.
