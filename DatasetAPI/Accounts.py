# Parent class for basic functionality
class _AccountBase(object):
    def __init__(self, id):
        self.id = id
        self.neighbors_ids = []
        self.transactions = []

    def add_neighbor(self, neighbor_id):
        self.neighbors_ids.append(neighbor_id)

    def get_neighbors(self):
        return self.neighbors_ids

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        if transaction.source == self.id and transaction.target not in self.neighbors_ids:
            self.add_neighbor(transaction.target)
        elif transaction.target == self.id and transaction.source not in self.neighbors_ids:
            self.add_neighbor(transaction.source)

    def get_transactions(self):
        return self.transactions


# Child class to add new options
class Account(_AccountBase):
    def __init__(self, id):
        _AccountBase.__init__(self, id)


