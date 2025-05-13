from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
import pandas as pd

from app.database import SessionLocal, init_db
from app.models import Department, Job, HiredEmployee

app = FastAPI()
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}

@app.post("/upload_csv/{table_name}")
async def upload_csv(table_name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if table_name == "departments":
        df = pd.read_csv(file.file, header=None, names=["id", "department"])
        for _, row in df.iterrows():
            db.add(Department(id=row["id"], department=row["department"]))

    elif table_name == "jobs":
        df = pd.read_csv(file.file, header=None, names=["id", "job"])
        for _, row in df.iterrows():
            db.add(Job(id=row["id"], job=row["job"]))

    elif table_name == "hired_employees":
        df = pd.read_csv(
        file.file,
        header=None,
        names=["id", "name", "datetime", "department_id", "job_id"])

        # Asegurar que datetime esté en el formato correcto
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

        # Filtrar filas inválidas
        df = df[df["job_id"].notna()]
        df = df[df["department_id"].notna()]
        df = df[df["name"].notna()]

        # Convertir las columnas id, department_id y job_id a numérico,
        # forzando errores a NA, y luego al tipo nullable Int64
        for col in ["id", "department_id", "job_id"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        # Ahora ya puedes iterar y agregar al ORM,
        # usando None donde haya pd.NA
        for _, row in df.iterrows():
            db.add(HiredEmployee(
                id=int(row["id"]) if pd.notna(row["id"]) else None,
                name=row["name"],
                datetime=row["datetime"].to_pydatetime() if pd.notna(row["datetime"]) else None,
                department_id=int(row["department_id"]) if pd.notna(row["department_id"]) else None,
                job_id=int(row["job_id"]) if pd.notna(row["job_id"]) else None,
            ))
    else:
        return {"error": "Invalid table name"}
    
    try:
        # tu lógica de inserción
        db.commit()
        return {"message": f"{len(df)} rows inserted into {table_name}"}    
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500
    finally:
        db.close()



# ——— Sección 2: Métricas ———
from sqlalchemy import Integer


@app.get("/metrics/hired-by-quarter")
def hired_by_quarter(year: int = 2021, db: Session = Depends(get_db)):
    # en SQLite no existe EXTRACT(QUARTER), así que extraemos mes y lo convertimos a INT
    month = func.cast(func.strftime("%m", HiredEmployee.datetime), Integer)

    q1 = func.sum(case((month.between(1, 3), 1), else_=0)).label("Q1")
    q2 = func.sum(case((month.between(4, 6), 1), else_=0)).label("Q2")
    q3 = func.sum(case((month.between(7, 9), 1), else_=0)).label("Q3")
    q4 = func.sum(case((month.between(10, 12), 1), else_=0)).label("Q4")

    results = (
        db
        .query(
            Department.department.label("department"),
            Job.job           .label("job"),
            q1, q2, q3, q4
        )
        .join(HiredEmployee, HiredEmployee.department_id == Department.id)
        .join(Job,           HiredEmployee.job_id        == Job.id)
        .filter(func.strftime("%Y", HiredEmployee.datetime) == str(year))
        .group_by(Department.department, Job.job)
        .order_by(Department.department, Job.job)
        .all()
    )
    return [r._mapping for r in results]


@app.get("/metrics/departments-above-mean")
def departments_above_mean(year: int = 2021, db: Session = Depends(get_db)):
    """
    Devuelve departamentos cuyo número de hires en el año indicado
    supere la media de hires de todos los departamentos.
    """
    # 1) Subquery: hires por departamento
    hires_subq = (
        db
        .query(
            Department.id   .label("id"),
            Department.department.label("department"),
            func.count(HiredEmployee.id).label("hired")
        )
        .join(HiredEmployee, HiredEmployee.department_id == Department.id)
        .filter(extract("year", HiredEmployee.datetime) == year)
        .group_by(Department.id, Department.department)
    ).subquery()

    # 2) Calcular media
    mean_hires = db.query(func.avg(hires_subq.c.hired)).scalar() or 0

    # 3) Filtrar > media y ordenar
    results = (
        db
        .query(
            hires_subq.c.id,
            hires_subq.c.department,
            hires_subq.c.hired
        )
        .filter(hires_subq.c.hired > mean_hires)
        .order_by(hires_subq.c.hired.desc())
        .all()
    )
    return [ { **r._mapping } for r in results ]