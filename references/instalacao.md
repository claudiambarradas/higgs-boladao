# Instalação e configuração

## 1. Ambiente suportado pelo desenho do pacote

Claude Code ou Codex com acesso a arquivos locais, Python, execução de processos e às conexões necessárias. A base `SKILL.md` é compartilhada; sessões, credenciais e ferramentas não são compartilhadas automaticamente entre os dois clientes. Os diretórios de descoberta utilizados seguem a documentação oficial. [1][2]

Este pacote não exige um framework de agentes adicional. Não cria servidor web, não abre porta local e não usa extensões que leem cookies do navegador.

## 2. Instalar a skill

Abra um terminal dentro da pasta `higgs-boladao` extraída do ZIP.

```bash
python3 install.py --agent claude --scope user
python3 install.py --agent codex --scope user
# Ou instalar nos dois:
python3 install.py --agent both --scope user
```

Destinos:

```text
Claude Code: ~/.claude/skills/higgs-boladao/SKILL.md
Codex:       ~/.agents/skills/higgs-boladao/SKILL.md
```

Para manter a skill em um projeto, use `--scope project --project /caminho/da/raiz-do-projeto`. Não escolha a própria pasta da skill como raiz; isso criaria instalação recursiva. O instalador impede esse caso.

No Windows, use `py` ou `python`, conforme sua instalação. As pastas de usuário ficam sob seu diretório pessoal. No WSL, instale no ambiente Linux do WSL em que o agente e os scripts serão executados; uma instalação do Windows não configura o ambiente Linux automaticamente.

Leia o arquivo instalado e procure a skill no cliente. Se ela não aparecer, recarregue/reinicie a sessão. Claude Code: `/higgs-boladao`. Codex: selecione a skill ou peça `Use $higgs-boladao`. Os clientes podem mudar a interface; a estrutura local é a base documentada. [1][2]

## 3. Dependências locais

Utilitários deste pacote: Python 3.10+, FFmpeg e FFprobe 6+, `Pillow` e `requests`. Não há instalador de FFmpeg embutido. Instale a distribuição apropriada ao sistema e verifique:

```bash
python3 --version
ffmpeg -version
ffprobe -version
```

Crie um ambiente Python na pasta de trabalho — separado de mídia e credenciais:

```bash
python3 -m venv .venv
# macOS / Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/doctor.py
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\doctor.py
```

Não é preciso alterar a política de execução do PowerShell para chamar diretamente o executável Python. Informe ao agente o caminho absoluto do Python desse ambiente; ativar um ambiente em um terminal não altera automaticamente um cliente já aberto.

Se instalar a skill em outra pasta, os comandos dos scripts devem usar o caminho real da instalação. O Python com as dependências pode continuar na pasta de trabalho.

## 4. Edição de imagens

### Rota nativa

Se o agente expuser uma ferramenta real de edição de imagens OpenAI com acesso aos arquivos, ele pode utilizá-la. Verifique a ferramenta e o caminho da imagem retornada. Não basta um modelo de texto dizer que gerou a imagem.

### API direta incluída no pacote

Configure `OPENAI_API_KEY` como segredo local e `OPENAI_IMAGE_MODEL` como o modelo de edição escolhido. `.env.example` é um modelo de configuração, não é carregado automaticamente e nunca deve conter sua chave real na distribuição.

O script `editar_imagem_openai.py` usa o endpoint oficial de edição, envia o frame e as referências como arquivos e salva o resultado em PNG. [3] Ele não usa sua conversa do ChatGPT, não importa memórias do chat e não promete o mesmo resultado da interface do ChatGPT. Acesso, cobrança, modelos e permissões são os da rota efetivamente configurada.

Teste primeiro sem `--execute`. Para uma chamada paga, o agente precisa de autorização, registro local e limite de tentativas. Veja `operacao.md`.

## 5. Higgsfield CLI

A documentação oficial orienta instalar o CLI, autenticar na conta e, opcionalmente, instalar as skills oficiais de apoio. [4][6]

```bash
npm install -g @higgsfield/cli
higgsfield auth login
higgsfield model list --json
```

Conclua o login no navegador oficial. Não entregue senha, cookie ou token ao agente. A instalação via npm depende de Node/npm disponíveis; a documentação oficial também oferece outras distribuições do CLI. Não é necessário instalar Node para a extração de frames ou a edição OpenAI por Python.

Skills oficiais de apoio são opcionais:

```bash
npx skills add higgsfield-ai/skills
```

Elas não substituem as regras da Higgs-boladao sobre imagens prontas, análise de movimento e referências sem espaços.

## 6. Claude com MCP

No cliente Claude que oferece conectores personalizados, conecte o servidor oficial:

```text
https://mcp.higgsfield.ai/mcp
```

Autorize a própria conta e faça uma consulta real, como saldo, para verificar. O fluxo MCP segue as ferramentas disponíveis na sessão; não depende do `higgsfield_runner.py`, que é um adaptador para CLI. No Claude web, um anexo do chat não equivale a upload no Higgsfield. Use o fluxo de upload/importação anunciado pelo conector. [4]

**Não há um servidor MCP de imagens OpenAI incluído neste ZIP.** No Claude Code, o script da API executado localmente fornece essa etapa. Em um Claude web sem execução/rede adequada, configure uma ferramenta de imagem acessível por MCP ou use a rota de imagens do Higgsfield expressamente escolhida. Não declare a automação pronta se essa conexão estiver faltando.

## 7. Claude web / importação de ZIP

O Claude oferece skills personalizadas em ambientes compatíveis, com requisitos de execução/criação de arquivos. [8] Importar o ZIP não instala FFmpeg no servidor, não autoriza acesso de rede e não transfere chaves do seu computador. A operação completa no web depende das ferramentas daquela sessão. Para a primeira implementação, prefira o ambiente local documentado acima.

## 8. Atualizar ou remover

Atualizar: execute o instalador da nova pasta com `--force`. Ele preserva a versão anterior em `skill-backups`, fora de `skills`, para não provocar descoberta duplicada.

Remover: depois de conferir o caminho exato, remova somente `higgs-boladao` do diretório de skills do agente. A skill não desconecta contas automaticamente; gerencie conexões e credenciais no serviço correspondente.

Fontes numeradas em `fontes.md`.
