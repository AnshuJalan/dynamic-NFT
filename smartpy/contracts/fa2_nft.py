import smartpy as sp

Addresses = sp.io.import_script_from_url("file:../common/addresses.py")
Errors = sp.io.import_script_from_url("file:../common/errors.py")  # Used for not standard errors


class Types:
    TRANSFER = sp.TList(
        sp.TRecord(
            from_=sp.TAddress,
            txs=sp.TList(
                sp.TRecord(to_=sp.TAddress, token_id=sp.TNat, amount=sp.TNat,).layout(
                    ("to_", ("token_id", "amount")),
                ),
            ),
        ).layout(("from_", "txs"))
    )

    OPERATOR_PARAMS = OPERATOR_KEY = sp.TRecord(
        owner=sp.TAddress,
        operator=sp.TAddress,
        token_id=sp.TNat,
    ).layout(("owner", ("operator", "token_id")))

    BALANCE_OF_PARAMS = sp.TRecord(
        requests=sp.TList(sp.TRecord(owner=sp.TAddress, token_id=sp.TNat).layout(("owner", "token_id"))),
        callback=sp.TContract(
            sp.TList(
                sp.TRecord(
                    request=sp.TRecord(owner=sp.TAddress, token_id=sp.TNat).layout(("owner", "token_id")),
                    balance=sp.TNat,
                ).layout(("request", "balance"))
            )
        ),
    ).layout(("requests", "callback"))


# TZIP-12 specified errors for FA2 standard
class FA2_Errors:
    FA2_TOKEN_UNDEFINED = "FA2_TOKEN_UNDEFINED"
    FA2_NOT_OPERATOR = "FA2_NOT_OPERATOR"
    FA2_INSUFFICIENT_BALANCE = "FA2_INSUFFICIENT_BALANCE"
    FA2_NOT_OWNER = "FA2_NOT_OWNER"


class FA2_NFT(sp.Contract):
    def __init__(
        self,
        admin=Addresses.ADMIN,
        ledger=sp.big_map(
            l={},
            tkey=sp.TPair(sp.TAddress, sp.TNat),
            tvalue=sp.TNat,
        ),
        # Required to prevent double minting of the same token-id
        tokens=sp.big_map(
            l={},
            tkey=sp.TNat,
            tvalue=sp.TUnit,
        ),
        operators=sp.big_map(
            l={},
            tkey=Types.OPERATOR_KEY,
            tvalue=sp.TUnit,
        ),
    ):
        self.init(
            admin=admin,
            ledger=ledger,
            tokens=tokens,
            operators=operators,
        )

    @sp.entry_point
    def mint(self, params):
        sp.set_type(params, sp.TRecord(address=sp.TAddress, token_id=sp.TNat))

        # Only admin can mint
        sp.verify(sp.sender == self.data.admin, Errors.NOT_AUTHORISED)

        # Token must not be minted already
        sp.verify(~self.data.tokens.contains(params.token_id), Errors.TOKEN_ID_ALREADY_EXISTS)

        # Mint the token at the provided address
        self.data.ledger[(params.address, params.token_id)] = sp.nat(1)

        # Record the token-id
        self.data.tokens[params.token_id] = sp.unit

    @sp.entry_point
    def balance_of(self, params):
        sp.set_type(params, Types.BALANCE_OF_PARAMS)

        # Response object
        response = sp.local("response", [])

        with sp.for_("request", params.requests) as request:
            sp.verify(self.data.tokens.contains(request.token_id), FA2_Errors.FA2_TOKEN_UNDEFINED)

            balance = self.data.ledger.get((request.owner, request.token_id), 0)
            response.value.push(sp.record(request=request, balance=sp.nat(0)))

        sp.transfer(response.value, sp.tez(0), params.callback)

    @sp.entry_point
    def transfer(self, params):
        sp.set_type(params, Types.TRANSFER)

        with sp.for_("transfer", params) as transfer:
            current_from = transfer.from_
            with sp.for_("tx", transfer.txs) as tx:

                # Verify sender
                sp.verify(
                    (sp.sender == current_from)
                    | self.data.operators.contains(
                        sp.record(owner=current_from, operator=sp.sender, token_id=tx.token_id)
                    ),
                    FA2_Errors.FA2_NOT_OPERATOR,
                )

                with sp.if_(tx.amount > 0):
                    # Make transfer
                    self.data.ledger[(current_from, tx.token_id)] = sp.as_nat(
                        self.data.ledger[(current_from, tx.token_id)] - tx.amount,
                        FA2_Errors.FA2_INSUFFICIENT_BALANCE,
                    )

                    balance = self.data.ledger.get((tx.to_, tx.token_id), 0)
                    self.data.ledger[(tx.to_, tx.token_id)] = balance + tx.amount
                with sp.else_():
                    pass

    @sp.entry_point
    def update_operators(self, params):
        sp.set_type(
            params,
            sp.TList(
                sp.TVariant(
                    add_operator=Types.OPERATOR_PARAMS,
                    remove_operator=Types.OPERATOR_PARAMS,
                )
            ),
        )

        with sp.for_("update", params) as update:
            with update.match_cases() as arg:
                with arg.match("add_operator") as upd:
                    sp.verify(
                        upd.owner == sp.sender,
                        FA2_Errors.FA2_NOT_OWNER,
                    )
                    self.data.operators[upd] = sp.unit
                with arg.match("remove_operator") as upd:
                    sp.verify(
                        upd.owner == sp.sender,
                        FA2_Errors.FA2_NOT_OWNER,
                    )
                    del self.data.operators[upd]
