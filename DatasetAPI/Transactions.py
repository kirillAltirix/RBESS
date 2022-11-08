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


class TransactionsFilter(object):
    # decorator for _get_last_n_transactions() method
    @staticmethod
    def get_last_n_transactions(params_set):
        if len(params_set) != 2:
            return []
        accounts = params_set[0]
        trans_num = params_set[1]
        return TransactionsFilter._get_last_n_transactions(accounts, trans_num)

    @staticmethod
    def _get_last_n_transactions(accounts, trans_num):
        transactions = []

        for account in accounts:
            if (len(account.get_transactions()) <= trans_num):
                transactions = transactions + account.get_transactions()
            else:
                for i in range(len(account.get_transactions()) - 1, len(account.get_transactions()) - trans_num - 1, -1):
                    transactions.append(account.get_transactions()[i])

        return transactions

    # decorator for _get_transactions_by_time() method
    @staticmethod
    def get_transactions_by_time(params_set):
        if len(params_set) != 3:
            return []
        accounts = params_set[0]
        time_from = params_set[1]
        time_to = params_set[2]
        return TransactionsFilter._get_transactions_by_time(accounts, time_from, time_to)

    @staticmethod
    def _get_transactions_by_time(accounts, time_from, time_to):
        transactions = []

        for account in accounts:
            for trans in account.get_transactions():
                if time_from < trans.timestamp and trans.timestamp < time_to:
                    transactions.append(trans)

        return transactions

    @staticmethod
    def get_amounts(transactions):
        amounts = []

        for trans in transactions:
            amounts.append(trans.amount)

        return amounts

    @staticmethod
    def greater_than(params):
        value = params[0]
        comparing_value = params[1]
        if value > comparing_value:
            return True
        else:
            return False

    @staticmethod
    def smaller_than(params):
        value = params[0]
        comparing_value = params[1]
        if value < comparing_value:
            return True
        else:
            return False

    @staticmethod
    def greater_equal_than(params):
        value = params[0]
        comparing_value = params[1]
        if value >= comparing_value:
            return True
        else:
            return False

    @staticmethod
    def smaller_equal_than(params):
        value = params[0]
        comparing_value = params[1]
        if value <= comparing_value:
            return True
        else:
            return False

    @staticmethod
    def equal_to(params):
        value = params[0]
        comparing_value = params[1]
        if value == comparing_value:
            return True
        else:
            return False

    @staticmethod
    def between(params):
        value = params[0]
        left_border = params[1]
        right_border = params[2]
        if left_border <= value and value <= right_border:
            return True
        else:
            return False
