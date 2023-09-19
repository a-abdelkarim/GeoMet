from qgis.core import QgsTask, QgsMessageLog, QgsApplication
from qgis.PyQt.QtCore import Qt, QObject, QTimer
from concurrent.futures import ThreadPoolExecutor

class UpdateWeatherJob(QgsTask):
    def __init__(self, description):
        super().__init__(description, QgsTask.CanCancel)
    
    def run(self):
        try:
            # Your background task code goes here
            QgsMessageLog.logMessage("Background task is running.", "MyPlugin")

            # Simulate a long-running task
            import time
            time.sleep(5)

            return True
        except Exception as e:
            QgsMessageLog.logMessage(f"Background task failed: {str(e)}", "MyPlugin", level=QgsMessageLog.CRITICAL)
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
            QgsApplication.taskManager().addTask(self.background_task)
            # Ensure that the background task instance is kept alive until it completes
            self.background_task.taskCompleted.connect(self.on_task_completed)
            
    def start_continuous_task(self, interval_seconds=5):
        # Set the timer interval in milliseconds (5 seconds in this case)
        self.timer.start(interval_seconds * 1000)

    def stop_continuous_task(self):
        self.timer.stop()

    def on_task_completed(self, task):
        if task.wasSuccessful():
            QgsMessageLog.logMessage("Background task completed successfully.", "MyPlugin")
        else:
            QgsMessageLog.logMessage("Background task failed.", "MyPlugin")

        # Clean up the task and set the completed flag
        self.background_task_completed = True

    def cancel_background_task(self):
        if self.background_task and self.background_task.isRunning() and not self.background_task_completed:
            self.background_task.cancel()
