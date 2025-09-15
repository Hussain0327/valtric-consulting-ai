"""
Export Routes for ValtricAI
Handles file exports (Excel, PDF, PowerPoint) from structured data
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
import os
from typing import Optional

from services.export_service import export_service

router = APIRouter()

@router.get("/excel/{file_id}")
async def download_excel(file_id: str):
    """Download Excel file by file ID"""
    file_path = export_service.get_file_path(file_id)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    filename = f"valtric_export_{file_id}.xlsx"
    
    return FileResponse(
        path=file_path,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/pdf/{file_id}")
async def download_pdf(file_id: str):
    """Download PDF file by file ID"""
    file_path = export_service.get_file_path(file_id)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    filename = f"valtric_report_{file_id}.pdf"
    
    return FileResponse(
        path=file_path,
        media_type='application/pdf',
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/ppt/{file_id}")
async def download_powerpoint(file_id: str):
    """Download PowerPoint file by file ID"""
    file_path = export_service.get_file_path(file_id)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    filename = f"valtric_presentation_{file_id}.pptx"
    
    return FileResponse(
        path=file_path,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/cleanup")
async def cleanup_old_files():
    """Clean up old export files (admin endpoint)"""
    try:
        export_service.cleanup_old_files(max_age_hours=24)
        return {"status": "success", "message": "Old files cleaned up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")