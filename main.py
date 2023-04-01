import DatasetAPI.Core as Core
import DatasetAPI.Transactions as Ts
import DatasetAPI.Accounts as Acc
import time
import statistics
import random
import pyeasyga.pyeasyga as pyga
import pandas as pd
import json


def get_execution_time_string(total_execution_time):
    total_execution_time = round(total_execution_time)
    hours = total_execution_time // 3600
    total_execution_time %= 3600
    minutes = total_execution_time // 60
    total_execution_time %= 60
    seconds = total_execution_time
    result = ""
    if hours > 0:
        result += str(hours) + " hours "
    if minutes > 0:
        result += str(minutes) + " minutes "
    result += str(seconds) + " seconds"
    return result


def calc_f1(true_pos, false_pos, false_neg):
    precision = true_pos / (true_pos + false_pos)
    recall = true_pos / (true_pos + false_neg)
    if precision == 0 and recall == 0:
        return 0.0
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def init_db():
    print("--Process Log: start loading database")
    start_time = time.time()
    db = Core.DB()
    db.init()
    finish_time = time.time()
    print("--Process Log: finish loading database in", get_execution_time_string(finish_time - start_time))
    return db


def init_methods_table(make_prediction=True):
    norm_values = []
    for val in range(0, 100):
        list_val = [val / 100]
        norm_values.append(list_val)
    print("--Process Log: start constructing methods table")
    methods_table = Core.CMethodsTable()
    methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[1], [2]], 0)
    methods_table.add_method(Ts.TransactionsFilter.get_last_n_transactions, [[2], [3], [4]], 1)
    methods_table.add_method(Ts.TransactionsFilter.get_amounts, 0, 2)
    methods_table.add_method(statistics.stdev, 0, 3)
    if make_prediction:
        methods_table.add_method(Ts.TransactionsFilter.greater_than, norm_values, 4)
        methods_table.add_method(Ts.TransactionsFilter.smaller_than, norm_values, 4)
    methods_table.construct_table()

    methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[1], [2]], 0)
    methods_table.add_method(len, 0, 1)
    if make_prediction:
        methods_table.add_method(Ts.TransactionsFilter.greater_than, [[10], [20], [30], [40], [50], [100], [200], [500], [1000]], 2)
    methods_table.construct_table()

    methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[1], [2]], 0)
    methods_table.add_method(Ts.TransactionsFilter.get_transactions, 0, 1)
    methods_table.add_method(len, 0, 2)
    if make_prediction:
        methods_table.add_method(Ts.TransactionsFilter.greater_than, [[1000], [2000], [3000], [5000], [10000], [20000], [50000]], 3)
    methods_table.construct_table()

    methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[1], [2]], 0)
    methods_table.add_method(Ts.TransactionsFilter.get_last_n_transactions, [[2], [3]], 1)
    methods_table.add_method(Ts.TransactionsFilter.get_amounts, 0, 2)
    methods_table.add_method(statistics.mean, 0, 3)
    if make_prediction:
        methods_table.add_method(Ts.TransactionsFilter.greater_than, norm_values, 4)
        methods_table.add_method(Ts.TransactionsFilter.smaller_than, norm_values, 4)
    methods_table.construct_table()

    '''methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[1], [2], [3]], 0)
    methods_table.add_method(Ts.TransactionsFilter.get_chained_transactions, 0, 1)
    methods_table.add_method(len, 0, 2)
    if make_prediction:
        methods_table.add_method(Ts.TransactionsFilter.greater_than, [[5], [10], [15], [20], [25]], 3)
    methods_table.construct_table()'''

    '''methods_table.add_method(Acc.AccountsFilter.get_neighbors, [[1], [2]], 0)
    methods_table.add_method(Ts.TransactionsFilter.get_night_transaction, 0, 1)
    methods_table.add_method(len, 0, 2)
    if make_prediction:
        methods_table.add_method(Ts.TransactionsFilter.greater_than, [[1], [2], [3]], 3)
    methods_table.construct_table()'''

    print(f"--Process Log: features number: {methods_table.get_len()}")
    print("--Process Log: finish constructing methods table")
    return methods_table


# increase the performance of calculation randomly choosing non fraud accounts
def init_account_ids(db):
    check_coefficient = 30000
    accounts_ids = []
    for i in range(0, db.frauds_num):
        accounts_ids.append(i)
    for i in range(0, db.frauds_num * check_coefficient):
        if i >= len(db.accounts) - db.frauds_num:
            break
        accounts_ids.append(random.randint(db.frauds_num, len(db.accounts) - 1))
    return accounts_ids


def fitness(individual, data):
    true_pos = 0
    true_neg = 0
    false_pos = 0
    false_neg = 0

    for id in data[2]:
        account = data[0].accounts[id]
        true_num = 0
        false_num = 0
        rule_id = 0
        for rule_trigger in individual:
            if rule_trigger == 1:
                res = account.features[rule_id]
                # res = data[1](account, rule_id)
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

    if true_pos == 0 and false_pos == 0:
        return 0.0
    else:
        return calc_f1(true_pos, false_pos, false_neg)


def calc_confusion_matrix(individual, data) -> list:
    true_pos = 0
    true_neg = 0
    false_pos = 0
    false_neg = 0

    for id in data[2]:
        account = data[0].accounts[id]
        true_num = 0
        false_num = 0
        rule_id = 0
        for rule_trigger in individual:
            if rule_trigger == 1:
                res = account.features[rule_id]
                if res:
                    true_num += 1
                else:
                    false_num += 1
            rule_id += 1

        if true_num == 0 and false_num == 0:
            break
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

    return [true_pos, false_pos, false_neg, true_neg]


def run_ga(data):
    print("--Process Log: start genetic algorithm")
    start_time = time.time()
    population_size = 100
    generations = 5000
    ga = pyga.GeneticAlgorithm(data[1].get_len(), data, population_size, generations)
    ga.fitness_function = fitness
    ga.run(1)
    total_execution_time = time.time() - start_time
    print("--Process Log: finish genetic algorithm in", get_execution_time_string(total_execution_time))
    print("--Process Log: Time to process 1 population:", get_execution_time_string(total_execution_time / generations))
    print("--Process Log: Time to process 1 individual:",
          get_execution_time_string(total_execution_time / (generations * population_size)))
    print("--Process Log: Time to process 1 gen:",
          get_execution_time_string(total_execution_time / (generations * population_size * data[1].get_len())))
    print(ga.best_individual())


def create_features(db, methods_table):
    print("--Process Log: start creating features list")
    print("Progress bar: ", end='')
    tenth_size = len(db.accounts) // 10
    tenth_size_iterator = tenth_size
    iterator = 0
    for account in db.accounts:
        account.features = []
        if (iterator >= tenth_size_iterator):
            print("|", end='')
            tenth_size_iterator += tenth_size
        for rule_id in range(0, methods_table.get_len()):
            account.features.append(methods_table(account, rule_id))
        iterator += 1
    print("")
    print("--Process Log: stop creating features list")


def export_features(db, path, format):
    print("--Process Log: start export")
    features_list = []
    features_names = []
    prefix = "feature_"
    index_label_var = "accounts addresses"
    flag_init_header = True
    for account in db.accounts:
        if flag_init_header:
            flag_init_header = False
            for i in range(0, len(account.features)):
                features_names.append(prefix + str(i))
            features_names.append("target")
        features_list.append(account.features + [account.is_fraud])

    df = pd.DataFrame(features_list, index=db.accounts_addresses, columns=features_names)
    df.replace({False: 0, True: 1}, inplace=True)
    if format == "csv":
        df.to_csv(path + "." + format, index_label=index_label_var, float_format="%.2f")
    elif format == "xlsx":
        df.to_excel(path + "." + format, index_label=index_label_var, float_format="%.2f")
    print("--Process Log: finished export")


def process_individual() -> list:
    file = open("individual.txt")
    str_individual = file.read()
    str_individual = json.loads(str_individual)
    individual = []
    for gen in str_individual:
        individual.append(gen)
    return individual


def print_confusion():
    individual = process_individual()
    db = init_db()
    methods_table = init_methods_table()
    create_features(db, methods_table)
    accounts_ids = init_account_ids(db)
    data = [db, methods_table, accounts_ids]
    print(calc_confusion_matrix(individual, data))


def go_algo():
    db = init_db()
    methods_table = init_methods_table()
    create_features(db, methods_table)
    accounts_ids = init_account_ids(db)
    run_ga([db, methods_table, accounts_ids])


def calc_features():
    db = init_db()
    # methods_table_bool = init_methods_table()
    # create_features(db, methods_table_bool)
    # export_features(db, ".\\rbess_features_bool", "csv")
    methods_table_val = init_methods_table(False)
    create_features(db, methods_table_val)
    export_features(db, ".\\rbess_features_val", "csv")


def main():
    # go_algo()
    # calc_features()
    print_confusion()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# working with date/time
# date_from = time.strptime("01.02.2022 00:00:00", "%d.%m.%Y %H:%M:%S")
# date_to = time.strptime("02.02.2022 00:00:00", "%d.%m.%Y %H:%M:%S")
# transactions_by_date = Ts.TransactionsFilter.get_transactions_by_time([neighbors, date_from, date_to])



