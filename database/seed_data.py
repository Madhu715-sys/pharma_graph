from database.connection import db_manager

def seed_medical_graph():
    driver = db_manager.get_driver()
    if not driver:
        print("[!] Database is unreachable. Verify credentials.")
        return

    try:
        with driver.session() as session:
            print("Applying unique constraints and resetting graph...")
            session.run("MATCH (n) DETACH DELETE n")

            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Patient) REQUIRE p.patient_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disease) REQUIRE d.code IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (dr:Drug) REQUIRE dr.drug_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (i:ActiveIngredient) REQUIRE i.ing_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE")

            print("Seeding medical entities and interaction network...")
            seed_cypher = """
            // 1. Active Ingredients
            MERGE (ing_asp:ActiveIngredient {ing_id: 'ING_001', name: 'Acetylsalicylic Acid'})
            MERGE (ing_clop:ActiveIngredient {ing_id: 'ING_002', name: 'Clopidogrel Bisulfate'})
            MERGE (ing_warf:ActiveIngredient {ing_id: 'ING_003', name: 'Warfarin Sodium'})
            MERGE (ing_ibu:ActiveIngredient {ing_id: 'ING_004', name: 'Ibuprofen'})
            MERGE (ing_amox:ActiveIngredient {ing_id: 'ING_005', name: 'Amoxicillin Trihydrate'})
            MERGE (ing_azith:ActiveIngredient {ing_id: 'ING_006', name: 'Azithromycin'})
            MERGE (ing_metf:ActiveIngredient {ing_id: 'ING_007', name: 'Metformin Hydrochloride'})
            MERGE (ing_atorv:ActiveIngredient {ing_id: 'ING_008', name: 'Atorvastatin Calcium'})

            // 2. Diseases & Symptoms
            MERGE (dis_cad:Disease {code: 'I25.1', name: 'Coronary Artery Disease', category: 'Cardiovascular'})
            MERGE (dis_afib:Disease {code: 'I48.0', name: 'Atrial Fibrillation', category: 'Cardiovascular'})
            MERGE (dis_t2d:Disease {code: 'E11.9', name: 'Type 2 Diabetes', category: 'Endocrine'})
            MERGE (dis_pneu:Disease {code: 'J18.9', name: 'Bacterial Pneumonia', category: 'Respiratory'})
            MERGE (dis_oa:Disease {code: 'M19.9', name: 'Osteoarthritis', category: 'Musculoskeletal'})

            MERGE (sym_pain:Symptom {name: 'Chest Pain', severity: 'High'})
            MERGE (sym_fever:Symptom {name: 'High Fever', severity: 'Medium'})
            MERGE (sym_joint:Symptom {name: 'Joint Inflammation', severity: 'Medium'})
            MERGE (dis_cad)-[:PRESENTS_SYMPTOM]->(sym_pain)
            MERGE (dis_pneu)-[:PRESENTS_SYMPTOM]->(sym_fever)
            MERGE (dis_oa)-[:PRESENTS_SYMPTOM]->(sym_joint)

            // 3. Drugs & Ingredient Bindings
            MERGE (d_aspirin:Drug {drug_id: 'DRUG_ASP', name: 'Aspirin Cardio', dosage_form: 'Tablet 81mg'})
            MERGE (d_plavix:Drug {drug_id: 'DRUG_PLV', name: 'Plavix', dosage_form: 'Tablet 75mg'})
            MERGE (d_coumadin:Drug {drug_id: 'DRUG_CMD', name: 'Coumadin', dosage_form: 'Tablet 5mg'})
            MERGE (d_advil:Drug {drug_id: 'DRUG_ADV', name: 'Advil', dosage_form: 'Capsule 200mg'})
            MERGE (d_amoxil:Drug {drug_id: 'DRUG_AMX', name: 'Amoxil', dosage_form: 'Capsule 500mg'})
            MERGE (d_zithro:Drug {drug_id: 'DRUG_ZTH', name: 'Zithromax', dosage_form: 'Tablet 250mg'})
            MERGE (d_glucophage:Drug {drug_id: 'DRUG_GLC', name: 'Glucophage', dosage_form: 'Tablet 500mg'})
            MERGE (d_lipitor:Drug {drug_id: 'DRUG_LPT', name: 'Lipitor', dosage_form: 'Tablet 20mg'})

            MERGE (d_aspirin)-[:CONTAINS_INGREDIENT]->(ing_asp)
            MERGE (d_plavix)-[:CONTAINS_INGREDIENT]->(ing_clop)
            MERGE (d_coumadin)-[:CONTAINS_INGREDIENT]->(ing_warf)
            MERGE (d_advil)-[:CONTAINS_INGREDIENT]->(ing_ibu)
            MERGE (d_amoxil)-[:CONTAINS_INGREDIENT]->(ing_amox)
            MERGE (d_zithro)-[:CONTAINS_INGREDIENT]->(ing_azith)
            MERGE (d_glucophage)-[:CONTAINS_INGREDIENT]->(ing_metf)
            MERGE (d_lipitor)-[:CONTAINS_INGREDIENT]->(ing_atorv)

            // 4. Indications
            MERGE (d_aspirin)-[:TREATS]->(dis_cad)
            MERGE (d_plavix)-[:TREATS]->(dis_cad)
            MERGE (d_coumadin)-[:TREATS]->(dis_afib)
            MERGE (d_advil)-[:TREATS]->(dis_oa)
            MERGE (d_amoxil)-[:TREATS]->(dis_pneu)
            MERGE (d_zithro)-[:TREATS]->(dis_pneu)
            MERGE (d_glucophage)-[:TREATS]->(dis_t2d)

            // 5. Drug-Drug Interactions
            MERGE (d_coumadin)-[:INTERACTS_WITH {severity: 'Critical', effect: 'Severe Bleeding Risk'}]->(d_aspirin)
            MERGE (d_aspirin)-[:INTERACTS_WITH {severity: 'Critical', effect: 'Severe Bleeding Risk'}]->(d_coumadin)
            MERGE (d_coumadin)-[:INTERACTS_WITH {severity: 'Major', effect: 'Increased Hemorrhage Risk'}]->(d_advil)
            MERGE (d_advil)-[:INTERACTS_WITH {severity: 'Major', effect: 'Increased Hemorrhage Risk'}]->(d_coumadin)
            MERGE (d_aspirin)-[:INTERACTS_WITH {severity: 'Moderate', effect: 'Reduced Platelet Action'}]->(d_advil)

            // 6. Patients
            MERGE (p1:Patient {patient_id: 'PAT_101', name: 'Arthur Morgan', age: 58, gender: 'Male'})
            MERGE (p2:Patient {patient_id: 'PAT_102', name: 'Elena Fisher', age: 44, gender: 'Female'})
            MERGE (p3:Patient {patient_id: 'PAT_103', name: 'Marcus Vance', age: 67, gender: 'Male'})

            MERGE (p1)-[:DIAGNOSED_WITH]->(dis_afib)
            MERGE (p1)-[:CURRENTLY_TAKING]->(d_coumadin)
            MERGE (p1)-[:ALLERGIC_TO]->(ing_amox)

            MERGE (p2)-[:DIAGNOSED_WITH]->(dis_t2d)
            MERGE (p2)-[:CURRENTLY_TAKING]->(d_glucophage)

            MERGE (p3)-[:DIAGNOSED_WITH]->(dis_cad)
            MERGE (p3)-[:CURRENTLY_TAKING]->(d_plavix)
            MERGE (p3)-[:CURRENTLY_TAKING]->(d_lipitor)
            MERGE (p3)-[:ALLERGIC_TO]->(ing_asp)
            """
            session.run(seed_cypher)
            print("-> Graph data successfully seeded into CognoDB!")
    finally:
        db_manager.close()

if __name__ == "__main__":
    seed_medical_graph()