class TaskQueue:

    def __init__(self):
        self.queue = []

    def add_task(self, task):
        self.queue.append(task)

    def get_next_task(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def has_tasks(self):
        return len(self.queue) > 0
