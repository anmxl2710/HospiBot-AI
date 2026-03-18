class AuctionAllocator:

    def allocate(self, robots, task_location):

        bids = {}

        for robot in robots:
            bid = robot.bid_for_task(task_location)
            bids[robot] = bid

        winner = min(bids, key=bids.get)

        return winner
