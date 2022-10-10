import smartpy as sp


class Harbinger(sp.Contract):
    def __init__(self, price=sp.nat(0)):
        self.init(price=price)

    @sp.entry_point
    def default(self):
        pass

    @sp.onchain_view()
    def getPrice(self, assetCode):
        sp.set_type(assetCode, sp.TString)

        sp.result((sp.timestamp(0), self.data.price))
