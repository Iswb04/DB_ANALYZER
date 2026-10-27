from pathlib import Path
import hashlib

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
CHROMA_DIR = BASE_DIR / "chroma_db"


def carregar_documentos():
    return [Document(page_content=arquivo.read_text(encoding="utf-8"),
                     metadata={"arquivo": arquivo.name})
            for arquivo in sorted(KNOWLEDGE_DIR.glob("*.md"))]


def dividir_documentos(documentos):
    return RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(documentos)


def criar_rag():
    arquivos = sorted(KNOWLEDGE_DIR.glob("*.md"))
    if not arquivos:
        raise RuntimeError("Nenhum documento encontrado na pasta knowledge.")

    # O nome da coleção muda quando qualquer documento é editado.
    # Assim, nunca reutilizamos embeddings gerados a partir de regras antigas.
    digest = hashlib.sha256()
    for arquivo in arquivos:
        digest.update(arquivo.name.encode("utf-8"))
        digest.update(arquivo.read_bytes())
    colecao = "knowledge_" + digest.hexdigest()[:16]

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(collection_name=colecao,
                         persist_directory=str(CHROMA_DIR),
                         embedding_function=embeddings)
    if vectorstore._collection.count() == 0:
        vectorstore.add_documents(dividir_documentos(carregar_documentos()))
    return vectorstore


def buscar_contexto(pergunta, quantidade=3):
    resultados = criar_rag().similarity_search(pergunta, k=quantidade)
    return "\n\n".join(documento.page_content for documento in resultados)


if __name__ == "__main__":
    pergunta = input("Digite uma pergunta: ")
    print(buscar_contexto(pergunta))
