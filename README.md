# Higgs-boladao

**Transformação de visual em vídeos existentes — método de Claudia Mendes.**

Versão **0.1.0** • 03/11/2026 • manual assistido + automação opcional.

Comece por **[COMECE-AQUI.md](COMECE-AQUI.md)**. A instrução principal do agente está em **[SKILL.md](SKILL.md)**.

## O produto

Isto é um pacote de Agent Skill: instruções, utilitários executáveis, critérios visuais, exemplos e testes. Claude Code ou Codex faz a interpretação do pedido, a análise visual, a seleção das referências e a escrita dos prompts. Os scripts cuidam de arquivos, validações e chamadas às ferramentas configuradas.

**Não é um gerador de filmes do zero, um plugin já instalado na sua conta, um servidor MCP próprio ou um programa autônomo que toma todas as decisões estéticas sem um agente.** O pacote não contém credenciais, não publica nada e não conecta contas automaticamente.

### Entregas possíveis

| Modo | Trabalho do agente | Trabalho do usuário |
|---|---|---|
| Manual | Analisa o vídeo, gera as imagens modificadas, revisa, monta prompt e pacote pronto | Faz upload no Higgsfield, associa as referências e inicia a edição |
| Prévia | Faz a mesma preparação e apresenta as referências antes do envio | Aprova o visual e o gasto da próxima etapa |
| Automático | Faz a preparação, envia a tarefa autorizada, consulta o estado, baixa o vídeo e revisa | Configura contas, escolhe modelo e autoriza limites |

## Conteúdo

```text
higgs-boladao/
├── SKILL.md
├── COMECE-AQUI.md
├── README.md
├── install.py
├── requirements.txt
├── .env.example
├── .gitignore
├── VERSION
├── CHANGELOG.md
├── TESTES.md
├── agents/openai.yaml
├── scripts/
│   ├── _common.py
│   ├── doctor.py
│   ├── video_frames.py
│   ├── editar_imagem_openai.py
│   ├── verificar_referencias.py
│   ├── empacotar_manual.py
│   ├── higgsfield_runner.py
│   ├── baixar_resultado.py
│   └── restaurar_audio.py
├── references/
│   ├── instalacao.md
│   ├── operacao.md
│   ├── selecao-de-frames.md
│   ├── fidelidade-visual.md
│   ├── integracoes.md
│   ├── seguranca-e-custos.md
│   ├── distribuicao.md
│   └── fontes.md
├── examples/
│   ├── manifesto-manual.template.json
│   ├── plano-higgsfield.template.json
│   └── pedidos-e-prompts.md
└── tests/
    ├── test_local.py
    └── test_integrations_mock.py
```

## Instalação local

```bash
python3 install.py --agent both --scope user --dry-run
python3 install.py --agent both --scope user
```

O instalador copia a mesma base para os diretórios locais documentados do Claude Code e do Codex. [1][2] Não altera outros arquivos de configuração. Atualizações exigem `--force` e preservam um backup fora da pasta de skills. Instalação e reconhecimento dentro de cada cliente ainda devem ser conferidos no computador do usuário.

Dependências, autenticação e variantes de Windows estão em `references/instalacao.md`.

## Verificar sem gerar mídia paga

Dentro da pasta do pacote, com o Python do ambiente configurado:

```bash
python3 scripts/doctor.py
python3 -m unittest discover -s tests -v
```

Os testes não usam as suas contas. A suíte cria vídeos sintéticos e simula respostas de API/CLI. A ferramenta de diagnóstico não mostra chaves nem faz login.

## Limites intencionais

O extrator não reconhece automaticamente perfil, rosto ou espelho: ele entrega mídia e indicadores para o agente examinar. Uma folha de contatos não é a referência final. Amostrar toda a linha do tempo não equivale a assistir a cada frame; trechos rápidos exigem refinamento.

Os verificadores locais conferem estrutura e arquivos, não provam identidade facial ou qualidade estética. Campos de revisão precisam ser preenchidos após inspeção real, nunca para apenas passar na validação.

O executor do Higgsfield utiliza um plano com os campos do modelo consultado em tempo de execução, em vez de prometer que todos os modelos aceitam o mesmo vídeo, áudio, número de imagens ou conjunto de arrobas. Modelos e parâmetros não são congelados nesta skill. O CLI oficial aceita consultas de catálogo/esquema e operações de geração com arquivos de mídia; verifique o esquema atual antes de enviar. [6][7]

O bloqueio de duplicação é **local**, não uma chave de idempotência garantida pelo provedor. Se houver timeout, consultar a tarefa/histórico. Não apagar registros para tentar novamente sem verificar.

## Distribuir

O pacote pode ser versionado como uma pasta de repositório ou entregue em ZIP. Não há licença de código aberto atribuída automaticamente, nem publicação no GitHub realizada por este pacote. Claudia decide o público e as condições de distribuição. Veja `references/distribuicao.md`.

Documentação consultada: `references/fontes.md`. Testes executados e pendências: `TESTES.md`.
