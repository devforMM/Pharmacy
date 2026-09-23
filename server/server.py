from fastapi import FastAPI
from services.Pharmacist import pharmasict_router
from services.Supplier import supplier_router
from fastapi.staticfiles import StaticFiles
app=FastAPI()
app.mount("/static",StaticFiles(directory="../styles"),"styles")
app.include_router(pharmasict_router,prefix="/pharmacist")
app.include_router(supplier_router,prefix="/supplier")

