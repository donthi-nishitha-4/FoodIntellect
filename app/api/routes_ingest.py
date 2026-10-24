from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"]
)


UPLOAD_FOLDER = Path("uploads")

UPLOAD_FOLDER.mkdir(
    exist_ok=True
)


@router.post("/barcode")
def barcode_lookup(barcode: str = Form(...)):

    # Mock ProductData
    # Later this will call Member 1's Open Food Facts code.

    product = {
        "product_name": "Sample Chocolate Biscuit",
        "barcode": barcode,

        "ingredients": [
            "Wheat Flour",
            "Sugar",
            "Palm Oil",
            "Cocoa Powder",
            "Soy Lecithin"
        ],

        "allergens": [
            "Gluten",
            "Soy"
        ],

        "nutrition": {
            "energy_kcal": 450,
            "sugars": 22,
            "fat": 20,
            "protein": 6
        }
    }

    return {
        "success": True,
        "product": product
    }


@router.post("/image")
async def upload_image(
    image: UploadFile = File(...)
):

    file_path = UPLOAD_FOLDER / image.filename

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            image.file,
            buffer
        )

    # Mock OCR result
    # Later Member 1 will provide real OCR output.

    product = {
        "product_name": "Scanned Food Product",

        "ingredients": [
            "Wheat Flour",
            "Sugar",
            "Palm Oil",
            "Soy Lecithin"
        ],

        "allergens": [
            "Gluten",
            "Soy"
        ],

        "nutrition": {
            "energy_kcal": 450,
            "sugars": 22
        }
    }

    return {
        "success": True,

        "filename": image.filename,

        "product": product
    }