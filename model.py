import torch
import ollama


def promptLLM(context: str, USER_prompt : str) ->list[dict]:
    #Build a grounded Romanian chat prompt from retrieved passages.
    messages=[
        {
            "role":"system",
            "content":(
"Răspunde în română.Identifică ce întreabă utilizatorul și selectează doar pasajele care oferă dovezi directe pentru răspuns. Ignoră pasajele fără legătură.Răspunde direct și concis, folosind exclusiv informațiile din pasajele selectate. Nu combina persoane sau evenimente distincte, nu transforma acuzațiile în fapte dovedite și nu prezenta evenimentele planificate ca fiind deja întâmplate.Dacă pasajele selectate nu oferă un răspuns sigur, precizează ce informație lipsește. Nu inventa și nu rezuma contextul în ansamblu."
"Dacă există pasaje relevante, rezumă-le direct în loc să spui că informația lipsește"
"Leagă fiecare afirmație de subiectul și evenimentul exact din întrebare."
"Nu combina informații din articole despre persoane sau evenimente diferite."
"Dacă pasajele nu oferă dovezi directe despre subiectul cerut, spune că informația nu apare în context."
"Prioritizeaza articolele recente ca data"
                    ),
        },
        {
            "role":"user",
            # Qwen3 recognizes /no_think as a request to skip reasoning output.
            "content":f"""/no_think
            Context:
            {context}

        Întrebare: {USER_prompt}
        Răspuns:"""
        }
    ]
    return messages


def generateAnswer(prompt : list[dict]) ->str:
    #Send the prompt to the locally running Ollama model and return its text.
    response=ollama.chat(model="qwen3:8b",
                         messages=prompt)
    return response.message.content


