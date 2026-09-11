"""
FastAPI Ingestion Routes (Member 3 Workstream)

Endpoints for Barcode lookup and Image upload OCR processing.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from schemas.contracts import ProductData
from ingestion.openfoodfacts.client import OpenFoodFactsClient
from ingestion.pipeline import IngestionPipeline

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])

off_client = OpenFoodFactsClient()
ingest_pipeline = IngestionPipeline()


@router.get("/barcode/{barcode}", response_model=ProductData)
async def get_by_barcode(barcode: str):
    """Lookup product details by EAN/UPC barcode."""
    product = off_client.fetch_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with barcode '{barcode}' not found in Open Food Facts.")
    return product


@router.post("/ocr", response_model=ProductData)
async def process_ocr_image(file: UploadFile = File(...)):
    """Upload food package photo for OCR extraction."""
    contents = await file.read()
    try:
        product = ingest_pipeline.process_image(contents)
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process label image: {str(e)}")
