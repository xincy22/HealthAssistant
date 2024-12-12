import time
from datetime import datetime
from threading import Thread

import psutil
import win32gui
import win32process

from .utils.logger import LoggerManager

class WindowMonitor:
    def __init__(self):
        self.current_window = None
        self._running = False
        self.start_time = None
        self._monitor_thread = None
        self.logger = LoggerManager.get_logger(__name__)
        self.logger.info("WindowMonitor initialized")

    def get_active_window_info(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            window_title = win32gui.GetWindowText(hwnd)

            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess
            ) as e:
                self.logger.warning(
                    "Failed to get process info for %s: %s",
                    window_title,
                    e
                )
                process_name = "Unknown"

            window_info = {
                'hwnd': hwnd,
                'pid': pid,
                'title': window_title,
                'process_name': process_name,
                'timestamp': datetime.now()
            }

            self.logger.debug(
                "Active window info: %s",
                window_info
            )

            return window_info
        except Exception as e:
            self.logger.error("Error getting active window info: %s", e)
            return None

    def start_monitoring(self):
        self.logger.info("Starting window monitoring")
        self._running = True
        self._monitor_thread = Thread(target=self._monitor_loop)
        self._monitor_thread.start()

    def stop_monitoring(self):
        self.logger.info("Stopping window monitoring")
        self._running = False
        if self._monitor_thread is not None:
            self._monitor_thread.join()
        self.logger.info("Window monitoring stopped")

    def _monitor_loop(self):
        self.logger.debug("Window monitor loop started")

        while self._running:
            try:
                window_info = self.get_active_window_info()
                if window_info:
                    self._handle_window_change(window_info)
                time.sleep(1)
            except Exception as e:
                self.logger.error("Error in monitor loop: %s", e)

    def _handle_window_change(self, window_info):
        if self.current_window is None:
            self.logger.info(
                "New active window: %s",
                window_info['title']
            )
            self.current_window = window_info
            self.start_time = window_info['timestamp']
            return 

        if window_info['hwnd'] != self.current_window['hwnd']:
            end_time = window_info['timestamp']
            duration = (end_time - self.start_time).total_seconds()

            self.logger.info(
                "Window changed from %s (%s) to %s (%s) after %.2f seconds", 
                self.current_window['title'],
                self.current_window['process_name'],
                window_info['title'],
                window_info['process_name'],
                duration
            )

            #TODO: Add data storage logic here

            self.current_window = window_info
            self.start_time = window_info['timestamp']