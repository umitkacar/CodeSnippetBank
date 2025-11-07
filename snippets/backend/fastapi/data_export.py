"""Data Export"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import csv
import io
import json

app = FastAPI()

# Sample data
data = [
    {"id": 1, "name": "Item 1", "price": 10.0},
    {"id": 2, "name": "Item 2", "price": 20.0},
    {"id": 3, "name": "Item 3", "price": 30.0}
]

@app.get("/export/csv")
async def export_csv():
    """Export data as CSV"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name", "price"])
    writer.writeheader()
    writer.writerows(data)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"}
    )

@app.get("/export/json")
async def export_json():
    """Export data as JSON"""
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=export.json"}
    )

@app.get("/export/excel")
async def export_excel():
    """Export data as Excel (simplified)"""
    # In production, use openpyxl or xlsxwriter
    csv_output = io.StringIO()
    writer = csv.DictWriter(csv_output, fieldnames=["id", "name", "price"])
    writer.writeheader()
    writer.writerows(data)

    return StreamingResponse(
        iter([csv_output.getvalue()]),
        media_type="application/vnd.ms-excel",
        headers={"Content-Disposition": "attachment; filename=export.xls"}
    )
