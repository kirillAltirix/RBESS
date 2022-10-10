class _TransactionDBBase(object):
    def __init__(self, amount_name, timestamp_name, source_name, target_name):
        self.amount_name = amount_name
        self.timestamp_name = timestamp_name
        self.source_name = source_name
        self.target_name = target_name
        self.options = []
        self.options_ids = []


class TransactionDB(_TransactionDBBase):
    def __init__(self, amount_name, timestamp_name, source_name, target_name):
        _TransactionDBBase.__init__(self, amount_name, timestamp_name, source_name, target_name)


# Parent class for basic functionality
class _TransactionBase(object):
    def __init__(self, amount, timestamp, source, target):
        self.amount = amount
        self.timestamp = timestamp
        self.source = source
        self.target = target


# Child class to add new options
class Transaction(_TransactionBase):
    def __init__(self, amount, timestamp, source, target):
        _TransactionBase.__init__(self, amount, timestamp, source, target)
        self.options = []
