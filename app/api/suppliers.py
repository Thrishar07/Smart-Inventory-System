
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.database import get_connection

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    contact_email: str | None = None
    phone: str | None = None
    lead_time_days: int = Field(ge=0)


@router.get("/")
def get_suppliers():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT supplier_id, name, contact_email,
                       phone, lead_time_days
                FROM suppliers
                ORDER BY name;
            """)

            rows = cur.fetchall()

            return [
                {
                    "supplier_id": row[0],
                    "name": row[1],
                    "contact_email": row[2],
                    "phone": row[3],
                    "lead_time_days": row[4]
                }
                for row in rows
            ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


@router.post("/")
def create_supplier(supplier: SupplierCreate):
    if not supplier.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Supplier name cannot be empty."
        )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO suppliers (
                    name,
                    contact_email,
                    phone,
                    lead_time_days
                )
                VALUES (%s, %s, %s, %s)
                RETURNING supplier_id, name, contact_email,
                          phone, lead_time_days;
            """, (
                supplier.name.strip(),
                supplier.contact_email,
                supplier.phone,
                supplier.lead_time_days
            ))

            row = cur.fetchone()
            conn.commit()

            return {
                "supplier_id": row[0],
                "name": row[1],
                "contact_email": row[2],
                "phone": row[3],
                "lead_time_days": row[4]
            }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
