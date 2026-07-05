import asyncio
import logging
from src.core.celery import celery_app
from src.modules.reports.service import ReportService
import os
import uuid

logger = logging.getLogger(__name__)

@celery_app.task(name="reports.generate_daily_report")
def generate_daily_report_task(user_id: str) -> dict:
    """
    Celery task to generate a daily trading report.
    This runs asynchronously and can be scheduled.
    """
    logger.info(f"Starting report generation for user: {user_id}")
    
    # In a real scenario, we would query the database here using a synchronous session
    # or wrap async database calls. For this milestone, we use mocked data representing
    # what would be fetched.
    
    market_data = {
        "EUR/USD": {"bid": 1.0950, "ask": 1.0952},
        "GBP/USD": {"bid": 1.2500, "ask": 1.2503}
    }
    
    journal_entries = [
        {
            "currency_pair": "EUR/USD",
            "direction": "LONG",
            "entry_price": 1.0900,
            "exit_price": 1.0950,
            "profit_loss": 50.0
        }
    ]
    
    report_content = ReportService.generate_daily_report(
        user_id=user_id,
        market_data=market_data,
        journal_entries=journal_entries
    )
    
    # Save report to a file (simulating storing it somewhere)
    report_dir = "/tmp/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_id = str(uuid.uuid4())
    report_path = os.path.join(report_dir, f"report_{report_id}.md")
    
    with open(report_path, "w") as f:
        f.write(report_content)
        
    logger.info(f"Report generated successfully at {report_path}")
    
    return {
        "status": "success",
        "report_id": report_id,
        "path": report_path
    }
