import configparser
import pandas as pd
import DatasetAPI.Accounts as Accounts
import DatasetAPI.Transactions as Transactions
import time


class DB(object):
    def __init__(self):
        self.path = ""
        self.id = ""
        self.transaction_db = Transactions.TransactionDB("", "", "", "")
        self.pd = pd.DataFrame()
        self.accounts = []
        self.accounts_addresses = []
        self.frauds_num = 0

    def init(self):
        config = configparser.ConfigParser()
        config.read("common_cfg.ini")

        self.path = config["DB_Base"]["path"]
        self.id = config["DB_Base"]["id"]
        self.pd = pd.read_csv(self.path, delimiter=",")

        self.transaction_db = Transactions.TransactionDB(
            config["Transaction_Base"]["amount"],
            config["Transaction_Base"]["time"],
            config["Transaction_Base"]["trans_from"],
            config["Transaction_Base"]["trans_to"]
        )

        for property_trans_name in config.options("Transaction"):
            property_trans_value = config["Transaction"][property_trans_name]
            setattr(Transactions.TransactionDB, property_trans_name + "_name", property_trans_value)
            # setattr(Accounts.Account, property_trans_name, "0")
            self.transaction_db.options.append(property_trans_name)

        for index, row in self.pd.iterrows():
            amount = row[self.transaction_db.amount_name]
            timestamp = time.strptime(row[self.transaction_db.timestamp_name],
                                      config["Transaction_Base"]["time_format"])

            source = row[self.transaction_db.source_name]
            target = row[self.transaction_db.target_name]
            transaction_source = Transactions.Transaction(amount, timestamp, source, target, False)
            transaction_target = Transactions.Transaction(amount, timestamp, source, target, True)

            for option in self.transaction_db.options:
                attribute_value = getattr(self.transaction_db, option + "_name")
                setattr(transaction_source, option, row[attribute_value])
                setattr(transaction_target, option, row[attribute_value])

            source_account_flag = False
            target_account_flag = False

            if source not in self.accounts_addresses:
                source_account = Accounts.Account(source)
                source_account_flag = True
            else:
                index = self.accounts_addresses.index(source)
                source_account = self.accounts[index]

            if target not in self.accounts_addresses:
                target_account = Accounts.Account(target)
                target_account_flag = True
            else:
                index = self.accounts_addresses.index(target)
                target_account = self.accounts[index]

            target_account.add_neighbor(source_account)
            source_account.add_neighbor(target_account)

            source_account.add_transaction(transaction_source)
            target_account.add_transaction(transaction_target)

            if source_account_flag:
                self.accounts.append(source_account)
                self.accounts_addresses.append(source)

            if target_account_flag:
                self.accounts.append(target_account)
                self.accounts_addresses.append(target)

        j = 0
        for i in range(0, len(self.accounts)):
            if self.accounts[i].is_fraud:
                account_temp = self.accounts[j]
                account_addr_temp = self.accounts_addresses[j]

                self.accounts[j] = self.accounts[i]
                self.accounts_addresses[j] = self.accounts_addresses[i]

                self.accounts[i] = account_temp
                self.accounts_addresses[i] = account_addr_temp

                j += 1
        self.frauds_num = j


def get(input_param):
    return input_param


class CMethod(object):
    def __init__(self, method, params):
        self.method = method
        self.params = params
        self.method_name = method.__name__

    def __call__(self, prev_params):
        if self.params != 0:
            if prev_params != "-":
                params = [prev_params]
                for param in self.params:
                    params.append(param)
                return self.method(params)
            else:
                return self.method(self.params)
        else:
            if prev_params != "-":
                return self.method(prev_params)
            else:
                return self.method()

    @staticmethod
    def init_empty_method():
        method = CMethod(get, 0)
        return method


class CMethodsTable(object):
    def __init__(self):
        self.methods_layers = []
        self.methods_buffer = []

    def __call__(self, account, rule_id):
        prev_method_return = self.methods_layers[0][rule_id](account)
        for i in range(1, len(self.methods_layers)):
            if len(self.methods_layers[i]) >= rule_id - 1:
                method = self.methods_layers[i][rule_id]
                prev_method_return = method(prev_method_return)

        return prev_method_return

    def add_method(self, method, params_list, layer_id):
        if params_list != 0:
            for params in params_list:
                p_method = CMethod(method, params)
                if len(self.methods_buffer) <= layer_id:
                    for i in range(len(self.methods_buffer), layer_id + 1):
                        self.methods_buffer.append([])
                self.methods_buffer[layer_id].append(p_method)
        else:
            p_method = CMethod(method, params_list)
            if len(self.methods_buffer) <= layer_id:
                for i in range(len(self.methods_buffer), layer_id + 1):
                    self.methods_buffer.append([])
            self.methods_buffer[layer_id].append(p_method)

    def construct_table(self):
        self._construct_table(0)
        self.methods_buffer = []
        self.adjust_table()

    def _construct_table(self, layer_id):
        counter = 0
        if len(self.methods_buffer[layer_id]) == 0:
            return self._construct_table(layer_id + 1)
        for method in self.methods_buffer[layer_id]:
            if len(self.methods_layers) <= layer_id:
                for i in range(len(self.methods_layers), layer_id + 1):
                    self.methods_layers.append([])

            self.methods_layers[layer_id].append(method)
            counter += 1

            if len(self.methods_buffer) > layer_id + 1:
                counter_next_layers = self._construct_table(layer_id + 1)
                for i in range(1, counter_next_layers):
                    self.methods_layers[layer_id].append(method)
                    counter += 1

        return counter

    def adjust_table(self):
        max_len = 0

        for layer in self.methods_layers:
            if len(layer) > max_len:
                max_len = len(layer)

        for layer in self.methods_layers:
            layer_len = len(layer)
            for i in range(layer_len, max_len):
                layer.append(CMethod.init_empty_method())

    def get_len(self):
        return len(self.methods_layers[0])








