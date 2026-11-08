from fastapi import APIRouter, HTTPException, status

from app.core.database import get_connection
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/", response_model=list[ProductResponse])
def get_products():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        product_id,
                        sku,
                        name,
                        category,
                        unit_price,
                        supplier_id
                    FROM products
                    ORDER BY product_id;
                """)

                rows = cur.fetchall()

        return [
            {
                "product_id": row[0],
                "sku": row[1],
                "name": row[2],
                "category": row[3],
                "unit_price": row[4],
                "supplier_id": row[5]
            }
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve products: {str(e)}"
        )


@router.post("/", response_model=ProductResponse,
             status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO products
                    (sku, name, category, unit_price, supplier_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING
                        product_id, sku, name, category,
                        unit_price, supplier_id;
                """, (
                    product.sku,
                    product.name,
                    product.category,
                    product.unit_price,
                    product.supplier_id
                ))

                row = cur.fetchone()

        return {
            "product_id": row[0],
            "sku": row[1],
            "name": row[2],
            "category": row[3],
            "unit_price": row[4],
            "supplier_id": row[5]
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not create product: {str(e)}"
        )
