from typing import Any
from ItemsetGenerator import ItemsetGenerator
import pandas as pd
import itertools
import time


class Apriori:
    isg = ItemsetGenerator('store_data.csv', 'transactions.html')
    rules = {}
    minSup = 0
    minConf = 0

    def __init__(self, minSup, minConf) -> None:
        self.minSup = minSup
        self.minConf = minConf
        self.isg.generateTransactionLists()

    def generateRules(self, minOrder, maxOrder, dItems):
        if minOrder == 1:  # Rules of the form : One to Rest / Rest to One
            if maxOrder == 2:
                for itemSet in dItems:
                    self.rules[itemSet[0], itemSet[1]] = self.isg.dfSupport[1][itemSet]['Support'] / \
                                                         self.isg.dfSupport[0][itemSet[0]]['Support']
                    self.rules[itemSet[1], itemSet[0]] = self.isg.dfSupport[1][itemSet]['Support'] / \
                                                         self.isg.dfSupport[0][itemSet[1]]['Support']
            else:
                for itemSet in dItems:
                    for item in itemSet:
                        li = list(itemSet)
                        li.remove(item)
                        T = tuple(li)
                        self.rules[item, T] = self.isg.dfSupport[maxOrder - 1][itemSet]['Support'] / \
                                              self.isg.dfSupport[0][item]['Support']
                        self.rules[T, item] = self.isg.dfSupport[maxOrder - 1][itemSet]['Support'] / \
                                              self.isg.dfSupport[maxOrder - 2][T]['Support']
        else:
            for itemSet in dItems:
                C = itertools.combinations(itemSet, minOrder)
                for c in C:
                    T = (i for i in itemSet if not c.__contains__(i))
                    T = tuple(T)
                    self.rules[c, T] = self.isg.dfSupport[maxOrder - 1][itemSet]['Support'] / \
                                       self.isg.dfSupport[minOrder - 1][c]['Support']

        if minOrder + 1 == maxOrder - 1 or maxOrder == 2:

            print('Rules For Order ' + str(maxOrder) + ' Have Been Generated.')
            print('Eliminating Non-Confident Rules For Order ' + str(maxOrder) + '...')
            for key in list(self.rules):
                if self.rules[key] < self.minConf:
                    self.rules.pop(key)
            print('Non-Confident Rules For Order ' + str(maxOrder) + ' Have Been Eliminated.')

            return
        else:
            return self.generateRules(minOrder + 1, maxOrder, dItems)

    def eliminateItemsets(self, k, dItems):
        print('Eliminating Infrequent ItemSets...')

        droppedCols = []
        for item in dItems:
            if dItems[item][0] < self.minSup:
                droppedCols.append(item)

        print('Infrequent ItemSets :\n', droppedCols)
        if len(dItems.columns) == 0:
            print('all ItemSets are Infrequent.')
        dItems = dItems.drop(droppedCols, axis=1)

        print(dItems)
        print('Infrequent ItemSets Eliminated Successfully.')

        if k > 1 and not dItems.empty:
            print('Generating Rules For k = ' + str(k) + '...')
            self.generateRules(1, k, dItems)

        return dItems

    def runApriori(self):
        print('Running Apriori...')
        self.recursiveApriori(1, pd.DataFrame())

    def recursiveApriori(self, k, dItems):
        dItems = self.isg.generateItemsSupport(k, dItems)
        dItems = self.eliminateItemsets(k, dItems)

        if len(dItems.columns) > 0:
            dItems = self.isg.generatePossibleItemSets(dItems, k)
            return self.recursiveApriori(k + 1, dItems)

        print('Saving Generated Rules...')
        df = pd.DataFrame(self.rules, index=['Confidence'])
        f = open('rules.html', 'w')
        f.write(df.to_html())
        print('Generated Rules Have Been Saved in a File.')


a = Apriori(10 / 7501, 0.5)
startTime = time.time()
a.runApriori()
print('Execution Time ' + str((time.time() - startTime)) + ' seconds')
