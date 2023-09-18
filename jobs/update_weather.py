from qgis.core import QgsTask, QgsMessageLog, QgsApplication
from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, QTimer
from concurrent.futures import ThreadPoolExecutor

class UpdateWeatherJob(QgsTask):
    task_completed = pyqtSignal(bool)
    
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)
    
    def run(self):
        try:
            # Your background task code goes here
            QgsMessageLog.logMessage("Background task is running.", "MyPlugin")

            # Simulate a long-running task
            import time
            time.sleep(5)

            # Emit the signal to notify task completion (replace True with the actual result)
            self.task_completed.emit(True)
            return True
        except Exception as e:
            QgsMessageLog.logMessage(f"Background task failed: {str(e)}", "MyPlugin", level=QgsMessageLog.CRITICAL)
            self.task_completed.emit(False)
            return False

class UpdateWeatherJobManager(QObject):
    def __init__(self):
        super().__init__()
        self.thread_pool = ThreadPoolExecutor(max_workers=1)
        self.background_task = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_background_task)
        self.background_task_completed = False

    def start_background_task(self):
        if not self.background_task or self.background_task.isCanceled() or self.background_task_completed:
            self.background_task = UpdateWeatherJob("My Background Task")
            self.background_task.task_completed.connect(self.on_task_completed)
            QgsApplication.taskManager().addTask(self.background_task)
            self.background_task_completed = False

    def start_continuous_task(self, interval_seconds=5):
        # Set the timer interval in milliseconds (5 seconds in this case)
        self.timer.start(interval_seconds * 1000)

    def stop_continuous_task(self):
        self.timer.stop()

    def on_task_completed(self, success):
        if success:
            QgsMessageLog.logMessage("Background task completed successfully.", "MyPlugin")
        else:
            QgsMessageLog.logMessage("Background task failed.", "MyPlugin")

        # Restart the background task if it was not canceled
        if not self.background_task.isCanceled():
            self.start_background_task()

    def cancel_background_task(self):
        if self.background_task and self.background_task.isRunning() and not self.background_task_completed:
            self.background_task.cancel()
