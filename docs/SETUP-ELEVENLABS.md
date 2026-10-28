# Conectar a ElevenLabs

Cada pessoa conecta a própria conta. Nenhuma chave, voz ou áudio do mantenedor
é distribuído com o BRAGA VOICE.

## Pela tela do aplicativo

1. crie uma chave restrita em **ElevenLabs → API Keys**;
2. habilite somente as permissões necessárias para Text to Speech e leitura de
   vozes/modelos;
3. abra o BRAGA VOICE e clique em **Configurar**;
4. cole a chave e selecione uma voz pertencente à sua conta.

A chave é enviada apenas ao backend local em `127.0.0.1`, validada diretamente
na ElevenLabs e gravada neste Mac com permissão `600`. Ela nunca é devolvida
pela API local.

## Pelo arquivo local

Como alternativa:

```bash
mkdir -p "$HOME/Library/Application Support/BRAGA VOICE"
cp .env.example "$HOME/Library/Application Support/BRAGA VOICE/.env"
chmod 600 "$HOME/Library/Application Support/BRAGA VOICE/.env"
```

Preencha somente no arquivo local:

```text
ELEVENLABS_API_KEY=sua_chave_local
ELEVENLABS_VOICE_ID=id_opcional_da_sua_voz
```

Nunca cole a chave em chat, issue, commit, documentação ou captura de tela.

## Modelos do MVP

- conteúdo e narração: `eleven_multilingual_v2`;
- testes rápidos: `eleven_flash_v2_5`.

Revise números, datas, siglas, nomes e valores na prévia antes da geração.
Confirme também o plano, o direito comercial e a política de retenção da sua
conta ElevenLabs.
