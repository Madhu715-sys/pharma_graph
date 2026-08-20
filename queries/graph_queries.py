from database.connection import db_manager

def run_cypher(cypher: str, params: dict = None):
    driver = db_manager.get_driver()
    if not driver:
        return []
    with driver.session() as session:
        result = session.run(cypher, params or {})
        return [record.data() for record in result]

def get_graph_overview():
    cypher = """
    MATCH (n)-[r]->(m)
    RETURN 
        id(n) AS source_id, labels(n)[0] AS source_label, coalesce(n.name, n.code, n.patient_id) AS source_name,
        id(m) AS target_id, labels(m)[0] AS target_label, coalesce(m.name, m.code, m.patient_id) AS target_name,
        type(r) AS rel_type,
        coalesce(r.severity, '') AS rel_detail
    LIMIT 150
    """
    return run_cypher(cypher)

def check_patient_prescription_risk(patient_id: str, proposed_drug_id: str):
    cypher = """
    MATCH (p:Patient {patient_id: $patient_id})
    MATCH (target_drug:Drug {drug_id: $proposed_drug_id})

    OPTIONAL MATCH (p)-[:ALLERGIC_TO]->(allergy:ActiveIngredient)<-[:CONTAINS_INGREDIENT]-(target_drug)
    OPTIONAL MATCH (p)-[:CURRENTLY_TAKING]->(current_drug:Drug)-[interaction:INTERACTS_WITH]-(target_drug)

    RETURN 
        p.name AS patient_name,
        target_drug.name AS target_drug_name,
        collect(DISTINCT allergy.name) AS allergy_conflicts,
        collect(DISTINCT {
            existing_drug: current_drug.name,
            severity: interaction.severity,
            effect: interaction.effect
        }) AS interaction_conflicts
    """
    return run_cypher(cypher, {"patient_id": patient_id, "proposed_drug_id": proposed_drug_id})

def find_safe_alternative_drugs(patient_id: str, target_disease_name: str):
    cypher = """
    MATCH (p:Patient {patient_id: $patient_id})
    MATCH (disease:Disease) WHERE disease.name =~ ('(?i).*' + $target_disease_name + '.*')
    MATCH (candidate:Drug)-[:TREATS]->(disease)

    WHERE NOT EXISTS {
        MATCH (p)-[:ALLERGIC_TO]->(ing:ActiveIngredient)<-[:CONTAINS_INGREDIENT]-(candidate)
    }
    AND NOT EXISTS {
        MATCH (p)-[:CURRENTLY_TAKING]->(current:Drug)-[:INTERACTS_WITH]-(candidate)
    }

    RETURN 
        disease.name AS disease_treated,
        candidate.drug_id AS safe_drug_id,
        candidate.name AS safe_drug_name,
        candidate.dosage_form AS dosage
    """
    return run_cypher(cypher, {"patient_id": patient_id, "target_disease_name": target_disease_name})

def get_patient_profile(patient_id: str):
    cypher = """
    MATCH (p:Patient {patient_id: $patient_id})
    OPTIONAL MATCH (p)-[:DIAGNOSED_WITH]->(d:Disease)
    OPTIONAL MATCH (p)-[:CURRENTLY_TAKING]->(dr:Drug)
    OPTIONAL MATCH (p)-[:ALLERGIC_TO]->(a:ActiveIngredient)
    RETURN 
        p.patient_id AS patient_id,
        p.name AS name,
        p.age AS age,
        p.gender AS gender,
        collect(DISTINCT d.name) AS diagnoses,
        collect(DISTINCT dr.name) AS current_drugs,
        collect(DISTINCT a.name) AS allergies
    """
    return run_cypher(cypher, {"patient_id": patient_id})