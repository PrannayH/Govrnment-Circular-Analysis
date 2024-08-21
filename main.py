from ocr import POCR
from ner import FNER
from neodb import NeoDB
from embed import Embed
from vector_db import VectorDB

if __name__ == "__main__":
    pdf_path = 'temp.pdf'  # Replace with your PDF file path
    model_path = "output_model55"  # Path to your custom-trained SpaCy NER model

    # Aura instance credentials
    aura_uri = "neo4j+s://3e84cc7b.databases.neo4j.io"
    aura_username = ""
    aura_password = ""

    # Perform OCR
    pdf_processor = POCR(pdf_path)
    ocr_texts = pdf_processor.perform_ocr()
    print("OCR Outputs: \n", ocr_texts)
    print("OCR DONE\n")

    # Perform NER on OCR output
    fner_processor = FNER(model_path)
    entities = fner_processor.perform_ner(ocr_texts)
    print(entities)
    print("NER Results for given text:\n")  # Print the text and NER results
    for entity in entities:
        print(f"{entity['entity_group']} : {entity['word']}")
    print("NER DONE\n")

    # Concatenate entity values in the specified format
    concatenated_text = "\n".join([f"{entity['entity_group']} : {entity['word']}" for entity in entities])
    print("Concatenated Text:\n", concatenated_text)

    # Insert entities and relationships into Neo4j Aura
    neo_db = NeoDB(aura_uri, aura_username, aura_password)
    neo_db.insert_entities_and_relationships(entities)
    neo_db.close()

    # # Embed the concatenated text into FAISS
    # embed = Embed()
    # embed.add_to_index([concatenated_text])
    # embed.save_index('faiss_index.bin')
    # print("Embedding DONE\n")

    # # Example query
    # query = "What is the topic of the circular?"

    # # Perform search in FAISS index
    # vectordb = VectorDB('faiss_index.bin')
    # top_k_indices, entities = vectordb.search(query, k=3)  # Adjust k as needed for top-k results
    
    # print("Search Results for the query:\n")
    # for idx, entity in zip(top_k_indices[0], entities):
    #     print(f"Index: {idx}, Entity: {entity}")
