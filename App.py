from pprint import pprint
from retrieval import embeddQuery, returnMatches
from model import promptLLM, generateAnswer


def useLLM():
    #Retrieve evidence for one question and print the model's answer.
    USER_prompt=input("Waiting on question:")
    # Embed the question with the same BGE-M3 model used to build the index.
    Matches_RAG=returnMatches(embeddQuery(USER_prompt), 7)
    full_content=[]
    for match in Matches_RAG:
        documents = match["documents"][0]
        metadatas = match["metadatas"][0]


        for text_content, metadata in zip(documents, metadatas):
            # Keep source metadata beside each retrieved article passage.
            full_content.append(
                f"Date={metadata['date_of_processing']}\n"
                f"Domain={metadata['domain']}\n"
                f"Url={metadata['url']}\n"
                f"News:{text_content}"
            )
    full_content="\n\n".join(full_content)
    messages=promptLLM(full_content, USER_prompt)
    output=generateAnswer(messages)
    print(output)
    # Print evidence for inspection while developing the RAG pipeline.
    print("\n\n", full_content)
   
    
    

