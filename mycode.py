#!/usr/local/bin/python3
# CSCI B551 Fall 2019
#
# Authors: PLEASE PUT YOUR NAMES AND USERIDS HERE
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
import encode


def normalize(d, target=1.0):
    charset = string.ascii_lowercase+" "
    raw = {}
    for ch in charset:
        countSum = 0
        for key, value in d.items():
            if key[0] == ch:
                countSum += value
        raw.update({ch: countSum})
    return {key: math.log10(value*target/(raw[key[0]])) for key, value in d.items()}


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

    return normalize(dist)


def generate_initial_tables():
    letters = list(range(ord('a'), ord('z')+1))
    random.shuffle(letters)
    replace_table = dict(zip(map(chr, range(ord('a'), ord('z')+1)), map(chr, letters)))
    rearrange_table = list(range(0, 4))
    random.shuffle(rearrange_table)
    return replace_table, rearrange_table


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

def calculate_log_likelihood(string, letter_distribution):
    s = 0
    string = " "+string
    i = 1
    while i < len(string):
        first_letter = string[i-1]
        second_letter = string[i]
        s += letter_distribution[(first_letter, second_letter)]
        i += 1
    return 10**s 

# put your code here!


def break_code(string, corpus, letter_distribution):
    import time
    start_time = time.time()
    f = open("demo.txt", "a")
    replace_table, rearrange_table = generate_initial_tables()
    max_iterations = 400000
    max_time_limit = 600
    iteration_count = 0
    best_document = [-1, ""]
    while time.time() - start_time < max_time_limit:
    #while iteration_count < max_iterations and time.time() - start_time < 600000:
        if random.choice([0,1]) == 0:
            new_replace_table = modify_replace_table(replace_table)
            new_rearrange_table = copy.deepcopy(rearrange_table)
        else: 
            new_rearrange_table = modify_rearrange_table(rearrange_table)
            new_replace_table = copy.deepcopy(replace_table)

        initial_document = encode.encode(string, replace_table, rearrange_table)
        probability_D = calculate_log_likelihood(initial_document, letter_distribution)
        updated_document = encode.encode(string, new_replace_table, new_rearrange_table)
        probability_D_new = calculate_log_likelihood(updated_document, letter_distribution)

        if probability_D_new > probability_D or random.random() < (probability_D_new/probability_D):
            replace_table = copy.deepcopy(new_replace_table)
            rearrange_table = copy.deepcopy(new_rearrange_table)
        #elif :
            #replace_table = copy.deepcopy(new_replace_table)
            #rearrange_table = copy.deepcopy(new_rearrange_table)

        if best_document[0] < probability_D_new:
            best_document[0] = probability_D_new
            best_document[1] = updated_document
            #f.write(str(best_document[0])+": "+best_document[1]+"\n----------------------------\n")

        iteration_count += 1
        print(iteration_count)
        #if iteration_count > max_iterations or (timeit.timeit()-start) > max_time_limit:
        #if (timeit.timeit()-start) > max_time_limit:
            #break
    f.close()
    return best_document[1]

if __name__ == "__main__":
    if(len(sys.argv) != 4):
        raise Exception("usage: ./break_code.py coded-file corpus output-file")
    encoded = encode.read_clean_file(sys.argv[1])
    corpus = encode.read_clean_file(sys.argv[2])
    # pickle_data.storeData(corpus,"part2/corpusPickle")

    # corpus = pickle_data.loadData("corpusPickle")

    expected_letter_distribution = build_letter_transition_dist(corpus)
    # pickle_data.storeData(expected_letter_distribution,"part2/letterTransitionPickle")
    # expected_letter_distribution = pickle_data.loadData("letterTransitionPickle")
    print("Done")
    decoded = break_code(encoded, corpus, expected_letter_distribution)

    with open(sys.argv[3], "w") as file:
        print(decoded, file=file)

    print("done")
