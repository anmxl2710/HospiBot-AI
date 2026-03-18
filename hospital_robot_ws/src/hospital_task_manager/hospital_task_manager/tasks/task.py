class Task:

    def __init__(self, task_type, location, priority=1):
        self.task_type = task_type
        self.location = location
        self.priority = priority

    def __str__(self):
        return f"Task(type={self.task_type}, location={self.location}, priority={self.priority})"
