import tkinter as tk
from nlp.task_parser import parse_task
from allocator.auction_allocator import AuctionAllocator

class Dashboard:

    def __init__(self, robots):

        self.robots = robots
        self.allocator = AuctionAllocator()

        self.root = tk.Tk()
        self.root.title("Hospital Robot Fleet Manager")

        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack()

        self.button = tk.Button(self.root, text="Assign Task", command=self.assign)
        self.button.pack()

        self.output = tk.Label(self.root, text="")
        self.output.pack()

        self.root.mainloop()

    def assign(self):

        text = self.entry.get()

        task, location = parse_task(text)

        winner = self.allocator.allocate(self.robots, location)

        winner.assign_task(task)

        self.output.config(
            text=f"{winner.robot_id} assigned to {task}"
        )
