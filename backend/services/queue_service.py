"""
PGMQ Queue Service for ValtricAI
Handles async job processing using Supabase's built-in Postgres Message Queue
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from rag_system.supabase_client import supabase_manager

logger = logging.getLogger(__name__)


class QueueName(str, Enum):
    """Available queues in PGMQ"""
    EXPORT = "export_queue"
    RATE_LIMIT = "rate_limit_queue"
    AI_RESPONSE = "ai_response_queue"


class ExportJobStatus(str, Enum):
    """Export job statuses"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PGMQueueService:
    """Service for interacting with PGMQ queues in Supabase"""
    
    def __init__(self):
        self.client = supabase_manager.tenant_admin_client  # Use admin for queue operations
        self.export_status = {}  # In-memory status tracking (use Redis in production)
    
    async def send_to_queue(self, queue_name: QueueName, message: Dict[str, Any]) -> Optional[int]:
        """Send a message to a PGMQ queue"""
        try:
            # Add timestamp to message
            message["enqueued_at"] = datetime.utcnow().isoformat()
            
            # Use the helper function we created in SQL
            if queue_name == QueueName.EXPORT:
                result = self.client.rpc(
                    'send_to_export_queue',
                    {'message': message}
                ).execute()
            else:
                # Direct PGMQ call for other queues
                result = self.client.rpc(
                    'pgmq_send',
                    {
                        'queue_name': queue_name.value,
                        'message': message
                    }
                ).execute()
            
            msg_id = result.data
            logger.info(f"Queued message {msg_id} to {queue_name.value}")
            return msg_id
            
        except Exception as e:
            logger.error(f"Failed to queue message: {e}")
            return None
    
    async def read_from_queue(
        self, 
        queue_name: QueueName, 
        qty: int = 1, 
        visibility_timeout: int = 30
    ) -> List[Dict[str, Any]]:
        """Read messages from a PGMQ queue"""
        try:
            if queue_name == QueueName.EXPORT:
                result = self.client.rpc(
                    'read_export_queue',
                    {'qty': qty}
                ).execute()
            else:
                result = self.client.rpc(
                    'pgmq_read',
                    {
                        'queue_name': queue_name.value,
                        'vt': visibility_timeout,
                        'qty': qty
                    }
                ).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Failed to read from queue: {e}")
            return []
    
    async def delete_from_queue(self, queue_name: QueueName, msg_id: int) -> bool:
        """Delete a message from queue after successful processing"""
        try:
            result = self.client.rpc(
                'pgmq_delete',
                {
                    'queue_name': queue_name.value,
                    'msg_id': msg_id
                }
            ).execute()
            
            logger.info(f"Deleted message {msg_id} from {queue_name.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False
    
    async def enqueue_export_job(
        self, 
        session_id: str, 
        structured_data: Dict[str, Any],
        export_types: List[str] = ['excel', 'pdf', 'powerpoint']
    ) -> Dict[str, Any]:
        """Queue an export generation job"""
        
        job_id = f"{session_id}_{datetime.utcnow().timestamp()}"
        
        # Create job payload
        job = {
            "job_id": job_id,
            "session_id": session_id,
            "export_types": export_types,
            "structured_data": structured_data,
            "status": ExportJobStatus.QUEUED.value
        }
        
        # Send to queue
        msg_id = await self.send_to_queue(QueueName.EXPORT, job)
        
        if msg_id:
            # Track status (in production, use Redis or database)
            self.export_status[job_id] = {
                "status": ExportJobStatus.QUEUED.value,
                "msg_id": msg_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "job_id": job_id,
                "status": ExportJobStatus.QUEUED.value,
                "status_url": f"/api/v1/export/status/{job_id}",
                "message": "Export generation queued"
            }
        else:
            return {
                "job_id": None,
                "status": ExportJobStatus.FAILED.value,
                "message": "Failed to queue export"
            }
    
    async def get_export_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of an export job"""
        
        # In production, check Redis or database
        status = self.export_status.get(job_id)
        
        if not status:
            return {
                "job_id": job_id,
                "status": "not_found",
                "message": "Job not found"
            }
        
        return status
    
    async def update_export_status(
        self, 
        job_id: str, 
        status: ExportJobStatus,
        export_urls: Optional[Dict[str, str]] = None,
        error: Optional[str] = None
    ):
        """Update the status of an export job"""
        
        if job_id in self.export_status:
            self.export_status[job_id]["status"] = status.value
            self.export_status[job_id]["updated_at"] = datetime.utcnow().isoformat()
            
            if export_urls:
                self.export_status[job_id]["export_urls"] = export_urls
            
            if error:
                self.export_status[job_id]["error"] = error
    
    async def process_export_queue(self):
        """Background worker to process export jobs"""
        
        from services.export_service import export_service
        
        logger.info("Starting export queue processor...")
        
        while True:
            try:
                # Read jobs from queue
                messages = await self.read_from_queue(QueueName.EXPORT, qty=5)
                
                for msg in messages:
                    msg_id = msg.get('msg_id')
                    job_data = msg.get('message', {})
                    job_id = job_data.get('job_id')
                    
                    logger.info(f"Processing export job {job_id}")
                    
                    # Update status to processing
                    await self.update_export_status(
                        job_id, 
                        ExportJobStatus.PROCESSING
                    )
                    
                    try:
                        # Generate exports
                        export_urls = {}
                        structured_data = job_data.get('structured_data')
                        session_id = job_data.get('session_id')
                        
                        for export_type in job_data.get('export_types', []):
                            if export_type == 'excel':
                                file_id = export_service.create_excel_file(
                                    structured_data, session_id
                                )
                                export_urls['excel'] = f"/api/v1/export/excel/{file_id}"
                            
                            elif export_type == 'pdf':
                                file_id = export_service.create_pdf_report(
                                    structured_data, session_id
                                )
                                export_urls['pdf'] = f"/api/v1/export/pdf/{file_id}"
                            
                            elif export_type == 'powerpoint':
                                file_id = export_service.create_powerpoint(
                                    structured_data, session_id
                                )
                                export_urls['powerpoint'] = f"/api/v1/export/ppt/{file_id}"
                        
                        # Update status to completed
                        await self.update_export_status(
                            job_id,
                            ExportJobStatus.COMPLETED,
                            export_urls=export_urls
                        )
                        
                        # Delete message from queue
                        await self.delete_from_queue(QueueName.EXPORT, msg_id)
                        
                        logger.info(f"Completed export job {job_id}")
                        
                    except Exception as e:
                        logger.error(f"Export job {job_id} failed: {e}")
                        
                        # Update status to failed
                        await self.update_export_status(
                            job_id,
                            ExportJobStatus.FAILED,
                            error=str(e)
                        )
                        
                        # Message will reappear after visibility timeout for retry
                
                # Sleep briefly between polls
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                await asyncio.sleep(5)  # Back off on error


# Global queue service instance
queue_service = PGMQueueService()


# Background worker startup
async def start_queue_workers():
    """Start background queue workers"""
    
    # Start export queue processor
    asyncio.create_task(queue_service.process_export_queue())
    
    logger.info("Queue workers started")