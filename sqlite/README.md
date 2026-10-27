# DB Reader — consultas de produtos e estoque

Aplicação desktop Python para consultar a tabela SQLite `produtos` (arquivo `store.db`) em linguagem natural, usando Ollama e RAG (ChromaDB). **Não há histórico de vendas.** `quantidade` é estoque disponível.

## Instalação

1. Instale Python 3.12+ e Ollama.
2. Na raiz do projeto: `python -m pip install -r requirements.txt`.
3. Configure `DB_PATH` no `.env` caso queira alterar o caminho do arquivo SQLite.
4. Baixe os modelos: `ollama pull qwen2.5:3b`, `ollama pull llama3.2:3b`, `ollama pull nomic-embed-text`.
5. Crie a tabela: `python -m core.DB.create`.
6. Para inserir a lista inicial **somente se a tabela estiver vazia**: `python -m core.DB.insert`.
7. Abra a interface: `python -m interface.app`.

O ChromaDB é gerado automaticamente na primeira consulta com RAG; não é distribuído no ZIP. Falhas técnicas são registradas em `erro_pipeline.log` (não aparecem no terminal). Gráficos e CSV são salvos em Downloads.

## Consultas

- `quero itens disponíveis`: lista produtos com `quantidade > 0`.
- `mostre todos os produtos`: lista o catálogo.
- `quantos itens tem no banco`: conta registros/modelos.
- `quantas unidades há em estoque`: soma unidades.
- `quantos itens foram vendidos`: informa que não há histórico de vendas.

## Segurança e limites

A validação de SQL permite apenas consultas SELECT simples à tabela `produtos`. O botão Cancelar solicita cancelamento cooperativo: uma chamada já em andamento ao Ollama ou SQLite pode precisar terminar antes de parar.
