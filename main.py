import DatasetAPI.Core as Core
import DatasetAPI.Transactions as Ts
import DatasetAPI.Accounts as Acc
import time
import statistics

import pyeasyga.pyeasyga as pyga


def calc_f1(true_pos, false_pos, false_neg):
    precision = true_pos / (true_pos + false_pos)
    recall = true_pos / (true_pos + false_neg)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


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
    methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[2]], 0)
    methods_table.add_method(Ts.TransactionsFilter.get_last_n_transactions, [[2], [3]], 1)
    methods_table.add_method(Ts.TransactionsFilter.get_amounts, 0, 2)
    methods_table.add_method(statistics.stdev, 0, 3)
    methods_table.add_method(Ts.TransactionsFilter.greater_than, [[200]], 4)
    methods_table.construct_table()

    result = methods_table(account, 1)
    print(result)

    data = [db, methods_table]

    ga = pyga.GeneticAlgorithm(methods_table.get_len(), data, 5, 2)

    def fitness(individual, data):
        true_pos = 0
        true_neg = 0
        false_pos = 0
        false_neg = 0

        for account in data[0].accounts:
            true_num = 0
            false_num = 0
            rule_id = 0
            for rule_trigger in individual:
                if rule_trigger == 1:
                    res = data[1](account, rule_id)
                    if res:
                        true_num += 1
                    else:
                        false_num += 1
                rule_id += 1
            if true_num == 0 and false_num == 0:
                return 0.0
            local_res = False
            if true_num > false_num:
                local_res = True

            if local_res and account.is_fraud:
                true_pos += 1
            elif local_res and not account.is_fraud:
                false_pos += 1
            elif not local_res and account.is_fraud:
                false_neg += 1
            elif not local_res and not account.is_fraud:
                true_neg += 1

        return calc_f1(true_pos, false_pos, false_neg)

    ga.fitness_function = fitness
    ga.run(1)
    print(ga.best_individual())



