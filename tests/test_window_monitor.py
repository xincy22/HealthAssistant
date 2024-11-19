import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from src.window_monitor import WindowMonitor

class TestWindowMoniter:

    @pytest.fixture
    def monitor(self):
        monitor = WindowMonitor()
        yield monitor
        if monitor._running:
            monitor.stop_monitoring()

    def test_init(self, monitor):
        assert monitor.current_window is None
        assert not monitor._running
        assert monitor.start_time is None
        assert monitor.logger is not None
        assert monitor._monitor_thread is None

    @patch('win32gui.GetForegroundWindow')
    @patch('win32process.GetWindowThreadProcessId')
    @patch('win32gui.GetWindowText')
    @patch('psutil.Process')
    def test_get_active_window_info(
        self, 
        mock_process,
        mock_get_text,
        mock_get_pid,
        mock_get_hwnd,
        monitor
    ):
        mock_get_hwnd.return_value = 12345
        mock_get_pid.return_value = (0, 12345)
        mock_get_text.return_value = "Test Window"

        mock_process_instance = Mock()
        mock_process_instance.name.return_value = "test.exe"
        mock_process.return_value = mock_process_instance

        window_info = monitor.get_active_window_info()

        assert isinstance(window_info, dict)
        assert window_info['hwnd'] == 12345
        assert window_info['pid'] == 12345
        assert window_info['title'] == "Test Window"
        assert window_info['process_name'] == "test.exe"
        assert isinstance(window_info['timestamp'], datetime)

    def test_start_stop_monitoring(self, monitor):
        monitor.start_monitoring()
        
        assert monitor._running is True
        assert monitor._monitor_thread is not None
        assert monitor._monitor_thread.is_alive()

        monitor.stop_monitoring()

        assert monitor._running is False
        assert not monitor._monitor_thread.is_alive()

    @patch('time.sleep')
    def test_monitor_loop(self, mock_sleep, monitor):
        mock_window_info = {
            'hwnd': 12345,
            'pid': 12345,
            'title': 'Test Window',
            'process_name': 'test.exe',
            'timestamp': datetime.now()
        }

        with patch.object(
            monitor, 'get_active_window_info', 
            return_value = mock_window_info
        ):
            monitor.start_monitoring()
            time.sleep(0.1)
            monitor.stop_monitoring()

            assert monitor.current_window == mock_window_info

    def test_handle_window_change(self, monitor):
        initial_time = datetime.now()
        initial_window = {
            'hwnd': 12345,
            'pid': 12345,
            'title': 'Initial Window',
            'process_name': 'initial.exe',
            'timestamp': initial_time
        }

        new_window = {
            'hwnd': 67890,
            'pid': 67890,
            'title': 'New Window',
            'process_name': 'new.exe',
            'timestamp': initial_time + timedelta(seconds=5)
        }

        monitor._handle_window_change(initial_window)

        assert monitor.current_window == initial_window
        assert monitor.start_time == initial_time

        monitor._handle_window_change(new_window)
        assert monitor.current_window == new_window
        assert monitor.start_time == new_window['timestamp']
