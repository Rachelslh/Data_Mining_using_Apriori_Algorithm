from typing import Any
from mlxtend.preprocessing import TransactionEncoder
from itertools import combinations

import numpy as np
import pandas as pd


class ItemsetGenerator:
    fileName = ''
    htmlFile = ''
    df = []
    dfSupport = []

    def __new__(cls, fileName, htmlFile) -> Any:
        instance = super().__new__(cls)
        instance.fileName = fileName
        instance.htmlFile = htmlFile
        return instance

    def generateTransactionLists(self):
        print('Converting DataSet to a Transaction Table...')
        te = TransactionEncoder()

        # For First Time Generation of Table.HTML
        df = pd.read_csv(self.fileName, header=None).values.tolist()
        listOfLists = [[x for x in y if x == x] for y in df]
        te_trans = te.fit(listOfLists).transform(listOfLists)
        df = pd.DataFrame(te_trans, columns=te.columns_)
        print(df.info())
        print(df.head())
        '''
        f = open('transactions.html', 'w')
        f.write(df.to_html())
        
        f = open('grocery.html', 'w')
        f.write(pd.DataFrame(te.columns_, columns=['grocery']).to_html())
        '''
        self.df = df
        print('Transaction Table Generated.')

    def generatePossibleItemSets(self, dItems, k):
        print('Generating a Set of Possible ItemSets Combinations...')

        columns = dItems.columns
        temp = list(map(list, combinations(columns, 2)))

        if k + 1 == 2:
            itemSetIndex = pd.MultiIndex.from_tuples(temp)
            dItems = pd.DataFrame(index=['Support'], columns=itemSetIndex)
        else:
            AccComb = []

            for itemSet in temp:
                getOut = False
                for i in range(0, k - 1):
                    if itemSet[0][i] != itemSet[1][i]:
                        getOut = True
                if not getOut:
                    AccComb.append(itemSet[0] + (itemSet[1][k - 1],))

            itemSetIndex = pd.MultiIndex.from_tuples(AccComb)
            dItems = pd.DataFrame(index=['Support'], columns=itemSetIndex)

        print('Possible ItemSets Combinations Generated.')
        print(dItems)

        return dItems

    def generateItemsSupport(self, k, dItems):
        print('Calculating ItemSet Support for Order = ', k, '...')
        df = self.df
        if k == 1:
            data = np.zeros((1, len(df.columns)))
            dItems = pd.DataFrame(data, index=['Support'], columns=df.columns)
            for col in df.columns:
                dItems[col] = df[col].values.sum() / len(df)

        else:
            for itemSet in dItems.columns:
                temp = np.logical_and(df[itemSet[0]], df[itemSet[1]])
                for i in range(2, k):
                    temp = np.logical_and(temp, df[itemSet[i]])
                dItems[itemSet] = sum(temp) / len(df)

        print('Support Calculated for ItemSets of Order = ', k)
        print(dItems)
        self.dfSupport.append(dItems)
        return dItems
