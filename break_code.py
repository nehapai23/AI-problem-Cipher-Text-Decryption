#!/usr/local/bin/python3
# CSCI B551 Fall 2019
#
# Authors: nibafna-nrpai-sjejurka
#          Nikita Bafna; Neha Pai; Shivali Jejurkar
#
# based on skeleton code by D. Crandall, 11/2019
#
# ./break_code.py : attack encryption
#

import random
import math
import copy
import sys
import encode
import string
import pickle_data

'''
Function normalizes the letter distributions
'''
def normalize(d, total=1):
    charset = string.ascii_lowercase+" "
    rows = {}
    for ch in charset:
        countSum = 0
        for key, value in d.items():
            if key[0] == ch:
                countSum += value
        rows.update({ch: countSum})

    return {key: math.log(value*total/(rows[key[0]])) for key, value in d.items()}

'''
Function scales the more popular letter distributions and gives them more weightage
'''
def scale_distribution(d):
    return {key: value if value < 11000 else round(value * value/10000) for key, value in d.items()}

'''
Generates a distribution of all letters 
'''
def build_letter_transition_dist(file):
    charset = string.ascii_lowercase+" "

    dist = {}
    doc = file
    
    for a in charset:
        for b in charset:
            dist.update({(a, b): 1})

    for i in range(0, len(doc)):
        first_letter = doc[i-1] if doc[i-1].isalpha() else " "
        second_letter = doc[i] if doc[i].isalpha() else " "

        dist[(first_letter, second_letter)] += 1

    dist = scale_distribution(dist)
    return normalize(dist)

'''
Function to generate the initial replace and rearrangement table
'''
def generate_initial_tables():
    letters = list(range(ord('a'), ord('z')+1))
    random.shuffle(letters)
    replace_table = dict(zip(map(chr, range(ord('a'), ord('z')+1)), map(chr, letters)))
    rearrange_table = list(range(0, 4))
    random.shuffle(rearrange_table)
    return replace_table, rearrange_table

'''
Function takes as input the current replace table and swaps two 
transitions at random
'''
def modify_replace_table(replace_table):
    new_replace_table = copy.deepcopy(replace_table)
    first_letter = random.choice(list(new_replace_table))
    second_letter = random.choice(list(new_replace_table))
    while(first_letter == second_letter):
        second_letter = random.choice(list(new_replace_table))

    value1 = new_replace_table[first_letter]
    value2 = new_replace_table[second_letter]
    new_replace_table[first_letter] = value2
    new_replace_table[second_letter] = value1

    return new_replace_table

'''
Function takes current rearrange table and swaps two numbers at random to generate a new sequence
'''
def modify_rearrange_table(rearrange_table):
    new_rearrange_table = copy.deepcopy(rearrange_table)
    first_letter = random.choice(range(0, 4))
    second_letter = random.choice(range(0, 4))
    while(first_letter == second_letter):
        second_letter = random.choice(range(0, 4))
    temp = new_rearrange_table[first_letter]
    new_rearrange_table[first_letter] = new_rearrange_table[second_letter]
    new_rearrange_table[second_letter] = temp

    return new_rearrange_table

'''
Function computes the log likelihood of the current document string given 
the letter distribution
'''
def calculate_log_likelihood(string, letter_distribution):
    s = 0
    string = " "+string
    i = 1
    while i < len(string):
        first_letter = string[i-1]
        second_letter = string[i]
        s += letter_distribution[(first_letter, second_letter)]
        i += 1
    return (s)


'''
Function implements the metropolis hastings algorithm
'''
def break_code(string, corpus, letter_distribution):
    import time
    best_document = [float("-inf"), ""]
    ch = 0
    f = open("Outputs.txt", "w")
    for i in range(0,3):
        start_time = time.time()
        replace_table, rearrange_table = generate_initial_tables()
        max_time_limit = 190
        iteration_count = 0
        print("Starting Run ",i)
        while time.time() - start_time < max_time_limit:
            #Randomly choosing between replace table and rearrangement table
            
            if random.choice([0,1]) == 0:
                new_replace_table = modify_replace_table(replace_table)
                new_rearrange_table = copy.deepcopy(rearrange_table)
            else: 
                new_rearrange_table = modify_rearrange_table(rearrange_table)
                new_replace_table = copy.deepcopy(replace_table)
            
            #Optimization logic 2 starts: Choosing best option from 2 tables
            
#            new_replace_table1 = modify_replace_table(replace_table)
#            new_rearrange_table1 = copy.deepcopy(rearrange_table)
#            initial_doc1 = encode.encode(string, replace_table, rearrange_table)
#            probability_D1 = calculate_log_likelihood(initial_doc1, letter_distribution)
#             
#            new_rearrange_table2 = modify_rearrange_table(rearrange_table)
#            new_replace_table2 = copy.deepcopy(replace_table)
#            initial_doc2 = encode.encode(string, replace_table, rearrange_table)
#            probability_D2 = calculate_log_likelihood(initial_doc2, letter_distribution)
#            
#            if probability_D1 > probability_D2:
#                new_replace_table = copy.deepcopy(new_replace_table1)
#                new_rearrange_table = copy.deepcopy(new_rearrange_table1)
#                updated_document = initial_doc1
#                probability_D_new = probability_D1
#            else:
#                new_replace_table = copy.deepcopy(new_replace_table2)
#                new_rearrange_table = copy.deepcopy(new_rearrange_table2)
#                updated_document = initial_doc2
#                probability_D_new = probability_D2
#                
            #Optimization logic 2 ends    
        
            initial_document = encode.encode(string, replace_table, rearrange_table)
            probability_D = calculate_log_likelihood(initial_document, letter_distribution)
            updated_document = encode.encode(string, new_replace_table, new_rearrange_table)
            probability_D_new = calculate_log_likelihood(updated_document, letter_distribution)
    
    
            #Metropolis hastings condition
            if probability_D_new > probability_D or random.random() < math.exp(probability_D_new - probability_D):
                replace_table = copy.deepcopy(new_replace_table)
                rearrange_table = copy.deepcopy(new_rearrange_table)
    
            #Acceptance Criteria
            if best_document[0] < probability_D_new:
                best_document[0] = probability_D_new
                best_document[1] = updated_document
    
            iteration_count += 1
            if iteration_count % 1000 == 0:
                print(iteration_count," iterations done!")
                f.write(str(best_document[0])+": "+best_document[1]+"\n----------------------------\n")
    f.close()
    return best_document[1]

'''
Code execution starts here!
'''
if __name__ == "__main__":
    if(len(sys.argv) != 4):
        raise Exception("usage: ./break_code.py coded-file corpus output-file")
    encoded = encode.read_clean_file(sys.argv[1])
    print("Building my distribution!")
    corpus = encode.read_clean_file(sys.argv[2])
    #pickle_data.storeData(corpus,"corpusPickle")
    #corpus = pickle_data.loadData("corpusPickle")

    expected_letter_distribution = build_letter_transition_dist(corpus)
    #pickle_data.storeData(expected_letter_distribution,"letterTransitionPickle")
    #expected_letter_distribution = pickle_data.loadData("letterTransitionPickle")
    print("Wait while I try to decode!")
    decoded = break_code(encoded, corpus, expected_letter_distribution)

    with open(sys.argv[3], "w") as file:
        print(decoded, file=file)

    print("Done! Check your decrypted file.")
