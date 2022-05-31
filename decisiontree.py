#/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from statistics import mean, stdev
from treelib import Tree
cat = {}

class Branch:
    def __init__(self, col_type, col_name, col_val, y, size, is_left):
        self.col_type, self.col_name, self.col_val = col_type, col_name, col_val
        self.y, self.size, self.is_left = y, size, is_left
        self.left, self.right = None, None
        if not isinstance(y, float):
            self.y = mean(y)

    def attach_children(self, left, right):
        self.left, self.right = left, right

    def predict(self, x):
        if self.left is None:
            return self.y
        val = x[self.left.col_name]
        if self.left.col_type == 'cont':
            if val < self.left.col_val:
                return self.left.predict(x)
            return self.right.predict(x)
        if val != self.left.col_val:
            return self.left.predict(x)
        return self.right.predict(x)
    
    def _getPrint(self):
        if self.is_left == True:
            if self.col_type == 'cont':
                return f"{self.col_name} < {self.col_val}: {self.y} ({self.size})"
            else:
                return f"{self.col_name} == {self.col_val}: {self.y} ({self.size})"
        elif self.is_left == False:
            if self.col_type == 'cont':
                return f"{self.col_name} >= {self.col_val}: {self.y} ({self.size})"
            else:
                return f"{self.col_name} != {self.col_val}: {self.y} ({self.size})"
        else:
            return f"{self.y} ({self.size})"
    
    def print(self, parent=None, idx=None, first=True):
        if parent is None:
            self.tree = Tree()
            self.tree.create_node(self._getPrint(), id(self))
            parent = self.tree
        if self.left is not None:
            parent.create_node(self.left._getPrint(), id(self.left), id(self))
            self.left.print(parent, id(self), False)
        if self.right is not None:
            parent.create_node(self.right._getPrint(), id(self.right), id(self))
            self.right.print(parent, id(self), False)
        if first is True:
            self.tree.show()


class MyTreeRegressor:
    def __init__(self, min_samples_leaf=8):
        self.min_samples_leaf, self.tree = min_samples_leaf, None

    def fit(self, xs, y):
        self.tree = Branch("", "", "", mean(y), len(y), None)
        self._fit_helper(xs, y, self.tree)

    def _fit_helper(self, xs, y, branch):
        cond, minLowerBatch, minUpperBatch, batchVal, minCol, batchCond = None, None, None, None, None, None
        for cName in xs:
            minUpperCol, bestVal, minLowerCol, bestCond = None, None, None, None
            if cName not in cat:
                for val in set(xs[cName]):
                    #cond = (True if v < val else False for v in xs[cName])
                    #cond = xs[cName] < val
                    lower = [v for v in xs[cName] if v < val]
                    #upper = y[~cond]
                    upper = [v for v in xs[cName] if v not in lower]
                    if len(upper) < self.min_samples_leaf or len(lower) < self.min_samples_leaf:
                        continue
                    if minLowerCol is None or\
                    stdev(lower) + stdev(upper)\
                    > stdev(minLowerCol) + stdev(minUpperCol):
                        minLowerCol, minUpperCol, bestVal, bestCondLen = lower, upper, val, (len(lower), len(upper))
                if batchVal is None or minLowerCol is None or\
                stdev(minLowerCol) + stdev(minUpperCol)\
                > stdev(minLowerBatch) + stdev(minUpperBatch):
                        minLowerBatch, minUpperBatch, batchVal, batchCondLen = minLowerCol, minUpperCol, bestVal, bestCond
                        minCol = cName
            else: continue
        left, right = None, None
        if bestVal is None:
            return
        batchCond = (minLowerBatch, minUpperBatch)
        batchCondy = ([y[i] for i in range(len(y)) if xs[minCol][i] < bestVal], [y[i] for i in range(len(y)) if xs[minCol][i] >= bestVal])
        if minCol not in cat:
            left  = Branch('cont', minCol, batchVal, batchCond[0], batchCondy[0], True)
            right = Branch('cont', minCol, batchVal, batchCond[1], batchCondy[1], False)
        else:
            left  = Branch('cat', minCol, batchVal, batchCond[0], batchCondy[0], True)
            right = Branch('cat', minCol, batchVal, batchCond[1], batchCondy[1], False)
        l = {k: tuple(v[i] for i in range(len(v)) if xs[minCol][i] < batchVal) for k,v in xs.items()} 
        r = {k: tuple(v[i] for i in range(len(v)) if xs[minCol][i] >= batchVal) for k,v in xs.items()} 
        self._fit_helper(l, batchCondy[0], left)
        self._fit_helper(r, batchCondy[1], right)
        branch.attach_children(left, right)

    def predict(self, xs):
        return [self.tree.predict(x) for x in xs]

temps = [random.random() * 3 + 20 for _ in range(100)]
xs = {'temp_before': temps[:-1]}
y = temps[1:]
t = MyTreeRegressor()
t.fit(xs, y)
t.tree.print()
#pred = [{'temp_before': temps[10]}]
#print(t.predict(pred))

