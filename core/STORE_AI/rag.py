from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parents[2]

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
CHROMA_DIR = BASE_DIR / "chroma_db"


def carregar_documentos():
    documentos = []

    for arquivo in KNOWLEDGE_DIR.glob("*.md"):
        texto = arquivo.read_text(encoding="utf-8")

        documentos.append(
            Document(
                page_content=texto,
                metadata={
                    "arquivo": arquivo.name
                }
            )
        )

    return documentos


def dividir_documentos(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    return splitter.split_documents(documentos)


def criar_rag():
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    # Se o banco vetorial já existe, apenas carrega.
    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):

        vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings
        )

        return vectorstore

    # Se ainda não existe, cria pela primeira vez.
    documentos = carregar_documentos()

    documentos_divididos = dividir_documentos(documentos)

    vectorstore = Chroma.from_documents(
        documents=documentos_divididos,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR)
    )

    return vectorstore


def buscar_contexto(pergunta, quantidade=3):

    vectorstore = criar_rag()

    resultados = vectorstore.similarity_search(
        pergunta,
        k=quantidade
    )

    contexto = "\n\n".join(
        documento.page_content
        for documento in resultados
    )

    return contexto


if __name__ == "__main__":

    pergunta = input("Digite uma pergunta: ")

    contexto = buscar_contexto(pergunta)

    print("\n--- CONTEXTO ENCONTRADO ---\n")

    print(contexto)