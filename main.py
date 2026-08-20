import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from database.connection import db_manager
from database.seed_data import seed_medical_graph
from queries.graph_queries import (
    get_graph_overview,
    check_patient_prescription_risk,
    find_safe_alternative_drugs,
    get_patient_profile
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    driver = db_manager.get_driver()
    if driver:
        print("[APP] CognoDB connection confirmed.")
    yield
    db_manager.close()

app = FastAPI(title="PharmGraph Engine", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/graph-data")
async def fetch_graph_data():
    records = get_graph_overview()
    nodes = {}
    edges = []

    for r in records:
        s_id = str(r["source_id"])
        t_id = str(r["target_id"])

        if s_id not in nodes:
            nodes[s_id] = {"id": s_id, "label": r["source_name"], "group": r["source_label"]}
        if t_id not in nodes:
            nodes[t_id] = {"id": t_id, "label": r["target_name"], "group": r["target_label"]}

        edge_label = r["rel_type"]
        if r["rel_detail"]:
            edge_label += f" ({r['rel_detail']})"

        edges.append({"from": s_id, "to": t_id, "label": edge_label})

    return {"nodes": list(nodes.values()), "edges": edges}

@app.get("/api/patient/{patient_id}")
async def patient_summary(patient_id: str):
    data = get_patient_profile(patient_id)
    if not data:
        return JSONResponse(status_code=404, content={"message": "Patient not found"})
    return {"patient": data[0]}

@app.get("/api/safety-check")
async def evaluate_safety(patient_id: str, drug_id: str):
    res = check_patient_prescription_risk(patient_id, drug_id)
    return {"evaluation": res[0] if res else {}}

@app.get("/api/safe-alternatives")
async def safe_alternatives(patient_id: str, disease: str):
    res = find_safe_alternative_drugs(patient_id, disease)
    return {"safe_drugs": res}

@app.post("/api/reseed")
async def reseed():
    seed_medical_graph()
    return {"message": "Knowledge graph reseeded."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)