from pipeline import rodar_pipeline

while True:
    pergunta = input("\nPergunta (ou 'sair'): ")

    if pergunta.lower() == "sair":
        break

    rodar_pipeline(pergunta)