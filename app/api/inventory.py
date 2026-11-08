
from fastapi import APIRouter, HTTPException
from app.core.database import get_connection
from app.schemas.inventory import InventoryCreate, InventoryUpdate

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


# GET: View all inventory records
@router.get("/")
def get_inventory():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        p.product_id,
                        p.name,
                        p.sku,
                        i.quantity_on_hand,
                        i.reorder_level,
                        i.safety_stock,
                        i.updated_at
                    FROM products p
                    JOIN inventory i
                    ON p.product_id = i.product_id
                    ORDER BY p.product_id;
                """)

                rows = cur.fetchall()

        return [
            {
                "product_id": row[0],
                "name": row[1],
                "sku": row[2],
                "quantity_on_hand": row[3],
                "reorder_level": row[4],
                "safety_stock": row[5],
                "updated_at": row[6]
            }
            for row in rows
        ]

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve inventory"
        )


# POST: Create inventory for a product
@router.post("/")
def create_inventory(item: InventoryCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO inventory
                    (product_id, quantity_on_hand,
                     reorder_level, safety_stock)
                    VALUES (%s, %s, %s, %s)
                    RETURNING inventory_id, product_id,
                              quantity_on_hand, reorder_level,
                              safety_stock;
                """, (
                    item.product_id,
                    item.quantity_on_hand,
                    item.reorder_level,
                    item.safety_stock
                ))

                row = cur.fetchone()

        return {
            "inventory_id": row[0],
            "product_id": row[1],
            "quantity_on_hand": row[2],
            "reorder_level": row[3],
            "safety_stock": row[4]
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not create inventory: {str(e)}"
        )


# PUT: Update existing stock quantity
@router.put("/{product_id}")
def update_inventory(product_id: int, item: InventoryUpdate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE inventory
                    SET quantity_on_hand = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = %s
                    RETURNING product_id, quantity_on_hand,
                              reorder_level, safety_stock;
                """, (
                    item.quantity_on_hand,
                    product_id
                ))

                row = cur.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Inventory record not found"
                    )

        return {
            "product_id": row[0],
            "quantity_on_hand": row[1],
            "reorder_level": row[2],
            "safety_stock": row[3],
            "message": "Inventory updated successfully"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not update inventory"
        )
