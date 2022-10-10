import smartpy as sp

# Used for testing tez transfers
class Dummy(sp.Contract):
    def __init__(self):
        self.init()

    @sp.entry_point
    def default(self):
        pass
