# DB_READER

<img width="1600" height="867" alt="DB_READER" src="https://github.com/user-attachments/assets/2a11793c-db3e-4075-9aa0-ae5808b79997" />

## 📌 Sobre o projeto

O **DB_READER** é um sistema inteligente de Business Intelligence que utiliza **Inteligência Artificial para permitir consultas a bancos de dados por meio de linguagem natural**.

A proposta é facilitar o acesso e a interpretação de informações armazenadas em bancos de dados, permitindo que o usuário faça perguntas de forma simples, sem precisar conhecer a linguagem SQL.

A partir da pergunta realizada pelo usuário, o sistema utiliza Inteligência Artificial para gerar uma consulta SQL, executá-la no banco de dados e apresentar o resultado de forma compreensível.

Além do resultado da consulta, o sistema possibilita a geração de **gráficos** e a **exportação dos dados para CSV**.

---

## 🎯 Objetivo

Desenvolver um sistema de Business Intelligence capaz de utilizar Inteligência Artificial para transformar perguntas realizadas em linguagem natural em consultas SQL, permitindo a obtenção e interpretação de informações empresariais de maneira mais simples e acessível.

---

## 💡 Funcionamento

O sistema segue o seguinte fluxo:

**Pergunta em linguagem natural**
↓
**Processamento pela Inteligência Artificial**
↓
**Geração da consulta SQL**
↓
**Execução no banco de dados**
↓
**Apresentação do resultado**
↓
**Geração de gráfico ou exportação para CSV**

O projeto também utiliza técnicas de **RAG (Retrieval-Augmented Generation)** para fornecer informações sobre a estrutura do banco de dados à Inteligência Artificial, auxiliando na geração das consultas.

---

## 🧠 Inteligência Artificial

O projeto utiliza o modelo **Llama 3.1**, executado localmente por meio do **Ollama**.

A utilização de um modelo local permite que o processamento das perguntas e a geração das consultas SQL sejam realizados no ambiente do projeto.

---

## 🗄️ Banco de dados

O sistema utiliza **MySQL** como banco de dados.

A principal tabela utilizada pelo projeto é:

### `vendas`

| Campo        | Tipo    |
| ------------ | ------- |
| `id`         | INT     |
| `produto`    | VARCHAR |
| `preco`      | DECIMAL |
| `marca`      | VARCHAR |
| `modelo`     | VARCHAR |
| `quantidade` | INT     |

---

## 🛠️ Tecnologias utilizadas

- **Python**
- **MySQL**
- **Ollama**
- **Llama 3.1**
- **LangChain**
- **ChromaDB**
- **Pandas**
- **Matplotlib**
- **Seaborn**
- **CustomTkinter**

---

## 📂 Estrutura do projeto

```text
DB_READER/
│
├── interface/
│   └── app.py
│
├── TCC/
│   ├── DB/
│   │   ├── connect.py
│   │   ├── create.py
│   │   ├── insert.py
│   │   └── itens.py
│   │
│   ├── STORE_AI/
│   │   ├── charts.py
│   │   ├── exports.py
│   │   ├── llm.py
│   │   └── rag.py
│   │
│   ├── pipeline.py
│   └── main.py
│
├── chroma_db/
├── TCC.sql
├── requirements.txt
├── README.md
├── .gitignore
└── .gitattributes
```
