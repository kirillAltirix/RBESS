import warnings


# Parent class for basic functionality
class _AccountBase(object):
    def __init__(self, id):
        self.id = id
        self.neighbors_ids = []
        self.transactions = []
        self.neighbors = []
        self.is_fraud = False

    def add_neighbor(self, neighbor):
        if (neighbor.id not in self.neighbors_ids) and (neighbor.id != self.id):
            self.neighbors.append(neighbor)
            self.neighbors_ids.append(neighbor.id)

    def get_neighbors(self, level):
        return list(set(self._get_neighbors(level)))

    def _get_neighbors(self, level):
        accounts = self.neighbors.copy()

        level = level - 1
        if level > 0:
            for neighbor in self.neighbors:
                accounts += neighbor.get_neighbors(level)

        return accounts

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        try:
            trans_fraud_flag = getattr(transaction, "fraud_flag")
        except Exception:
            return
        else:
            if trans_fraud_flag:
                self.is_fraud = True

    def get_transactions(self):
        return self.transactions


# Child class to add new options
class Account(_AccountBase):
    def __init__(self, id):
        _AccountBase.__init__(self, id)
        self.features = []


class AccountsFilter(object):
    @staticmethod
    def get_neighbors(params):
        if len(params) != 2:
            warnings.warn("get_neighbors()")
            return []
        account = params[0]
        level = params[1]
        return account.get_neighbors(level)


