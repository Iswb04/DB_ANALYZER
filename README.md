
# DB ANALYZER
Aplicação desktop para consultar um estoque no **MySQL usando perguntas em português**, com inteligência artificial executada localmente pelo **Ollama**.

<img width="443" height="520" alt="Captura de tela 2026-10-28 184603" src="https://github.com/user-attachments/assets/85a4d65f-4333-4464-b7fe-911c4689a2df" />
<img width="441" height="524" alt="Captura de tela 2026-10-28 184521" src="https://github.com/user-attachments/assets/801c2020-638a-4f1a-abb5-f74640b7ff6b" />
<img width="1919" height="1025" alt="image1_DB" src="https://github.com/user-attachments/assets/6119d016-7b0c-42ba-a30e-91e371c0b6ab" />
<img width="1909" height="892" alt="image2_DB" src="https://github.com/user-attachments/assets/93aa627c-3366-476c-aca5-9fb75fa44405" />

<img width="1737" height="952" alt="Captura de tela 2026-10-28 184345" src="https://github.com/user-attachments/assets/f9e0ae53-5240-48c5-9c75-88478d0c418d" />




## Sobre o projeto

O DB Reader utiliza **NL2SQL** (*Natural Language to SQL*) para transformar perguntas em consultas SQL e apresentar os resultados em linguagem natural.

Para contextualizar a IA, utiliza **RAG** com documentos da pasta `knowledge`, que descrevem a estrutura do banco, as regras do estoque e exemplos de consultas. Esses documentos são indexados no banco vetorial **ChromaDB** por meio de **embeddings**.

A coluna `quantidade` representa **unidades disponíveis em estoque**. O projeto não possui histórico de vendas.

## Funcionalidades

- Consultas ao estoque usando perguntas em português.
- Consultas SQL predefinidas para perguntas frequentes.
- Validação de SQL antes da execução, restringindo a leitura à tabela `produtos`.
- Explicação dos resultados com IA.
- Geração de gráficos em PNG.
- Exportação dos resultados em CSV.
- Interface desktop com cancelamento cooperativo.

## Tecnologias

| Categoria | Tecnologias |
|---|---|
| Linguagem | Python |
| Banco de dados | MySQL |
| Execução de IA local | Ollama |
| Geração de SQL | Qwen2.5 |
| Explicação dos resultados | Llama3.2 |
| RAG | LangChain e ChromaDB |
| Embeddings | nomic-embed-text |
| Manipulação de dados | Pandas |
| Gráficos | Plotly e Kaleido |
| Interface | CustomTkinter e Tkinter |

## Como funciona

1. A interface recebe a pergunta.
2. O pipeline identifica se existe uma consulta predefinida.
3. Quando necessário, o RAG recupera contexto e o modelo gera o SQL.
4. O pipeline valida a consulta e executa a leitura no MySQL.
5. O resultado é apresentado diretamente ou explicado pela IA.
6. O usuário pode gerar um gráfico ou exportar um CSV.

## Estrutura

```text
DB_ANALYZER/
├── core/
│   ├── pipeline.py
│   ├── DB/
│   │   ├── create.py
│   │   ├── insert.py
│   │   └── itens.py
│   └── STORE_AI/
│       ├── llm.py
│       ├── rag.py
│       ├── charts.py
│       └── exports.py
├── interface/
│   └── app.py
├── knowledge/
│   ├── schema.md
│   ├── regras_negocio.md
│   └── exemplos_consultas.md
├── requirements.txt
├── FUNCTION.txt
├── CHANGES.TXT
└── EXECUTAR.txt
```

## Instalação

### Pré-requisitos

- Python 3.12 com Tkinter.
- MySQL.
- Ollama.
- Google Chrome ou Chromium para exportar gráficos PNG.

### Instalar as dependências

Na raiz do projeto:

```powershell
py -3.12 -m pip install -r requirements.txt
```

### Configurar o banco

Crie um arquivo `.env` na raiz:

```env
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

Com o MySQL em execução, crie o banco e a tabela:

```powershell
py -3.12 -m core.DB.create
```

Para inserir o catálogo inicial, caso a tabela esteja vazia:

```powershell
py -3.12 -m core.DB.insert
```

### Baixar os modelos

```powershell
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Executar

Com o MySQL e o Ollama em execução:

```powershell
py -3.12 -m interface.app
```

## Exemplos de perguntas

```text
Mostre todos os produtos.
Quero itens disponíveis.
Quantos produtos estão cadastrados?
Quantas unidades há em estoque?
Qual produto tem maior estoque?
Qual é o produto mais caro?
Qual é o valor total do estoque?
```
