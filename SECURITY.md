# Segurança

## Relatar uma vulnerabilidade

Não abra issue pública contendo chave, áudio privado, gravação de voz ou dados
pessoais. Use o canal privado do proprietário do repositório.

## Garantias atuais

- serviço restrito a `127.0.0.1` por padrão;
- credencial fora do bundle e do Git;
- gravação atômica da configuração com permissão `600`;
- respostas e logs não incluem a chave;
- downloads locais usam identificadores validados;
- CI executa testes e verificação de privacidade.

## Limites

O bundle atual usa assinatura ad hoc. Por isso, o macOS pode exigir autorização
manual na primeira abertura. Uma distribuição sem esse alerta deve usar
Developer ID, notarização Apple e revisão de dependências.
