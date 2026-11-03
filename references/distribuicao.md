# Entrega à comunidade e manutenção

## Para Claudia entregar

Enviar o ZIP da pasta inteira, com `SKILL.md` na pasta principal, e orientar a leitura de `COMECE-AQUI.md`. Não entregar somente o Markdown: ele referencia os scripts e os guias que fazem parte do fluxo.

A comunidade recebe o mesmo método e os mesmos utilitários. Cada pessoa usa suas próprias contas, permissões, créditos e diretórios de trabalho. Não incluir sua chave nem compartilhar sua sessão autenticada no pacote.

Este projeto foi preparado como base única para Claude Code e Codex, com instalador que copia os arquivos para as duas localizações. A execução estética e as ferramentas disponíveis devem ser testadas no ambiente de cada cliente. Não vender “compatibilidade testada de ponta a ponta” apenas por usar o mesmo formato de skill.

## Repositório privado ou público

O conteúdo está organizado para versionamento. Este pacote não cria repositório, não faz commit, não publica arquivos e não concede acesso a ninguém. A dona do projeto decide onde hospedar, quem acessa e sob quais termos.

Antes de publicar, revisar todos os arquivos, confirmar que `.env.example` está vazio de segredos, excluir saídas de gerações, vídeos, fotos e URLs assinados. Quando o repositório for a própria pasta do pacote, o `.gitignore` ajuda a evitar inclusão acidental de pastas de trabalho e registros. Em outro projeto, configure também o `.gitignore` da raiz dele.

Não foi imposta uma licença open source à sua criação. Para distribuição pública ou comercial, definir uma licença/termos separadamente; um repositório público e permissão de redistribuição não são a mesma decisão.

## Versões

A versão inicial é `0.1.0`, com testes locais e integrações simuladas. Depois de executar o roteiro de homologação em `TESTES.md`, registrar o cliente, as versões, os modelos, o esquema e os resultados. Só então publicar uma versão que afirme homologação daquelas combinações específicas.

Ao atualizar, manter `SKILL.md`, `agents/openai.yaml`, os templates e os scripts consistentes. Nunca mudar o contrato manual para “entregar apenas prompt” por conveniência. As regras `@video1`, `@imagem1` etc. e seleção de referências conforme o vídeo são parte do método.

## Mensagem sugerida para os alunos

> Esta é a Higgs-boladao, uma skill com meu método para transformar o visual de vídeos já gravados. Ela estuda o vídeo, prepara as imagens de referência editadas e entrega o prompt pronto. Você pode terminar manualmente no Higgsfield ou configurar a automação. Cada pessoa usa suas contas e créditos. Comece pelo arquivo COMECE-AQUI.md; a instalação não inicia nenhuma geração paga.
