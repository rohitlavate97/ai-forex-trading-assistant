import os
from unittest.mock import patch, MagicMock
from src.modules.reports.tasks import generate_daily_report_task

def test_generate_daily_report_task(tmp_path):
    """
    Test the celery task that generates a daily report.
    We mock the report_dir to use a temporary directory for testing.
    """
    user_id = "test-user-123"
    
    with patch("src.modules.reports.tasks.os.makedirs") as mock_makedirs, \
         patch("src.modules.reports.tasks.open", create=True) as mock_open:
        
        # We also need to patch os.path.join to return a mock path if we want,
        # but let's just let it use the real open mocked out.
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = generate_daily_report_task(user_id)
        
        assert result["status"] == "success"
        assert "report_id" in result
        assert "path" in result
        
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_file.write.assert_called_once()
        
        # Check if write was called with the generated markdown
        written_content = mock_file.write.call_args[0][0]
        assert "Daily Trading Report" in written_content
        assert "EUR/USD" in written_content
        assert "Total Trades Today" in written_content
