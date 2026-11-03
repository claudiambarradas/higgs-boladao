# Integrações e fronteiras da automação

## Arquitetura

```text
Vídeo + pedido
      ↓
Claude Code ou Codex lê a skill e coordena o trabalho
      ↓
FFprobe/FFmpeg → frames e metadados → inspeção do agente
      ↓
Editor OpenAI disponível → âncora editada → outros ângulos
      ↓
Inspeção + prompt final + associação dos arquivos
      ├─ MANUAL: imagens prontas + prompt.txt + mapa + ZIP
      └─ AUTOMÁTICO: CLI/MCP oficial Higgsfield → tarefa → arquivo → revisão
```

O método é compartilhado entre agentes. O acesso às ferramentas é específico da sessão. Skills não concedem permissões, não fazem login por conta própria e não tornam uma ferramenta ausente disponível.

## OpenAI

O adaptador Python chama `POST /v1/images/edits` com arquivos reais de entrada. [3] O frame do ângulo é o primeiro arquivo e a âncora editada pode ser adicionada como referência. A resposta precisa conter uma imagem decodificável; texto dizendo “imagem pronta” não conclui essa etapa.

Não presumir equivalência entre uma assinatura/chat e uma chamada de API, nem acesso do Claude ao histórico do ChatGPT. Conferir os direitos de uso, faturamento e modelos da rota escolhida. A skill não inclui login do ChatGPT via automação de navegador.

Uma ferramenta nativa OpenAI pode substituir o script quando estiver disponível e produzir arquivos que possam seguir no fluxo. A rota de GPT Image dentro do Higgsfield é outra opção somente se escolhida/aceita; conferir modelo, parâmetros e cobrança na plataforma. Nunca trocar o gerador por outro sem informar.

## Higgsfield: duas rotas, sem misturar credenciais

**CLI oficial:** a rota incluída como código em `higgsfield_runner.py`. Usa o executável autenticado, consulta o esquema e chama `generate create` ou `generate workflow` conforme um plano preenchido pelo agente. O CLI oferece parâmetros de mídia que podem receber caminhos locais nos modelos compatíveis. [6][7]

**MCP oficial:** o agente usa as ferramentas que o conector realmente expõe, com os esquemas e identificadores retornados. O `higgsfield_runner.py` não é um cliente MCP e não precisa ser executado nessa rota. A transferência de arquivos deve usar upload/importação oficial. No Claude web, o anexo do chat não chega ao Higgsfield automaticamente. [4]

A API de desenvolvedor do Higgsfield é um produto/fluxo diferente do login do CLI/MCP. Este pacote não implementa um cliente da API de desenvolvedor, não inventa endpoints e não exige uma chave dessa API para usar o CLI/MCP. [5]

## Modelos: descobrir em vez de fixar

O agente deve consultar o modelo atual e verificar:

- Existe uma operação que **edita o vídeo fornecido**, em vez de gerar vídeo novo só por imagem?
- Quantos vídeos/imagens aceita, em quais campos e em qual ordem?
- Quais duração, proporção, resolução e áudio são realmente suportados?
- Há controle de áudio original? A associação textual de referências é compatível?
- O custo depende de duração, resolução, modo ou quantidade? Há estimativa oficial?

IDs e nomes de controles mudam. O plano deve registrar o esquema consultado e a justificativa da operação. Não adaptar um modelo incompatível cortando o vídeo, descartando imagens ou recriando uma cena sem dizer.

## Arrobas e uploads

No prompt entregue: `@video1`, `@imagem1`, `@imagem2` etc. Acentos e espaços são proibidos dentro desses rótulos.

No transporte: arquivos reais, IDs de mídia e campos documentados. **Arroba não é caminho de arquivo, token de autenticação nem instrução de upload.** Se a interface cria chips ou outra sintaxe, associar cada item à mídia correta e registrar o mapeamento. Não afirmar que a simples presença de `@imagem1` no texto garante que o provedor sabe qual arquivo é esse.

## Espera, retomada e resultado

Salvar o ID retornado imediatamente. Consultar o estado da mesma tarefa. Se uma resposta falhar antes de retornar o ID, procurar no histórico/uso antes de reenviar. O código não promete idempotência remota.

Baixar o URL real retornado, verificar que ele é mídia legível e examinar o conteúdo. Distinguir os estados: **enviado**, **processando**, **gerado**, **obtido** e **revisado**. Se a sessão terminar, deixar o ID e o estado para retomada; não prometer monitoramento em segundo plano sem mecanismo disponível.

## Ausência de ferramenta

Concluir as partes independentes, dizer exatamente o que falta e marcar o pacote incompleto. No manual, só prompt sem imagens editadas não é a entrega combinada. Na automação, enviar uma tarefa não é entregar um vídeo final.

Fontes numeradas em `fontes.md`.
