import csv
from itertools import product
import itertools
import random
from pprint import pprint
import pre_process

import rules
from FST_feature import FST_feature
# from SOSFIA import Sosfia, train_data_prod, check_the_difference, convert_data, extract_feat_pairs, check_if_functional, feat_search
from SOSFIA import *
import numpy as np
import pandas as pd
from itertools import combinations
from minimal_search import *

def reverse_data(data):
    result = []
    
    for item in data:
        # Reverse the list of tuples (without reversing the tuples themselves)
        reversed_tuple_list = [item[0][0]] + item[0][1:-1][::-1] + [item[0][-1]]
        
        # Reverse the second list
        # reversed_char_list = item[1][::-1]
        reversed_lst = [i[::-1] for i in item[1]]
        # Append the reversed pair to the result
        result.append((reversed_tuple_list, reversed_lst))
    
    return result

def ident_non_transitions(transitions, feat_repr):

    '''input:
        feat_repr = pre_process.seg_to_feat(file_sigma)

    returns a tuple (x,y):
        x= number of ident transitions
        y= number of non-ident transitions'''
    in_out = {v[0]: v[1] for v in feat_repr.values()} # navigating thru 2 featurral representations 
    ident = 0
    non_ident = 0
    for i in transitions:
        if i[1] == ('>',) or i[1] == ('<',):
            # print(f'Trans to final or to beginning: {i}')
            if not all(x == '' for x in i[2]):
                # print(f'non_ident: {i}')
                non_ident += 1
            else:
                # print(f'ident: {i}')
                ident += 1

        else:
            temp_reading = [x for x in i[1][0]]
            # print(temp_reading)
            if temp_reading != i[2]:
                # print(f'non_ident: {i}')
                non_ident += 1
            else:
                # print(f'ident: {i}')
                ident += 1


    return ident, non_ident

def main(file_sigma, file_delta, data_pairs):

    k = 2 #---> UPDATE K VALUE FOR A LANG
    # features_english = [[i] for i in pre_process.features(file_sigma)]
    features_english = [['cons'], ['son'], ['cont'], ['nasal', 'cons'], ['approx'], ['strid'], ['lat'],
    ['lab'], ['labdent'], ['cor'], ['dor'], ['ant'], ['voice'], ['round'], ['high'], ['low'], ['tense'],
    ['front'], ['back'], ['long'], ['delrel'], ['distr']] #---> UPDATE FEATS FOR A LANG

    sigma  = pre_process.sigma(file_sigma)
    delta = pre_process.delta(file_delta)
    gen_trans = pre_process.transitions_gen(sigma, k, file_sigma)


    trans = rules.nasalize(sigma, gen_trans, k, file_sigma)
    # reversed_trans = rules.nasalize_reverse(sigma, gen_trans, k, file_sigma)
    training_data = convert_data(data_pairs)
    # reversed_data = reverse_data(training_data)

    # training_data_feat = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, 3)
    # print('Feat data:')
    # pprint(training_data_feat)
    # training_data_feat = [[[('<',), ('-',), ('>',)], ['-']],
                        #     [[('<',), ('+',), ('>',)], ['+']],
          

                  # ([('<',), ('+',), ('+',), ('>',)], ['++'])]


#### CHECK IF ITS WORKING, NO MINIMAL SAMPLE ####

    # print('L2R')
    # for feat in features_english:
    #     if feat == ['nasal', 'cons']: # --> this is to just avoid searching feat combo
    #         k = 2                     # if from scratch use k=1
    #     else:
    #         k = 1
    #     # print(f'-------------------------\n{feat}:')
    #     # print(f'\t\tk={k}')
    #     sigma_feat = pre_process.sigma_feat(feat, file_sigma)
    #     # print(f'sigma: {len(sigma_feat)}')
    #     # print(f'sigma: {sigma_feat}')
    #     delta_feat = pre_process.delta_feat(feat, file_delta)
        
    #     states_feat = pre_process.states_gen(sigma_feat, k)
    #     # print(f'states: {len(states_feat)}')
    #     # print(states_feat)
    #     trans_feat = pre_process.extract_feats_trans(trans, feat, file_sigma, k)
    #     # print(f'trans total: {len(trans_feat)}')
    #     # pprint(trans_feat)
    #     ident_trans = ident_non_transitions(trans_feat, pre_process.seg_to_feat(file_sigma))[0]
    #     # print(f'\tident: {ident_trans}')
    #     non_ident_trans = ident_non_transitions(trans_feat, pre_process.seg_to_feat(file_sigma))[1]
    #     # print(f'\tnon_ident: {non_ident_trans}')
    #     training_data_feat = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, k)
    #     # print(f'pairs: {len(training_data_feat)}')
    #     ident_pairs = ident_nonident(training_data_feat)[0]
    #     # print(f'\tident: {len(ident_pairs)}')
    #     # pprint(ident_pairs)
    #     non_ident_pairs = ident_nonident(training_data_feat)[1]
    #     # print(f'\tnon_ident: {len(non_ident_pairs)}')
    #     # pprint(non_ident_pairs)

    # print('R2L')
    # for feat in features_english:
    #     if feat == ['nasal', 'cons']:
    #         k = 2
    #     else:
    #         k = 1
    #     print(f'-------------------------\n{feat}:')
    #     print(f'\t\tk={k}')
    #     sigma_feat = pre_process.sigma_feat(feat, file_sigma)
    #     print(f'sigma: {len(sigma_feat)}')
    #     print(f'sigma: {sigma_feat}')
    #     delta_feat = pre_process.delta_feat(feat, file_delta)
    #     states_feat = pre_process.states_gen(sigma_feat, k)
    #     print(f'states: {len(states_feat)}')
    #     print(states_feat)
    #     trans_feat = pre_process.extract_feats_trans(reversed_trans, feat, file_sigma, k)
    #     print(f'trans total: {len(trans_feat)}')
    #     ident_trans = ident_non_transitions(trans_feat, pre_process.seg_to_feat(file_sigma))[0]
    #     print(f'\tident: {ident_trans}')
    #     non_ident_trans = ident_non_transitions(trans_feat, pre_process.seg_to_feat(file_sigma))[1]
    #     print(f'\tnon_ident: {non_ident_trans}')
    #     training_data_feat = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), reversed_data, k)
    #     print(f'pairs: {len(training_data_feat)}')
    #     ident_pairs = ident_nonident(training_data_feat)[0]
    #     print(f'\tident: {len(ident_pairs)}')
    #     # pprint(ident_pairs)
    #     non_ident_pairs = ident_nonident(training_data_feat)[1]
    #     print(f'\tnon_ident: {len(non_ident_pairs)}')
    #     # pprint(non_ident_pairs)

#### MINIMAL SAMPLE ####

    FST = FST_feature(pre_process.states_gen(sigma, k), sigma, delta, '<<', '>', trans, pre_process.features(file_sigma))

    result = feat_gen_results(features_english, FST, training_data, file_sigma, file_delta, 1)
    # pprint(result)


    # # # # ###### GETTING INSUFFICIENT FEATURES WITH SMALLEST SAMPLE #############
    # # # 
    # # # for feature in insufficient_features:
	# # #     feature_keys = {k: v for k, v in result.items() if feature in k}
	# # #     feature_keys_min = min(feature_keys, key=lambda i: feature_keys[i][0])
	# # #     new_results[feature_keys_min] = [pair[0][1:-1] for pair in result[feature_keys_min][1]]

    # # print('\n\n\n--------------------=-=-=-=-=-====================----=-=-=----==============\n\n\n')
    
    new_results = {}
    for k1,v1 in result.items():
        print(f'feature: {k1}\t\t\t\t sample size: {v1[0]}')
        # if len(k) == 1:
        #     # if k[0] not in nasal_keys_min: # --> use when excluding already added combination 
        new_results[k1] = [pair[0][1:-1] for pair in result[k1][1]]

    # # pprint(new_results)

    # ############# keys are indexes and values features ################
    features_idxs = {}
    for i,v in pre_process.feature_id(file_sigma).items():
        features_idxs[v] = i
    # ###################################################################

    print('\n\n\n--------------------=-=-=-=-=-====================----=-=-=----==============\n\n\n')

    #  # # ################ changing feats to indexes #############
    new_results_idx = {}
    # pprint(new_results)
    # new_results = result # --> use when no feat combinations are required
    for ks,vs in new_results.items():
        
        if len(ks) == 1:
            # print(k)
            if ks[0] in features_idxs.keys():
                new_results_idx[features_idxs[ks[0]]] = vs
        else:
            # print(k)
            new_k = []
            for i in ks:
                if i in features_idxs.keys():
                    new_k.append(features_idxs[i])


            new_results_idx[tuple(new_k)] = vs 




    new_training_data = [pair[0][1:-1] for pair in training_data] # just inputs
    # new_training_data = [pair[0][1:-1] for pair in reversed_data] # just inputs

#### COMBINE FEATURES TOGETHER ####

    table, requirements, processed_data = construct_coverage_table(new_training_data, new_results_idx)

    columns = [f"({key}: {req})" for _, req, key in requirements]
    df = pd.DataFrame(table, index=[str(row) for row in processed_data], columns=columns)
    df["Sum"] = df.sum(axis=1)
    df = df.loc[df.sum(axis=1).sort_values(ascending=False).index, df.sum(axis=0).sort_values(ascending=False).index]

    print(df)
    pprint(df.columns)

    unsatisfied_constraints = df.loc[:, (df == 0).all(axis=0)].columns
    print("Constraints that are never satisfied:", unsatisfied_constraints.tolist())


    # Call the function on the generated DataFrame
    satisfying_subset = find_minimal_satisfying_subset(df)

    print(f'Original data: {len(new_training_data)}')
    # for i in new_training_data:
    #     if i not in satisfying_subset:
    #         print(f' not in sat subset: {i}')

    print(f'Satisfying subset of orignal data: {len(satisfying_subset)}')


# # #### FOR SOSFIA FEAT remember to use **return self.lcp_feat(out)** #---> common_out


    # pprint(satisfying_subset)







 

if __name__ == "__main__":
    # i = 1
    # while i <= 10:
    # 	print('##################################################################################################')
    # 	print(f'ROUND {i}')
    # 	main('English_features_26_9_sigma.tsv', 'English_features_26_9_delta.tsv', 'English_gen_pairs_26_9.tsv')
    # 	i += 1
    main('English_features_26_9_sigma.tsv', 'English_features_26_9_delta.tsv', 'English_gen_pairs_26_9_feat.tsv')
    # main('Yawelmani_features_7_sigma_delta.tsv', 'Yawelmani_features_7_sigma_delta.tsv', 'Yawel_gen_pairs_7_feat.tsv')
    # main('Chukchi_features_7_sigma.tsv', 'Chukchi_features_7_delta.tsv', 'Chukchi_gen_pairs_7_feat.tsv')
    # main('Polish_features_7_sigma_delta.tsv', 'Polish_features_7_sigma_delta.tsv', 'Polish_gen_pairs_7_feat.tsv')
    # main('Polish_features_8_sigma_delta.tsv', 'Polish_features_8_sigma_delta.tsv', 'Polish_gen_pairs_8_feat.tsv')
    # main('Polish_features_9_sigma_delta.tsv', 'Polish_features_9_sigma_delta.tsv', 'Polish_gen_pairs_9_feat.tsv')
    # main('Polish_features_10_sigma_delta.tsv', 'Polish_features_10_sigma_delta.tsv', 'Polish_gen_pairs_10_feat.tsv')












