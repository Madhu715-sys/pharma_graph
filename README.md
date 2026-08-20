# Clinical Drug-Drug Interaction, Allergy Verification, and Safe Alternative Pathfinder

## Use Case Summary
This system provides real-time verification of drug-drug interactions, patient allergy cross-checks, and safe alternative medication recommendations. By linking clinical data points into an interconnected network, it helps healthcare providers make informed prescription decisions without missing hidden contraindications.

---

## Why a Graph Database?
Traditional relational databases struggle with complex clinical data where relationships are dynamic and multi-layered. 
* **Relational Bottlenecks:** Evaluating dynamic, multi-hop drug conflicts, cross-reactivity, and active ingredient allergen paths requires numerous computationally expensive `JOIN` operations across multiple junction tables.
* **Graph Native Traversals:** Graph databases store relationships as first-class entities, allowing the system to traverse multi-hop paths (e.g., `Patient -> Allergy -> Ingredient <- Drug`) natively and efficiently with constant-time index-free adjacency.

---

## Data Model Diagram

### Node Labels
* `:Patient`
* `:Drug`
* `:Disease`
* `:ActiveIngredient`
* `:Symptom`

### Relationships
* `(:Drug)-[:TREATS]->(:Disease)`
* `(:Drug)-[:CONTAINS_INGREDIENT]->(:ActiveIngredient)`
* `(:Drug)-[:INTERACTS_WITH]->(:Drug)`
* `(:Patient)-[:ALLERGIC_TO]->(:ActiveIngredient)`

### Graph Model Representation
<img width="510" height="712" alt="Screenshot 2026-08-20 175446" src="https://github.com/user-attachments/assets/685bd9d3-896a-437d-b8a9-ae4c1ba26d1e" />
<img width="724" height="724" alt="Screenshot 2026-08-20 175423" src="https://github.com/user-attachments/assets/d8406161-81a5-4ccb-85b2-7b1c06e71e6a" />
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/05276678-e84b-4ace-bf6a-ddeef1ae5d29" />
