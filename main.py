import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DATABRICKS_URL = os.getenv('DATABRICKS_URL')
DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')

app = FastAPI(title='API DevSkills - Predictive Analytics')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

class DeveloperProfile(BaseModel):
    horas_estudio: float = Field(..., ge=0, le=24)
    horas_sueno: float = Field(..., ge=0, le=24)
    asistencia: float = Field(..., ge=0, le=100)
    promedio_previo: float = Field(..., ge=0, le=5)
    indice_dedicacion: float = Field(..., ge=0)
    en_riesgo: int = Field(..., ge=0, le=1)
    destacado: int = Field(..., ge=0, le=1)

@app.get('/health')
def health():
    return {'status': 'ok', 'databricks_configurado': bool(DATABRICKS_URL and DATABRICKS_TOKEN)}

@app.post('/predecir')
def predecir(dev: DeveloperProfile):
    if not (DATABRICKS_URL and DATABRICKS_TOKEN):
        raise HTTPException(status_code=500, detail='Faltan credenciales')
    payload = {'dataframe_records': [dev.model_dump()]}
    try:
        r = requests.post(DATABRICKS_URL, headers={'Authorization': f'Bearer {DATABRICKS_TOKEN}'}, json=payload, timeout=120)
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail='Timeout')
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f'Error: {r.text}')
    pred = int(r.json()['predictions'][0])
    return {
        'prediccion': pred,
        'evaluacion': 'Dominio Exitoso del Lenguaje' if pred == 1 else 'Requiere Refuerzo Academico',
        'perfil_desarrollador': dev.model_dump()
    }
