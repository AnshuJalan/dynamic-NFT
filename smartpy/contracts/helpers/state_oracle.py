import smartpy as sp

# Dummy state oracle to test out the Oracle Structure
class StateOracle(sp.Contract):
    def __init__(
        self,
        state=sp.record(
            prop_1=sp.nat(0),
            prop_2=sp.nat(0),
        ),
    ):
        self.init(state=state)

    @sp.entry_point
    def default(self):
        pass

    @sp.onchain_view()
    def get_state(self, token_id):
        sp.set_type(token_id, sp.TNat)

        sp.result(self.data.state)
