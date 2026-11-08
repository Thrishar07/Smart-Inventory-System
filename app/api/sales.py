from fastapi import APIRouter, HTTPException
from app.core.database import get_connection
from app.schemas.sales import SaleCreate

router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)


# GET: Retrieve all sales
@router.get("/")
def get_sales():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        sale_id,
                        product_id,
                        quantity,
                        unit_price_at_sale,
                        sold_at
                    FROM sales
                    ORDER BY sold_at DESC;
                """)

                rows = cur.fetchall()

        return [
            {
                "sale_id": row[0],
                "product_id": row[1],
                "quantity": row[2],
                "unit_price_at_sale": row[3],
                "sold_at": row[4]
            }
            for row in rows
        ]

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve sales"
        )


# GET: Retrieve sales for a specific product
@router.get("/{product_id}")
def get_product_sales(product_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        sale_id,
                        product_id,
                        quantity,
                        unit_price_at_sale,
                        sold_at
                    FROM sales
                    WHERE product_id = %s
                    ORDER BY sold_at DESC;
                """, (product_id,))

                rows = cur.fetchall()

        return [
            {
                "sale_id": row[0],
                "product_id": row[1],
                "quantity": row[2],
                "unit_price_at_sale": row[3],
                "sold_at": row[4]
            }
            for row in rows
        ]

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve product sales"
        )


# POST: Record a sale and reduce inventory
@router.post("/")
def create_sale(sale: SaleCreate):

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                # Lock and retrieve the product price
                cur.execute("""
                    SELECT unit_price
                    FROM products
                    WHERE product_id = %s;
                """, (sale.product_id,))

                product = cur.fetchone()

                if product is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Product not found"
                    )

                unit_price = product[0]

                # Reduce stock only if sufficient inventory exists
                cur.execute("""
                    UPDATE inventory
                    SET quantity_on_hand = quantity_on_hand - %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = %s
                    AND quantity_on_hand >= %s
                    RETURNING quantity_on_hand;
                """, (
                    sale.quantity,
                    sale.product_id,
                    sale.quantity
                ))

                inventory = cur.fetchone()

                if inventory is None:
                    raise HTTPException(
                        status_code=409,
                        detail="Insufficient stock or inventory record missing"
                    )

                # Insert the sale record
                cur.execute("""
                    INSERT INTO sales
                    (product_id, quantity, unit_price_at_sale)
                    VALUES (%s, %s, %s)
                    RETURNING sale_id, product_id,
                              quantity, unit_price_at_sale;
                """, (
                    sale.product_id,
                    sale.quantity,
                    unit_price
                ))

                row = cur.fetchone()

        return {
            "sale_id": row[0],
            "product_id": row[1],
            "quantity": row[2],
            "unit_price_at_sale": row[3],
            "remaining_stock": inventory[0],
            "message": "Sale recorded successfully"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not record sale"
        )