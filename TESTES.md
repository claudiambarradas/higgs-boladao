# Testes e pendências — Higgs-boladao 0.1.0

**Executado em 03/11/2026. Resultado: 37 testes aprovados, sem falhas.**

## Ambiente efetivamente utilizado

Linux • Python 3.13.5 • FFmpeg/FFprobe 7.1.5 • Pillow 12.3.0 • requests 2.32.5.

Comando reproduzível, executado na pasta do pacote:

```bash
python -m unittest discover -s tests -v
```

## O que foi executado

| Grupo | Quantidade | Verificação |
|---|---:|---|
| Utilitários/arquivos locais e mídia sintética | 26 | Rótulos, limites, amostragem, extração, proporção, áudio, rotação, folhas de análise, bloqueios, entrega manual e instalação em diretórios temporários |
| Integrações simuladas | 11 | Decodificação de imagem, recibos, timeout sem repetição, plano de CLI, bloqueio no modo manual, estimativa maior que teto e prevenção local de reenvio |
| **Total** | **37** | **Todos aprovados** |

Mídia: vídeo sintético vertical com padrão de teste e áudio gerado localmente pelo FFmpeg. Uma alteração simples de pixels simulou a existência de uma referência editada para validar o empacotador. Isso não é teste de geração estética por IA.

Na simulação OpenAI, uma resposta fictícia com bytes de PNG substituiu a chamada de rede. Na simulação Higgsfield, respostas fictícias substituíram o processo CLI. Os modelos e IDs de teste são declaradamente fictícios e não são presets de produção.

## O que foi conferido nos arquivos

A sintaxe Python foi compilada; os templates JSON são objetos válidos; o frontmatter e o nome da skill são consistentes; os caminhos de scripts/referências citados no arquivo principal existem. Os comandos de ajuda dos utilitários foram executados. O ZIP de distribuição é verificado quanto à integridade após sua criação.

## O que NÃO foi testado

Não houve login OpenAI/Higgsfield, chamada real paga, consulta autenticada de saldo/modelos, geração real de imagem, geração real de vídeo, upload de mídia ao Higgsfield, download de um resultado real nem teste da interface MCP. Nenhuma cobrança foi iniciada por esses testes.

Não houve execução real dentro de uma sessão do Claude Code ou do Codex, nem teste em macOS ou Windows. A instalação nos caminhos documentados foi exercitada em diretórios temporários de Linux. O formato e a organização foram preparados para os dois clientes, mas isso não equivale a homologar toda a experiência de cada aplicativo.

O teste de código não comprova fidelidade facial, qualidade da roupa, coerência de espelho ou sincronização labial de uma geração. Esses itens exigem mídia real e avaliação visual/sonora.

## Roteiro de homologação antes de anunciar automação validada

### Caso 1 — câmera fixa, uma referência

Usar um vídeo curto e autorizado, mudar só uma peça de roupa. Verificar se o agente analisa toda a duração, escolhe uma referência quando suficiente, gera o arquivo editado e entrega imagem individual, prompt e mapa. No modo manual, conferir que nenhuma tarefa de vídeo foi enviada pelo agente.

### Caso 2 — giro, perfil e costas

Usar um vídeo que exponha lados diferentes. Conferir se o agente seleciona os instantes certos, mantém o mesmo visual em todas as referências e respeita o número de imagens permitido pelo modelo. Não aprovar referências com roupas ou cabelos contraditórios.

### Caso 3 — espelho e objeto na mão

Conferir pessoa, reflexo, roupa, oclusões, mãos e iluminação antes e depois da geração. Verificar que uma referência de espelho não transforma a vista refletida em duplicata frontal.

### Caso 4 — fluxo automático real

Configurar a própria conta; consultar modelo/esquema e estimativa; autorizar um limite pequeno; gerar uma tarefa; salvar seu ID; consultar até concluir; baixar pelo endereço retornado; revisar vídeo completo, dimensões e áudio. Registrar o custo observado separadamente da estimativa.

### Caso 5 — falha e retomada

Simular desconexão no acompanhamento após o envio. Retomar pelo mesmo ID e conferir que não há segundo pedido pago. Testar bloqueio por limite local e resposta incompleta. Não apagar estado/ledger para fazer o teste passar.

### Caso 6 — segundo cliente

Repetir instalação, reconhecimento da skill e ao menos um caso real no outro cliente. Registrar quais ferramentas de imagem e de vídeo estavam disponíveis. Não presumir que a conexão do primeiro cliente foi transferida.

## Registro sugerido

Para cada ensaio real, salvar em uma pasta privada de trabalho: versão do pacote, sistema, cliente, versão do CLI, modelo/ID, esquema consultado, parâmetros, número de imagens, duração, proporção, estimativa, custo observado, ID da tarefa, resultado e problemas encontrados. Não incluir chaves nem mídia de alunos no repositório de distribuição.
