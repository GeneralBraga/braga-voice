# AGENTS — BRAGA VOICE

## Missão

Construir uma plataforma de voz com IA em português, segura, auditável e útil
para produção de conteúdo e automações autorizadas.

## Antes de agir

1. ler `README.md` e `docs/ARQUITETURA.md`;
2. rodar `git status`;
3. verificar o estado real do BRAGA VOICE, da ElevenLabs e do armazenamento;
4. preservar arquivos e dados existentes;
5. propor e executar mudanças pequenas e testáveis.

## Regras de segurança

- clonar ou transformar somente vozes com autorização verificável;
- nunca publicar áudio, configurar cobrança, criar chaves ou enviar amostras a
  terceiros sem autorização explícita do usuário;
- não armazenar tokens, cookies, chaves, gravações pessoais ou dados de clientes
  no Git;
- modelos e datasets devem registrar origem, tamanho, licença e permissão de uso;
- analytics e serviços em nuvem permanecem opt-in;
- qualquer áudio sintético destinado ao público deve ser identificado quando o
  contexto puder induzir alguém a acreditar que é uma gravação humana real;
- push, deploy, publicação e distribuição exigem aprovação explícita.

## Limite de provedores

ElevenLabs é um provedor externo. Confirmar plano, direitos comerciais,
retenção, consumo e finalidade antes de gerar ou publicar. Manter o adaptador
substituível e nunca acoplar os demais projetos diretamente à credencial.

## Entrega mínima verificável

Cada etapa deve informar:

- provedor, modelo e versão;
- plano/direito de uso aplicável;
- entrada autorizada;
- caminho do áudio de teste;
- tempo, caracteres consumidos e observações de qualidade.
