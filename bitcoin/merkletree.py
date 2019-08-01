# -*- coding: utf-8 -*-

import hashlib
import json
from collections import OrderedDict


# 1. Declare the class trees
class PMerkTree:

    # 2. Initiate the class object
    def __init__(self, listoftransaction=None):
        self.listoftransaction = listoftransaction
        self.past_transaction = OrderedDict()

    # 3. Create the Merkle Tree
    def create_tree(self):

        # 3.0 Continue on the declaration
        listoftransaction = self.listoftransaction
        past_transaction = self.past_transaction
        temp_transaction = []

        # 3.1 Loop until the list finishes
        for index in range(0, len(listoftransaction), 2):

            # 3.2 Get the most left element
            current = listoftransaction[index]

            # 3.3 If there is still index left get the right of the left most element
            if index + 1 != len(listoftransaction):
                current_right = listoftransaction[index + 1]

            # 3.4 If we reached the limit of the list then make a empty string
            else:
                current_right = ''

            # 3.5 Apply the Hash 256 function to the current values
            current_hash = hashlib.sha256(current.encode('utf-8'))

            # 3.6 If the current right hash is not a '' <- empty string
            if current_right != '':
                current_right_hash = hashlib.sha256(current_right.encode('utf-8'))

            # 3.7 Add the Transaction to the dictionary
            past_transaction[listoftransaction[index]] = current_hash.hexdigest()

            # 3.8 If the next right is not empty
            if current_right != '':
                past_transaction[listoftransaction[index + 1]] = current_right_hash.hexdigest()

            # 3.9 Create the new list of transaction
            if current_right != '':
                temp_transaction.append(current_hash.hexdigest() + current_right_hash.hexdigest())

            # 3.01 If the left most is an empty string then only add the current value
            else:
                temp_transaction.append(current_hash.hexdigest())

        # 3.02 Update the variables and rerun the function again
        if len(listoftransaction) != 1:
            self.listoftransaction = temp_transaction
            self.past_transaction = past_transaction

            # 3.03 Call the function repeatly again and again until we get the root
            self.create_tree()

    # 4. Return the past Transaction
    def Get_past_transacion(self):
        return self.past_transaction

    # 5. Get the root of the transaction
    def Get_Root_leaf(self):
        last_key = list(self.past_transaction.keys())[-1]
        return self.past_transaction[last_key]


# Declare the main part of the function to run
if __name__ == "__main__":

    # a) Create the new class of PMerkTree
    MTree = PMerkTree()

    # b) Give list of transaction
    transaction = ['a', 'b', 'c', 'd']

    # c) pass on the transaction list
    MTree.listoftransaction = transaction

    # d) Create the Merkle Tree transaction
    MTree.create_tree()

    # e) Retrieve the transaction
    past_transaction = MTree.Get_past_transacion()

    # f) Get the last transaction and print all
    print("First Example - Even number of transaction Merkel Tree")
    print('Final root of the tree : ', MTree.Get_Root_leaf())
    print(json.dumps(past_transaction, indent=4))
    print("-" * 50)

    # h) Second example
    print("Second Example - Odd number of transaction Merkel Tree")
    MTree = PMerkTree()
    transaction = ['a', 'b', 'c', 'd', 'e']
    MTree.listoftransaction = transaction
    MTree.create_tree()
    past_transaction = MTree.Get_past_transacion()
    print('Final root of the tree : ', MTree.Get_Root_leaf())
    print(json.dumps(past_transaction, indent=4))
    print("-" * 50)

    # i) Actual Use Case
    print("Final Example - Actuall use case of the Merkle Tree")

    # i-1) Declare a transaction - the ground truth
    ground_truth_Tree = PMerkTree()
    ground_truth_transaction = ['a', 'b', 'c', 'd', 'e']
    ground_truth_Tree.listoftransaction = ground_truth_transaction
    ground_truth_Tree.create_tree()
    ground_truth_past_transaction = ground_truth_Tree.Get_past_transacion()
    ground_truth_root = ground_truth_Tree.Get_Root_leaf()

    # i-2) Declare a tampered transaction
    tampered_Tree = PMerkTree()
    tampered_Tree_transaction = ['a', 'b', 'c', 'd', 'e']
    tampered_Tree.listoftransaction = tampered_Tree_transaction
    tampered_Tree.create_tree()
    tampered_Tree_past_transaction = tampered_Tree.Get_past_transacion()
    tampered_Tree_root = tampered_Tree.Get_Root_leaf()

    # i-3) The three company share all of the transaction
    print('Company A - my final transaction hash : ', ground_truth_root)
    print('Company B - my final transaction hash : ', ground_truth_root)
    print('Company C - my final transaction hash : ', tampered_Tree_root)

    # i-4) Print out all of the past transaction
    print("\n\nGround Truth past Transaction ")
    print(json.dumps(ground_truth_past_transaction, indent=4))

    print("\n\nTamper Truth past Transaction ")
    print(json.dumps(tampered_Tree_past_transaction, indent=4))
