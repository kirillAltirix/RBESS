import configparser
import pandas as pd
import DatasetAPI.Accounts as Accounts
import DatasetAPI.Transactions as Transactions


class DB(object):
    def __init__(self):
        self.path = ""
        self.id = ""
        self.transaction_db = Transactions.TransactionDB("", "", "", "")
        self.pd = pd.DataFrame()
        self.accounts = []
        self.accounts_addresses = []

    def init(self):
        config = configparser.ConfigParser()
        config.read("common_cfg.ini")

        self.path = config["DB_Base"]["path"]
        self.id = config["DB_Base"]["id"]
        self.pd = pd.read_csv(self.path, delimiter=";")

        self.transaction_db = Transactions.TransactionDB(
            config["Transaction_Base"]["amount"],
            config["Transaction_Base"]["time"],
            config["Transaction_Base"]["trans_from"],
            config["Transaction_Base"]["trans_to"]
        )

        for property_trans_name in config.options("Transaction"):
            property_trans_value = config["Transaction"][property_trans_name]
            setattr(Transactions.TransactionDB, property_trans_name + "_name", property_trans_value)
            setattr(Accounts.Account, property_trans_name, "0")
            self.transaction_db.options.append(property_trans_name)

        for index, row in self.pd.iterrows():
            amount = row[self.transaction_db.amount_name]
            timestamp = row[self.transaction_db.timestamp_name]
            source = row[self.transaction_db.source_name]
            target = row[self.transaction_db.target_name]
            transaction = Transactions.Transaction(amount, timestamp, source, target)

            for option in self.transaction_db.options:
                attribute_value = getattr(self.transaction_db, option + "_name")
                setattr(transaction, option, row[attribute_value])

            for account_address in [source, target]:
                if account_address not in self.accounts_addresses:
                    account = Accounts.Account(account_address)
                    account.add_transaction(transaction)
                    self.accounts.append(account)
                    self.accounts_addresses.append(account_address)
                else:
                    index = self.accounts_addresses.index(account_address)
                    account = self.accounts[index]
                    account.add_transaction(transaction)







