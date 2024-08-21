from neo4j import GraphDatabase

class NeoDB:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def insert_entities_and_relationships(self, entities):
        with self.driver.session() as session:
            # Insert entities (nodes)
            for entity in entities:
                entity_group = entity['entity_group']
                word = entity['word']
                session.write_transaction(self.create_entity, entity_group, word)
            
            # Create relationships
            for entity in entities:
                entity_group = entity['entity_group']
                word = entity['word']
                self.create_relationships(session, entity_group, word, entities)

    @staticmethod
    def create_entity(tx, entity_group, word):
        query = f"MERGE (e:{entity_group} {{value: $word}})"
        tx.run(query, word=word)

    @staticmethod
    def create_relationships(session, entity_group, word, entities):
        if entity_group == 'Organization':
            pass  # No specific relationships for Organization in the provided data
        elif entity_group == 'Circular':
            org_word = next((e['word'] for e in entities if e['entity_group'] == 'Organization'), None)
            if org_word:
                session.write_transaction(NeoDB.create_relationship, 'Organization', org_word, 'ORGANIZATION_HAS_CIRCULAR', 'Circular', word)
        elif entity_group == 'Reference':
            circular_word = next((e['word'] for e in entities if e['entity_group'] == 'Circular'), None)
            if circular_word:
                session.write_transaction(NeoDB.create_relationship, 'Circular', circular_word, 'CIRCULAR_REFERENCES', 'Reference', word)
        elif entity_group == 'Date':
            circular_word = next((e['word'] for e in entities if e['entity_group'] == 'Circular'), None)
            if circular_word:
                session.write_transaction(NeoDB.create_relationship, 'Circular', circular_word, 'CIRCULAR_ISSUED_ON', 'Date', word)
        elif entity_group == 'Reader':
            circular_word = next((e['word'] for e in entities if e['entity_group'] == 'Circular'), None)
            if circular_word:
                session.write_transaction(NeoDB.create_relationship, 'Circular', circular_word, 'CIRCULAR_HAS_READER', 'Reader', word)
        elif entity_group == 'Topic':
            circular_word = next((e['word'] for e in entities if e['entity_group'] == 'Circular'), None)
            if circular_word:
                session.write_transaction(NeoDB.create_relationship, 'Circular', circular_word, 'CIRCULAR_HAS_TOPIC', 'Topic', word)
        elif entity_group == 'Content':
            topic_word = next((e['word'] for e in entities if e['entity_group'] == 'Topic'), None)
            if topic_word:
                session.write_transaction(NeoDB.create_relationship, 'Topic', topic_word, 'TOPIC_HAS_CONTENT', 'Content', word)
        elif entity_group == 'Subject':
            circular_word = next((e['word'] for e in entities if e['entity_group'] == 'Circular'), None)
            if circular_word:
                session.write_transaction(NeoDB.create_relationship, 'Circular', circular_word, 'CIRCULAR_HAS_SUBJECT', 'Subject', word)
        elif entity_group == 'SignedBy':
            circular_word = next((e['word'] for e in entities if e['entity_group'] == 'Circular'), None)
            if circular_word:
                session.write_transaction(NeoDB.create_relationship, 'Circular', circular_word, 'CIRCULAR_SIGNED_BY', 'SignedBy', word)
        elif entity_group == 'Designation':
            signed_by_word = next((e['word'] for e in entities if e['entity_group'] == 'SignedBy'), None)
            if signed_by_word:
                session.write_transaction(NeoDB.create_relationship, 'SignedBy', signed_by_word, 'PERSON_HAS_DESIGNATION', 'Designation', word)
        elif entity_group == 'OrgID':
            org_word = next((e['word'] for e in entities if e['entity_group'] == 'Organization'), None)
            if org_word:
                session.write_transaction(NeoDB.create_relationship, 'Organization', org_word, 'ORGANIZATION_HAS_ORGID', 'OrgID', word)
        else:
            # Handle other entity groups or raise an exception if needed
            pass

    @staticmethod
    def create_relationship(tx, from_entity_type, from_entity_value, relationship_type, to_entity_type, to_entity_value):
        query = (
            f"MATCH (a:{from_entity_type} {{value: $from_entity_value}}), (b:{to_entity_type} {{value: $to_entity_value}}) "
            f"MERGE (a)-[r:{relationship_type}]->(b)"
        )
        tx.run(query, from_entity_value=from_entity_value, to_entity_value=to_entity_value)
