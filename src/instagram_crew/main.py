import os
from dotenv import load_dotenv
from instagram_crew.crew import InstagramCrew

load_dotenv()

def run():
    load_dotenv()

    topic = input("¿Sobre qué tema quieres publicar en Instagram hoy? → ").strip()

    if not topic:
        print("Debes ingresar un tema.")
        return

    print(f"\nIniciando crew para el tema: '{topic}'\n{'='*50}\n")

    result = InstagramCrew().crew().kickoff(inputs={
        "topic": topic,
        "account_id": os.environ.get("INSTAGRAM_ACCOUNT_ID")
    })

    print(f"\n{'='*50}")
    print("PROCESO COMPLETADO")
    print(f"{'='*50}")
    print(result)

if __name__ == "__main__":
    run()