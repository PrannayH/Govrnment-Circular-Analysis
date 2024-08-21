import spacy

class FNER:
    def __init__(self, model_path):
        self.nlp = spacy.load(model_path)  # Load the custom-trained SpaCy NER model
        self.entity_mapping = {
            "IORG": "Organization",
            "ISD": "Date",
            "NNO": "Circular",
            "TOPIC": "Topic",
            "SUB": "Subject",
            "RTO": "Reader",
            "WRT": "Reference",
            "SBY": "SignedBy",
            "SDESG": "Designation",
            "CIN": "OrgID",
            "PCO": "Content"
        }

    def combine_spacy_entities(self, doc):
        combined_entities = []
        for ent in doc.ents:
            entity_label = self.entity_mapping.get(ent.label_, ent.label_)  # Map the label if it exists in the mapping
            combined_entities.append({"entity_group": entity_label, "word": ent.text})
        return combined_entities

    def perform_ner(self, text):
        doc = self.nlp(text)  # Perform NER using SpaCy
        combined_entities = self.combine_spacy_entities(doc)  # Process and combine NER results
        return combined_entities
