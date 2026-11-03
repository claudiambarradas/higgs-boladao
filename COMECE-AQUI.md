# Higgs-boladao
## Seu vídeo. Outro visual. Sem refazer a gravação.

**Método de Claudia Mendes • material para a SIA • versão 0.1.0**

A skill recebe um vídeo existente e uma transformação desejada. O agente estuda a linha do tempo, escolhe os prints que realmente importam, edita as referências e escreve o prompt. Uma pessoa parada pode precisar de uma referência; alguém que gira, mostra as costas ou aparece no espelho pode precisar de várias.

**Manual não significa que você precisa criar as imagens.** A skill entrega as imagens editadas, os arquivos individuais, o prompt completo e o mapa de upload. Você só faz a etapa final no site do Higgsfield. Na automação completa, o agente também envia a geração e obtém o resultado, depois de configurar e autorizar as ferramentas.

## O que instalar

Este pacote foi preparado para **Claude Code e Codex com execução local de scripts**. É uma skill que orienta o agente, não um aplicativo que funciona sozinho ao dar dois cliques.

Baixe e extraia o ZIP. Abra a pasta `higgs-boladao` no seu agente e envie:

> Leia COMECE-AQUI.md e references/instalacao.md. Verifique meu ambiente e instale esta skill para o agente que estou usando. Antes de instalar dependências ou conectar contas, explique o necessário. Não gere imagens ou vídeos pagos durante a instalação. Depois, confirme a instalação lendo o SKILL.md da pasta de destino.

Ou, no terminal **dentro da pasta extraída**, execute:

```bash
# Instalar a mesma base nos dois agentes; não conecta contas nem gera mídia.
python3 install.py --agent both --scope user
```

No Windows, pode ser necessário usar `py` no lugar de `python3`. Para apenas um agente, troque `both` por `claude` ou `codex`. Os caminhos utilizados são os documentados pelos próprios produtos: `~/.claude/skills/higgs-boladao` e `~/.agents/skills/higgs-boladao`. [1][2]

## Configurar uma vez

O agente precisa de **Python 3.10 ou superior, FFmpeg/FFprobe 6 ou superior e as dependências de `requirements.txt`** para os utilitários deste pacote. As versões efetivamente testadas estão em `TESTES.md`.

Para criar as imagens, configure uma destas rotas:

**Ferramenta nativa de edição OpenAI**, quando ela realmente estiver disponível no ambiente do agente; ou **API de imagens OpenAI**, usando sua própria chave no ambiente local. A segunda rota tem um script incluído. O agente não deve solicitar que você cole a chave no chat. O exemplo da API é edição com imagens reais de entrada, não geração apenas por texto. [3]

Para automatizar também o vídeo, conecte **o CLI ou o MCP oficial do Higgsfield**. Uma conexão com o Higgsfield não conecta automaticamente sua conta OpenAI. No Claude web, anexar o arquivo só ao chat não garante que o Higgsfield o recebeu; é preciso o upload oficial da integração. [4]

**Custo:** a geração pelo Higgsfield via CLI/MCP usa créditos, inclusive quando há uso ilimitado daquele modelo no site. As imagens também podem consumir créditos na rota escolhida. Não há um teto de cobrança do provedor imposto por esta skill: há instruções de autorização, limite local de tentativas e verificação de estimativa. [5]

## Primeiro pedido: modo manual

No Claude Code:

```text
/higgs-boladao
Prepare o pacote manual deste vídeo. Quero trocar minha roupa por um
vestido preto com brilho e manter meu rosto, cabelo e cenário.
Estude o vídeo inteiro e gere quantas referências forem realmente
necessárias. Entregue as imagens editadas prontas, o prompt completo
com @video1 e @imagem1, @imagem2 etc. e o mapa de upload.
Não envie a geração do vídeo ao Higgsfield.
```

No Codex, substitua a primeira linha por `$higgs-boladao`, ou peça em linguagem natural para usar a skill. Acrescente o modelo de edição que deseja usar; sem essa escolha, o agente deve resolvê-la antes de fechar os parâmetros.

O agente usa o seu vídeo e preenche os arquivos técnicos. **Você não precisa editar o manifesto JSON.** Os arquivos em `examples/` são moldes de trabalho do agente, não tarefas de casa para o aluno.

## Primeiro pedido: automação

```text
Use Higgs-boladao no modo automático para este vídeo, com a mudança
que descrevi. Use o modelo de edição que eu escolher, preserve a
proporção original e o áudio. Verifique ferramentas, limites e custo
antes de gerar. Após minha autorização, prossiga dentro do limite
combinado, obtenha o arquivo e confira o resultado antes de entregar.
```

A primeira autenticação e a autorização de gastos continuam sendo suas. Depois da configuração, o agente pode executar as etapas autorizadas sem perguntar a mesma coisa a cada arquivo.

## O que receber no modo manual

`imagem1.png` e, quando necessárias, `imagem2.png`, `imagem3.png` etc.; `prompt.txt`; `MAPA-DE-UPLOAD.md`; `configuracoes.json`; e um ZIP com a entrega. O vídeo original não é duplicado por padrão.

No prompt, os nomes são **`@video1` sem acento e sem espaço**, e **`@imagem1`, `@imagem2`, `@imagem3`**, sempre juntos. Esses nomes são o mapa de referência; associe os arquivos no seletor da plataforma, pois escrever uma arroba não faz upload.

## Estado desta versão

Os utilitários locais foram testados com mídia sintética; as chamadas externas foram simuladas. **A geração real OpenAI → Higgsfield ainda exige um teste com as contas conectadas.** Não trate este ZIP como uma automação já homologada nos serviços ou uma garantia de resultado visual perfeito.

Referências: [1] e [2] instalação; [3] edição de imagens; [4] integração; [5] créditos. Consulte `references/fontes.md`.
