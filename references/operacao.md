# Operação para o agente

Os caminhos nos exemplos são ilustrativos. Localize a pasta real desta skill, o Python com dependências e a pasta de trabalho do usuário. Não presuma que a pasta atual é a da skill. Não peça ao aluno que preencha JSON: o agente cria os arquivos após examinar as evidências.

## A. Verificar e extrair

```bash
python /CAMINHO/DA/SKILL/scripts/doctor.py
python /CAMINHO/DA/SKILL/scripts/video_frames.py original.mp4 --probe-only
python /CAMINHO/DA/SKILL/scripts/video_frames.py original.mp4 --out runs/caso/analise --every 1 --scene-detect
```

Abra **todas** as folhas `analise-001.jpg`, `analise-002.jpg` etc. e os frames em resolução original que forem relevantes. O limite de frames gera erro em vez de truncar o fim do vídeo. Para um vídeo longo, divida a análise em intervalos contíguos e registre a cobertura; não analise só o começo.

Refine trechos rápidos e extraia os instantes escolhidos:

```bash
python /CAMINHO/DA/SKILL/scripts/video_frames.py original.mp4 --out runs/caso/refinamento --start 2 --end 4 --every 0.15
python /CAMINHO/DA/SKILL/scripts/video_frames.py original.mp4 --out runs/caso/selecionados --times 0.8 2.6 4.3
```

Use tempos existentes no vídeo real. Os números acima são apenas exemplos. Os timestamps do extrator são alvos de busca, não PTS medidos frame a frame. A seleção de mudanças de cena é uma ajuda técnica; movimento sem corte também exige referências adicionais.

## B. Gerar uma âncora visual

Escreva um prompt específico de imagem em `edicao-principal.txt`, com as mudanças e as preservações. Não usar no prompt da API os rótulos de vídeo como se fossem uploads; a ordem dos arquivos enviados deve ser explicitada em linguagem natural.

Exemplo de comando **sem geração paga**:

```bash
python /CAMINHO/DA/SKILL/scripts/editar_imagem_openai.py \
  --image runs/caso/selecionados/frame-principal.png \
  --prompt-file runs/caso/edicao-principal.txt \
  --out runs/caso/referencias/imagem1.png \
  --model gpt-image-2.5-sunburst --size auto --quality high
```

O nome de frame acima é ilustrativo; utilize o caminho realmente extraído. O modelo é um exemplo documentado em 03/11/2026, não uma exigência ou autorização de gasto. Consulte a conta e os parâmetros aceitos. [3]

Para enviar a mesma operação depois da autorização, acrescente:

```text
--execute --ledger runs/caso/gastos-imagens.json --max-calls 3
```

O valor `3` é exemplo de máximo de tentativas autorizado, não de número obrigatório de referências. Use o limite que o usuário tiver aceitado. Tentativas incertas também contam. Não mudar o arquivo de registro para contornar o limite.

Abra a imagem produzida antes de usá-la como âncora. Ajuste apenas o que falhou e respeite o orçamento.

## C. Gerar outro ângulo

O primeiro arquivo é o frame original do novo ângulo. O segundo é a referência principal já editada:

```bash
python /CAMINHO/DA/SKILL/scripts/editar_imagem_openai.py \
  --image runs/caso/selecionados/frame-perfil.png \
  --reference runs/caso/referencias/imagem1.png \
  --prompt-file runs/caso/edicao-perfil.txt \
  --out runs/caso/referencias/imagem2.png \
  --model gpt-image-2.5-sunburst --size auto --quality high
```

Explique no prompt: a primeira imagem manda na pose, câmera e composição; a segunda manda no novo visual. Acrescente referências de cabelo/roupa quando necessário e permitido. Não force a pessoa de perfil a ficar de frente para copiar a âncora.

Conferir dimensões. `auto` não é garantia de proporção correta. Se a geração não respeitar a proporção, regenerar dentro do limite ou obter autorização para uma adaptação que não distorça a pessoa; jamais esticar silenciosamente. Os parâmetros de imagem dependem do modelo. [3]

## D. Escrever e validar o prompt final de vídeo

Prompt em português, sem campos a preencher, com `@video1` e as imagens realmente existentes. Associe a função de cada uma. Em modelos que exigem outra representação interna, preserve o mapa pedido e registre a adaptação necessária; não confundir rótulo textual e vínculo de arquivo.

```bash
python /CAMINHO/DA/SKILL/scripts/verificar_referencias.py runs/caso/prompt.txt --images 2
```

Só use `--max-chars` com o limite realmente documentado do campo.

## E. Fechar o pacote manual

Copie a estrutura de `examples/manifesto-manual.template.json` para `runs/caso/manifesto.json`. Preencha caminhos, metadados, evidências de revisão, função de cada imagem e características do modelo consultado. Todos os caminhos relativos são resolvidos a partir da pasta do manifesto.

`full_timeline_reviewed` e `visual_review_passed` são declarações do agente após inspeção; nunca podem ser marcados automaticamente pelo simples fato de os arquivos existirem. Não adote números ou confirmações dos templates como se tivessem sido medidos.

```bash
python /CAMINHO/DA/SKILL/scripts/empacotar_manual.py runs/caso/manifesto.json --check-only
python /CAMINHO/DA/SKILL/scripts/empacotar_manual.py runs/caso/manifesto.json --out runs/caso/entrega-manual
```

A saída inclui arquivos de imagem individuais e um ZIP. Entregue links reais ou caminhos realmente acessíveis ao usuário, o prompt completo e o mapa de upload. **Aqui termina o modo manual.** Não chamar o executor de vídeo.

## F. Automação por CLI

Consulte primeiro o catálogo e o esquema atual. O ID não é o nome informal do site.

```bash
python /CAMINHO/DA/SKILL/scripts/higgsfield_runner.py list
python /CAMINHO/DA/SKILL/scripts/higgsfield_runner.py inspect ID_REAL --out runs/caso/schema-higgsfield.json
```

Para operação do tipo workflow, use `--operation workflow` nas consultas. Nem todo modelo de vídeo edita um vídeo existente: confirme a operação, as entradas e seus limites. [6][7]

Preencha `plano-higgsfield.template.json` com esse esquema. Os campos `video_flag` e `image_flag` são nomes de opções do CLI sem `--`, confirmados pelo esquema atual. Por exemplo, um modelo pode usar `video-references` e `image-references`; outro pode usar `video` e `sketch`. Não reutilizar esses exemplos sem conferir. Operações que não se encaixam neste formato devem ser executadas com a ferramenta oficial apropriada pelo agente, sem inventar campos.

Simulação local, sem enviar:

```bash
python /CAMINHO/DA/SKILL/scripts/higgsfield_runner.py submit runs/caso/plano.json
```

Depois de obter custo real/estimado e autorização:

```bash
python /CAMINHO/DA/SKILL/scripts/higgsfield_runner.py submit runs/caso/plano.json \
  --execute --ledger runs/caso/gastos-video.json --max-calls 1 \
  --quoted-credits 40 --max-credits 50
```

**40 e 50 são exemplos de sintaxe, não preços.** Substituir por valores realmente consultados e autorizados. Se a estimativa não estiver disponível, não inventar zero; resolver com o usuário e usar um fluxo de autorização que exponha a incerteza. O wrapper exige estimativa para a rota paga que ele controla.

O envio é separado da espera para registrar o ID antes de acompanhar:

```bash
python /CAMINHO/DA/SKILL/scripts/higgsfield_runner.py get ID_REAL_DA_TAREFA --out runs/caso/status-01.json
python /CAMINHO/DA/SKILL/scripts/higgsfield_runner.py wait ID_REAL_DA_TAREFA --out runs/caso/status-final.json
```

Em caso de timeout ou formato de resposta desconhecido, examine o registro e o histórico. Não apagar o estado para reenviar às cegas.

## G. Obter e revisar

Extraia o URL real de resultado da resposta. Não construir URLs por padrão de nome.

```bash
python /CAMINHO/DA/SKILL/scripts/baixar_resultado.py --url 'URL_HTTPS_RETORNADO' --out runs/caso/resultado.mp4
```

URLs assinados podem expirar ou dar acesso a mídia privada. Não versionar respostas ou URLs no GitHub.

Compare original, saída e referências em toda a duração, aprofundando movimentos, espelhos e transições. Se precisar recolocar o áudio e a correspondência temporal tiver sido confirmada:

```bash
python /CAMINHO/DA/SKILL/scripts/restaurar_audio.py \
  --original original.mp4 --edited runs/caso/resultado.mp4 \
  --out runs/caso/resultado-com-audio.mp4 --timing-confirmed
```

O script não corrige ritmo ou sincronização, nem usa um corte silencioso para esconder durações divergentes. Ouça e reveja a versão final antes de entregar.

Fontes numeradas em `fontes.md`.
