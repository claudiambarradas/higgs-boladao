# Fontes técnicas e escopo de verificação

Documentação consultada em **03/11/2026**. Os critérios estéticos e a sequência do método vêm das instruções de Claudia Mendes nesta conversa. As fontes abaixo sustentam as integrações, não certificam o funcionamento deste pacote.

**[1] OpenAI — criação e descoberta local de skills.** Estrutura `SKILL.md`, recursos de apoio e localizações de descoberta do Codex.

```text
https://learn.chatgpt.com/docs/build-skills
https://developers.openai.com/codex/skills
```

**[2] Anthropic — skills no Claude Code.** Estrutura, comandos, diretórios locais e diferenças entre ambientes.

```text
https://code.claude.com/docs/en/skills
```

**[3] OpenAI — geração e edição de imagens.** Edição com arquivos, modelos/parâmetros e respostas da API. Consultar os modelos atuais antes de gerar.

```text
https://developers.openai.com/api/docs/guides/image-generation
https://developers.openai.com/api/reference/resources/images/methods/edit
```

**[4] Higgsfield — integração e transferência de arquivos.** MCP, CLI, autenticação e observação de que o anexo do Claude não é automaticamente upload para o Higgsfield.

```text
https://higgsfield.ai/enterprise-help-center/platform/integrations
https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-ai-agent
https://higgsfield.ai/CLI
```

**[5] Higgsfield — diferença entre uso no site, MCP/CLI e API.** Consumo de créditos; benefícios ilimitados do site não se aplicam à automação. Autorização por prompt não é teto técnico nativo de gasto.

```text
https://higgsfield.ai/creator-hub/help-center/integrations/what-is-higgsfield-mcp
https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-ai-agent
```

**[6] Higgsfield — CLI oficial.** Instalação, catálogo/esquemas, tarefas e comandos de consulta. O adaptador deve acompanhar a versão instalada.

```text
https://github.com/higgsfield-ai/cli/blob/main/README.md
```

**[7] Higgsfield — parâmetros e mídia.** Campos e limites de cada modelo; a descoberta em tempo de execução prevalece sobre exemplos.

```text
https://github.com/higgsfield-ai/cli/blob/main/MODELS.md
https://github.com/higgsfield-ai/skills/blob/main/higgsfield-generate/references/media-inputs.md
```

**[8] Anthropic — uso de skills no Claude.** Importação/ativação e requisitos do ambiente web, que não equivalem a instalar dependências locais.

```text
https://support.claude.com/en/articles/12512180-use-skills-in-claude
```

Os scripts de mídia foram conferidos executando `ffmpeg`/`ffprobe` no ambiente local descrito em `TESTES.md`. As imagens desta tarefa são apenas arquivos sintéticos dos testes; não foi gerada uma transformação visual real. Não houve autenticação nem teste de cobrança nos serviços externos.
