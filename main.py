import DatasetAPI.Core as Core
import DatasetAPI.Transactions as Ts
import DatasetAPI.Accounts as Acc
import time
import statistics

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    db = Core.DB()
    db.init()

    account = db.accounts[0]
    neighbors = Acc.AccountsFilter.get_neighbors([account, 2])
    transactions_n_last = Ts.TransactionsFilter.get_last_n_transactions([neighbors, 3])
    # date_from = time.strptime("01.02.2022 00:00:00", "%d.%m.%Y %H:%M:%S")
    # date_to = time.strptime("02.02.2022 00:00:00", "%d.%m.%Y %H:%M:%S")
    # transactions_by_date = Ts.TransactionsFilter.get_transactions_by_time([neighbors, date_from, date_to])
    transactions_n_last_amount = Ts.TransactionsFilter.get_amounts(transactions_n_last)
    print(statistics.stdev(transactions_n_last_amount))
    # print(statistics.mean(transactions_n_last_amount))

    methods_table = Core.CMethodsTable()
    methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[account, 2]], 0)
    methods_table.add_method(Ts.TransactionsFilter.get_last_n_transactions, [[2], [3]], 1)
    methods_table.add_method(Ts.TransactionsFilter.get_amounts, 0, 2)
    methods_table.add_method(statistics.stdev, 0, 3)
    methods_table.add_method(Ts.TransactionsFilter.greater_than, [[200]], 4)
    methods_table.construct_table()

    result = methods_table(1)
    print(result)
    # for neighbor in neighbors:
    #     print(neighbor.id)


