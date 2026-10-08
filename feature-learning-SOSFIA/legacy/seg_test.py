import csv
from itertools import product
import itertools
import random
from pprint import pprint
from pre_process import pre_process
from rules import Rules
from FST_feature import FST_feature
# from SOSFIA import Sosfia, train_data_prod, check_the_difference, convert_data, extract_feat_pairs, check_if_functional, feat_search
from SOSFIA import *
import numpy as np
import pandas as pd
from itertools import combinations
from minimal_search import *

def data_seg_to_feat(data, training_data):

    data_feat = []

    seg_to_feat = data.seg_to_feat()

    for i in training_data:
        # print(i)
        new_input = [(seg_to_feat[x[0]][0],) for x in i[0][1:-1]]
        # print(new_input)
        # new_output = [seg_to_feat[x][0] for x in i[1]]
        new_output = [''.join(map(str, item)) for item in zip(*[seg_to_feat[x][1] for x in i[1]])]
        # print(new_output)
        new_input.insert(0, ('<',))
        new_input.append(('>',))
        data_feat.append([new_input, new_output])

    return data_feat

def reverse_data(data):
    result = []
    
    for item in data:
        # Reverse the list of tuples (without reversing the tuples themselves)
        reversed_tuple_list = [item[0][0]] + item[0][1:-1][::-1] + [item[0][-1]]
        
        # Reverse the second list
        reversed_char_list = item[1][::-1]
        
        # Append the reversed pair to the result
        result.append((reversed_tuple_list, reversed_char_list))
    
    return result



def main(file_sigma, file_delta, k, data_pairs):
    data = Rules(file_sigma, file_delta, k)
    sigma = data.sigma_seg()
    # print(sigma)

    trans = data.nasalize_seg(sigma) # --> update the rules as needed
    trans_reversed = data.nasalize_seg_reverse(sigma)
    pprint(trans)


    FST = FST_feature(data.states_gen(sigma), sigma, data.delta(), '<<', '>', trans, data.features())
    # FST_reversed = FST_feature(data.states_gen(sigma), sigma, data.delta(), '<<', '>', trans_reversed, data.features())
    # # # pprint(FST.nested_dict_trans())
    # # # trans_ident = FST.identity_trans('seg')
    # # trans_ident = FST.identity_trans()

    FST_ident = FST_feature(data.states_gen(data.sigma_seg()), data.sigma_seg(), data.delta_seg(), 
                                 '<<', '>', FST.identity_trans('seg'), data.features())

    # FST_reversed_ident = FST_feature(data.states_gen(data.sigma_seg()), data.sigma_seg(), data.delta_seg(), 
                                 # '<<', '>', FST_reversed.identity_trans('seg'), data.features())
    # FST_ident = FST_feature(data.states_gen(sigma), sigma, data.delta(), 
    #                         '<<', '>', trans_ident, data.features())

    training_data = convert_data(data_pairs)
    # reversed_training_data = reverse_data(training_data)

    sosfia = Sosfia(training_data, FST_seg_empty, FST_empty.feature)
    # sosfia = Sosfia(reversed_data, FST_reversed_ident, FST_reversed_ident.feature)
    # # # # sosfia = Sosfia(training_data, FST_ident, FST_ident.feature)
    sosfia_trans = sosfia.fill_in_trans_seg()
    # pprint(check_the_difference(trans_reversed, sosfia_trans))
    pprint(check_the_difference(trans, sosfia_trans))

    len_one_pairs = [] # --> pairs of len = 1 are given always as a default
    len_non_one_pairs = []
    for i in training_data:
        if len(i[0]) == 3:
            len_one_pairs.append(i)
        else:
            len_non_one_pairs.append(i)
#     # print(len(len_one_pairs))
#     # print(len(len_non_one_pairs))

#     # print('Round: ', 1)
    print(minimal_sample_full(len_non_one_pairs, FST_reversed, len_one_pairs, switch=True))
    print('----------------------------------------------------------------------\n\n')


if __name__ == "__main__":
    # i = 1
    # while i <= 10:
    #     print('##################################################################################################')
    #     print(f'ROUND {i}')
    #     main('English_features_26_9_sigma.tsv', 'English_features_26_9_delta.tsv', 2, 'English_gen_pairs_26_9_seg.tsv')
    #     i += 1
    main('English_features_26_9_sigma.tsv', 'English_features_26_9_delta.tsv', 'English_gen_pairs_26_9_seg.tsv')
    # main('Polish_features_7.tsv', 'Polish_features_7.tsv', 3, 'Polish_gen_pairs_7_seg.tsv')
    # main('Yawelmani_features_7.tsv', 'Yawelmani_features_7.tsv', 3, 'Yawel_gen_pairs_7_seg.tsv')
    # main('Chukchi_features_7_sigma.tsv', 'Chukchi_features_7_delta.tsv', 3, 'Chukchi_gen_pairs_7_seg.tsv')


