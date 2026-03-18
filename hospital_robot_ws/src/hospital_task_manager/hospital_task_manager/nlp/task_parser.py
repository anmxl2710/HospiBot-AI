from hospital_task_manager.tasks.task import Task

def parse_task(text):

    text = text.lower()

    if "clean" in text:
        return Task("clean", (4,9))

    elif "sample" in text:
        return Task("sample", (2,3))

    elif "deliver" in text:
        return Task("deliver", (6,2))

    else:
        return Task("unknown",(0,0))
