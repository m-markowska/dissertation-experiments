import csv
from itertools import product
import itertools
import os
import random
from pprint import pprint
from . import preprocessing as pre_process
from . import rules
from .fst import FST_feature
# from SOSFIA import Sosfia, train_data_prod, check_the_difference, convert_data, extract_feat_pairs, check_if_functional, feat_search
from .learner import *
import numpy as np
import pandas as pd
from itertools import combinations


def set_random_seed(seed):
    """Seed both random generators used by the sample searches.

    Args:
        seed: Integer seed recorded with the experiment.

    Returns:
        The normalized integer seed.
    """
    normalized = int(seed)
    random.seed(normalized)
    np.random.seed(normalized % (2**32))
    return normalized


ACTIVE_RANDOM_SEED = None
if os.environ.get("FXF_SOSFIA_SEED") is not None:
    ACTIVE_RANDOM_SEED = set_random_seed(os.environ["FXF_SOSFIA_SEED"])


def output_to_input(pair):
    """Test whether a pair represents an identity mapping.

        Args:
            pair: One input-output training example.

        Returns:
            The output produced by `output_to_input`.
        """


    input_len = len(pair[0])-2
    new_input = []
    for p in pair[0][1:-1]:
        new_input.append(p[0])

    #print(new_input)
    new_output = []
    for i in range(input_len):
        word = ''
        for j in pair[1]:
            word += j[i]
        new_output.append(word)
    if new_output == new_input:
        return True
    else:
        #return f"The input is: {new_input}, the output is: {new_output}."
        return new_input, new_output



#print(seg_to_feats)
def feat_to_seg(data, seg_dict):
    """Convert feature-encoded data back to segment symbols.

        Args:
            data: Encoded input-output examples.
            seg_dict: Mapping between segments and feature encodings.

        Returns:
            The output produced by `feat_to_seg`.
        """

    #print(data)
    feat_dict = {}
    result = []
    for seg, feats in seg_dict.items():
        feat_dict[feats[0]] = seg
    for pair in data:
        new_pair = []
        for i in pair:
            new_list = []
            for j in i:
                if j in feat_dict.keys():
                    new_list.append(feat_dict[j])
            new_pair.append(new_list)
        result.append(new_pair)


    return result

# data = Rules('English_features_10_sigma.tsv', 'English_features_10_delta.tsv', 2)
# seg_to_feats = data.seg_to_feat()

def changed_pairs(data):
    """Select pairs whose input and output are different.

        Args:
            data: Encoded input-output examples.

        Returns:
            The output produced by `changed_pairs`.
        """

    count = 0
    changed = []
    for i in data:
        result = output_to_input(i)
        #print(output_to_input(i))
        if result == True:
            continue
        else:
            count +=1
            changed.append(result)
    return count, feat_to_seg(changed, seg_to_feats)



def ident_nonident(pairs, mode='feat'):
    """Partition pairs into identity and non-identity groups.

        Args:
            pairs: Input-output examples.
            mode: Requested representation or learning mode.

        Returns:
            The output produced by `ident_nonident`.
        """

    ident_pairs = []
    non_ident_pairs = []

    if mode == 'seg':

        for pair in pairs:
            new_input = pair[0][1:-1]
            new_output = [(x,) for x in pair[1]]
            # print(new_output)
            if new_input == new_output:
                ident_pairs.append(pair)
            else:
                non_ident_pairs.append(pair)
    else:

        # ident_pairs = []
        # non_ident_pairs = []
        for pair in pairs:
            new_out = []

            for j in range(len(pair[0])-2):
                temp = ''
    #             print(f"number: {j}")
                for i in pair[1]:
    #                 print(f"out i now is: {i[j]}")
                    temp = temp + i[j]
    #                 print("TEMP: ", temp)
                new_out.append((temp,))
            new_out.insert(0, ('<',))
            new_out.append(('>',))
            if pair[0] == new_out:
                ident_pairs.append((pair[0], pair[1]))
            else:
                non_ident_pairs.append((pair[0], pair[1]))
    return ident_pairs, non_ident_pairs




def generate_combinations(features, feat, l):
    """Generate feature sets that retain the required features.

        Args:
            features: Ordered selected feature names.
            feat: Ordered selected feature names.
            l: Requested total number of selected features.

        Returns:
            The output produced by `generate_combinations`.
        """
    # Ensure picked features are part of the original feature set
    remaining_features = [f for f in features if f not in feat]

    # The number of additional features needed to reach length l
    needed = l - len(feat)

    # If the picked list is already larger than l, return an empty list
    if needed < 0:
        return []

    # Generate combinations from remaining features
    combinations = [
        feat + list(combo)
        for combo in itertools.combinations(remaining_features, needed)
    ]

    return combinations


def minimal_sample_full(pairs, FST, current_sample=None, switch=True):
    """Search incrementally for a sufficient full-feature sample.

        Args:
            pairs: Input-output examples.
            FST: Gold or structural feature transducer used for learning and evaluation.
            current_sample: Examples accumulated by incremental sample search.
            switch: Flag controlling which sample group is drawn next.

        Returns:
            The output produced by `minimal_sample_full`.
        """


    pairs_ident = ident_nonident(pairs, 'seg')[0]
    pairs_nonident = ident_nonident(pairs, 'seg')[1]

    if current_sample is None:
        current_sample = []

    # print(f"Len of ident pairs: {len(pairs_ident)}")
    # print(f"Len of non-indent pairs: {len(pairs_nonident)}")
    # Continue picking as long as there are elements in either list
    while pairs_ident or pairs_nonident:
        if switch and pairs_ident:  # Pick from pairs_ident if it's the turn and not empty
            num_to_pick = min(50, len(pairs_ident))  # Pick 10 or all remaining elements
            chosen_pairs = random.sample(pairs_ident, num_to_pick)
            pairs_ident = [item for item in pairs_ident if item not in chosen_pairs]

        elif not switch and pairs_nonident:  # Pick from pairs_nonindent if it's the turn and not empty
            num_to_pick = min(50, len(pairs_nonident))
            chosen_pairs = random.sample(pairs_nonident, num_to_pick)
            pairs_nonident = [item for item in pairs_nonident if item not in chosen_pairs]

        # If one list is empty, always pick from the non-empty one
        elif not pairs_ident and pairs_nonident:
            num_to_pick = min(50, len(pairs_nonident))
            chosen_pairs = random.sample(pairs_nonident, num_to_pick)
            pairs_nonident = [item for item in pairs_nonident if item not in chosen_pairs]

        elif not pairs_nonident and pairs_ident:
            num_to_pick = min(50, len(pairs_ident))
            chosen_pairs = random.sample(pairs_ident, num_to_pick)
            pairs_ident = [item for item in pairs_ident if item not in chosen_pairs]

        # Add selected pairs to the current sample
        current_sample += chosen_pairs
        # print(f"Current sample size: {len(current_sample)}")
        # print(f"Len of ident pairs: {len(pairs_ident)}")
        # print(f"Len of non-indent pairs: {len(pairs_nonident)}")

        FST_ident = FST_feature(FST.states, FST.in_alphabet, FST.out_alphabet, '<<', '>', FST.identity_trans('seg'), FST.feature)
        # FST_ident = FST_feature(FST.states, FST.in_alphabet, FST.out_alphabet, '<<', '>', FST.clear_trans_output(), FST.feature)
        sosfia = Sosfia(current_sample, FST_ident, FST_ident.feature)
        sosfia_trans = sosfia.fill_in_trans_seg()
        output = check_the_difference(FST.transitions, sosfia_trans)

        if output == "It's a match":
            print(f"Lenght of a sufficient sample is \t\t: {len(current_sample)}")
            return

        # else:
        #     print(output)

        # Toggle switch for next iteration
        switch = not switch

    # Recursively call the function if more elements need to be selected
    return minimal_sample_full(pairs, FST, current_sample, switch)




def minimal_sample_feat(feat, feat_pairs, training_data, FST, file_sigma, file_delta, k, current_sample=None, switch=True, batch_size=None):
    """Search incrementally for a sufficient projected-feature sample.

        Args:
            feat: Ordered selected feature names.
            feat_pairs: Training pairs projected onto the selected features.
            training_data: Complete training pairs in the active representation.
            FST: Gold or structural feature transducer used for learning and evaluation.
            file_sigma: Input feature-inventory path.
            file_delta: Output feature-inventory path.
            k: Locality or memory bound.
            current_sample: Examples accumulated by incremental sample search.
            switch: Flag controlling which sample group is drawn next.
            batch_size: Optional number of pairs drawn on every iteration.

        Returns:
            The output produced by `minimal_sample_feat`.
        """
    # print(f"=== Starting minimal_sample_feat with feature(s): {feat} ===")
    # print(f"Len of trainign data for {feat} is {len(feat_pairs)}")
    if batch_size is not None:
        batch_ident = batch_size
        batch_nonident = batch_size
    elif len(feat_pairs) < 400:
        batch_ident = 1
        batch_nonident = 1
    else:
        batch_ident = 10
        batch_nonident = 100
    # Base case for current_sample
    # print(f'K at the beginning: {k}')

    if current_sample is None:



        len_one_pairs = [i for i in feat_pairs if len(i[0]) == 3]
        # pprint(f'Here are strings of len 1: {len_one_pairs}')
        len_non_one_pairs = [i for i in feat_pairs if len(i[0]) > 3]
        current_sample = len_one_pairs
    # print(f'Batch: {batch}')
    # print(f'Sample size at the start: {current_sample}')

    output = feat_search(FST, feat, current_sample, training_data, file_sigma, file_delta, k)
    # print(f"🔍 Output of feat_search: {output}")


    # Check if the current feature is sufficient
    if learn_feat(feat, FST, feat_pairs, training_data, file_sigma, file_delta, k) != 'Add another feature':
        print(f"🎯 Found valid feature: {feat}")

        pairs_ident, pairs_nonident = ident_nonident(len_non_one_pairs)
        # pairs_ident, pairs_nonident = ident_nonident(feat_pairs)


        # Continue selecting samples while data exists
        while pairs_ident or pairs_nonident:
            if switch and pairs_ident:
                chosen_pairs = random.sample(pairs_ident, min(batch_ident, len(pairs_ident)))
                pairs_ident = [item for item in pairs_ident if item not in chosen_pairs]
            elif not switch and pairs_nonident:
                chosen_pairs = random.sample(pairs_nonident, min(batch_nonident, len(pairs_nonident)))
                pairs_nonident = [item for item in pairs_nonident if item not in chosen_pairs]
            elif pairs_nonident:  # Fallback if ident is empty
                chosen_pairs = random.sample(pairs_nonident, min(batch_nonident, len(pairs_nonident)))
                pairs_nonident = [item for item in pairs_nonident if item not in chosen_pairs]
            elif pairs_ident:  # Fallback if non-ident is empty
                chosen_pairs = random.sample(pairs_ident, min(batch_ident, len(pairs_ident)))
                pairs_ident = [item for item in pairs_ident if item not in chosen_pairs]
            else:
                break  # No more data to sample

            # print('Those are chosen pairs', chosen_pairs)
            current_sample += chosen_pairs
            # print(f"📊 Current sample size: {len(current_sample)}")
            # pprint(f'And this is the current_sample size after chosen_pairs: {len(current_sample)}')

            output = feat_search(FST, feat, current_sample, training_data, file_sigma, file_delta, k)
            # print(f"🔍 Output of feat_search: {output}")

            if output != 'More data':
                return output  # Return as soon as a sufficient sample is found
            # else:
            #     if len(output) <= 10:
            #         print(f"Len of ident pairs: {len(pairs_ident)}")
            #         print(f"Len of non-indent pairs: {len(pairs_nonident)}")
            #         print(f"Current sample size: {len(current_sample)}")
            #         print(output)

            switch = not switch

        return "More data"  # No sufficient sample found with the current feature

    else:
        # If the feature alone is insufficient, try adding more features
        output = []  # To collect all successful combinations
        length = 2   # Start with pairs of features

        # print(f"\n❗ Adding more features to: {feat}")

        while not output:  # Continue until at least one successful combination is found
            combos = generate_combinations(FST.feature, feat, length)
            # print(f"🔗 Trying combinations of length {length}: {combos}")

            for combo in combos:
                # print(f"➡️ Testing combo: {combo}")
                # print(f'\t\t\t\t\t\t k={k}')
                # feat_pairs = extract_feat_pairs(combo, Rules(sigmatsv,sigmatsv, k).feature_id(), training_data) ------
                feat_pairs = extract_feat_pairs(combo, pre_process.feature_id(file_sigma), training_data, k)
                # print(f"Len of feat pairs: {len(feat_pairs)}")
                # print('feat pairs:')
                # for i in feat_pairs:
                #     print(i)
                if not is_functional(feat_pairs):
                    # print(f"\n\n\n Not functional sample for combo: {combo} \n\n\n")
                    continue
                else:
                    # print(f"\n\n\n Len of extracted pairs in the ELSE condition: {len(feat_pairs)}")
                    result = minimal_sample_feat(
                        combo, feat_pairs, training_data, FST, file_sigma,
                        file_delta, k, batch_size=batch_size,
                    )
                    # print(f"🔎 Result for combo {combo}: {result}")

                    if result != 'More data':
                        # print(f"✅ Successful combination found: {combo}")
                        output.append(result)  # Store the successful combination
                    # else:
                    #     if len(result) <= 10:
                    #         print(f"Len of ident pairs: {len(pairs_ident)}")
                    #         print(f"Len of non-indent pairs: {len(pairs_nonident)}")
                    #         print(f"Current sample size: {len(current_sample)}")
                    #         print(result)

            if not output:
                length += 1  # Increase combination length only if no successful combos were found

        return output  # Return all successful combinations






def learn_feat(feat, FST, feat_pairs, training_data, file_sigma, file_delta, k):
    """Learn and evaluate one selected feature representation.

        Args:
            feat: Ordered selected feature names.
            FST: Gold or structural feature transducer used for learning and evaluation.
            feat_pairs: Training pairs projected onto the selected features.
            training_data: Complete training pairs in the active representation.
            file_sigma: Input feature-inventory path.
            file_delta: Output feature-inventory path.
            k: Locality or memory bound.

        Returns:
            The output produced by `learn_feat`.
        """

    # data = Rules(sigmatsv, sigmatsv, k) -----
    # print(f'K insiade learn_feat: {k} for feature: {feat}')
    extracted_trans = pre_process.extract_feats_trans(FST.transitions, feat, file_sigma, k)
    # data.extract_feats_trans(FST.transitions, feat) -------
    # print('Original trans:')
    # for i in extracted_trans:
    #     print(i)
    # feat_pairs = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, k) #--> use when no min_sample


    # pprint(feat_pairs)
    # for i in feat_pairs:
    #     print(f'pair:                   {i}')
    # print(f'Output for is_functional(feat_pairs) for {feat}: {is_functional(feat_pairs)}')
    if not is_functional(feat_pairs):
        # insufficient.append(feat)
        # combos = generate_combinations(FST.feature, [feat], length)

        return "Add another feature"
    else:
        # print("Sample of len", len(feat_pairs), "is functional")
        # print(f"FEAT: \t\t\t\t\t\t {feat}")
        # print(f"Here is sigma for feature {feat}: \n\n {data.sigma_feat(feat)}")
        # fst_feat = FST_feature(data.states_gen(data.sigma_feat(feat)), data.sigma_feat(feat), data.delta_feat(feat),
        #              '<<', '>', extracted_trans, feat) ----
        sigma_feat = pre_process.sigma_feat(feat, file_sigma)
        delta_feat = pre_process.delta_feat(feat, file_delta)
        states_feat = pre_process.states_gen(sigma_feat, k)
        fst_feat = FST_feature(states_feat, sigma_feat, delta_feat, '<<', '>', extracted_trans, feat)
        # print('+++++++ IN ALPHABET +++++++')
        # pprint(fst_feat.in_alphabet)
        # print('----STaTES ------')
        # pprint(fst_feat.states)
        # pprint(fst_feat.nested_dict_trans())
        # ensuring onwardnes (full means built from the *full* feature sample):
        # fst_feat_ident = FST_feature(data.states_gen(data.sigma_feat(feat)), data.sigma_feat(feat), data.delta_feat(feat),
        #              '<<', '>', fst_feat.identity_trans(), feat) -------
        # print('IDENT before definig fst_feat:')
        # pprint(fst_feat.identity_trans())
        fst_feat_ident = FST_feature(states_feat, sigma_feat, delta_feat, '<<', '>', fst_feat.identity_trans(), feat)
        # full_feat_pairs = extract_feat_pairs(feat, data.feature_id(), training_data) ------
        # print('IDENT after definig fst_feat and before fst_ident:')
        # pprint(fst_feat.identity_trans())
        full_feat_pairs = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, k)
        # pprint(f'Here are extracted_pairs1: ')
        # for j in full_feat_pairs:
        #     print(j)
        # print('ident1 before sosßfia def: ')
        # pprint(fst_feat_ident.transitions)
        sosfia_full_feat = Sosfia(feat_pairs, fst_feat_ident, feat)
        # for i, j in sosfia_full_feat.nested_dict_trans().items():
        #     print(i, j)
        onward_trans = sosfia_full_feat.fill_in_trans()
        output = check_the_difference(extracted_trans, onward_trans)

        if output == "It's a match":
            # print('\n INSIDE learn_feat: output equals its a match \n')
            # pprint(feat_pairs)
            return (feat, len(feat_pairs)), feat_pairs
            # return feat, len(feat_pairs) #--> use when only feats and len of pairs
        else:
            # print('\n\n now in the else \n\n')
            # print('\n')
            # pprint(output)
            return "More data"



def feat_search(FST, feat, feat_pairs, training_data, file_sigma, file_delta, k, length=2):
    """Search feature combinations until learning succeeds.

        Args:
            FST: Gold or structural feature transducer used for learning and evaluation.
            feat: Ordered selected feature names.
            feat_pairs: Training pairs projected onto the selected features.
            training_data: Complete training pairs in the active representation.
            file_sigma: Input feature-inventory path.
            file_delta: Output feature-inventory path.
            k: Locality or memory bound.
            length: Requested combination or substring length.

        Returns:
            The output produced by `feat_search`.
        """


    # length = 2
    # data = Rules(sigmatsv, sigmatsv, k)

    while learn_feat(feat, FST, feat_pairs, training_data, file_sigma, file_delta, k) != 'Add another feature':
        # print(f"Found valid feature: {feat} \n\n\n\n")
        # print(learn_feat(feat, FST, training_data, sigmatsv, k))
        return learn_feat(feat, FST, feat_pairs, training_data, file_sigma, file_delta, k)
    else:
        # print("Entering combo generation...")
        good_combos = []
        combos = generate_combinations(FST.feature, feat, length)

        for combo in combos:
            # print(f'\nCOMBO: {combo}')

            # feat_pairs = extract_feat_pairs(combo, data.feature_id(), training_data) ----
            feat_pairs = extract_feat_pairs(combo, pre_process.feature_id(file_sigma), training_data, k)
            # print(minimal_sample_feat(combo, feat_pairs, training_data, FST, sigmatsv, k, current_sample, switch))
            result = learn_feat(combo, FST, feat_pairs, training_data, file_sigma, file_delta, k)
            # print(f"Combo: {combo}, Result: {result}")
            if result != 'Add another feature':
                good_combos.append(result)
            # if len(good_combos) >= 2: --> use when you want only 2 combos
            #     break


    if good_combos:
        # print(f"Good combos found: {good_combos}")
        return good_combos
    else:
        length += 1
        feat_search(FST, feat, feat_pairs, training_data, file_sigma, file_delta, k, length)

    # print("No valid features or combos found.")
    return "More data"


def feat_gen_results(features, FST, training_data, file_sigma, file_delta, k, initial_k=None):
    """Collect characteristic-sample results for feature configurations.

        Args:
            features: Ordered selected feature names.
            FST: Gold or structural feature transducer used for learning and evaluation.
            training_data: Complete training pairs in the active representation.
            file_sigma: Input feature-inventory path.
            file_delta: Output feature-inventory path.
            k: Locality or memory bound.
            initial_k: Starting memory bound for the search.

        Returns:
            The output produced by `feat_gen_results`.
        """


    if initial_k is None:
        initial_k = k  # Save the initial value on first call

    feat_min_s_result = dict()

    for feat in features:
        print(f"\n\nConsidering feature: {feat}-------------------------")
        current_k = initial_k  # <-- Reset k at the start of each feature
        # print('Now k=', current_k)

        feat_pairs = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, current_k)

        result = minimal_sample_feat(feat, feat_pairs, training_data, FST,
            file_sigma, file_delta, k, current_sample=None, switch=True)
        # print(f'result at the beginning:  \n {result}')


        while result == 'More data':
            current_k += 1
            # print('now k =', current_k)

            feat_pairs = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, current_k)
            result = minimal_sample_feat(feat, feat_pairs, training_data, FST,
                file_sigma, file_delta, current_k, current_sample=None, switch=True)

            if result != 'More data':
                # print(f'K={k}')
                feat_key = tuple(result[0][0])
                # pprint(sorted(result[1], key=lambda x: len(x[0])))
                if feat_key not in feat_min_s_result.keys():
                    feat_min_s_result[feat_key] = (result[0][1], sorted(result[1], key=lambda x: len(x[0])))
        if type(result) != tuple:
            # print('RESULTTTTTTTTTTTTT:')
            # print(result)
            result = sorted(result, key=lambda x: x[1])
            for i in result:
                feat_key = tuple(i[0][0])
                if feat_key not in feat_min_s_result.keys():
                    feat_min_s_result[feat_key] = (i[0][1], sorted(i[1], key=lambda x: len(x[0])))

        feat_key = tuple(result[0][0])
        # pprint(sorted(result[1], key=lambda x: len(x[0])))
        if feat_key not in feat_min_s_result.keys():
            feat_min_s_result[feat_key] = (result[0][1], sorted(result[1], key=lambda x: len(x[0])))


    return feat_min_s_result
    # return
def feat_gen_results_polish(features, FST, training_data, file_sigma, file_delta, k, initial_k=None):
    """Collect Polish characteristic-sample results by feature.

        Args:
            features: Ordered selected feature names.
            FST: Gold or structural feature transducer used for learning and evaluation.
            training_data: Complete training pairs in the active representation.
            file_sigma: Input feature-inventory path.
            file_delta: Output feature-inventory path.
            k: Locality or memory bound.
            initial_k: Starting memory bound for the search.

        Returns:
            The output produced by `feat_gen_results_polish`.
        """


    if initial_k is None:
        initial_k = k  # Save the initial value on first call

    feat_min_s_result = dict()

    for feat in features:
        print(f"\n\nConsidering feature: {feat}-------------------------")
        if feat == ['voice', 'son']:
            initial_k = 2
        elif feat == ['high', 'voice', 'nasal', 'low'] or feat == ['tense', 'voice', 'nasal', 'round']:
            initial_k = 3

        else:
            initial_k = 1
        # print(f'initial_k = {initial_k}')
        current_k = initial_k  # <-- Reset k at the start of each feature

        feat_pairs = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, current_k)

        result = minimal_sample_feat(feat, feat_pairs, training_data, FST,
            file_sigma, file_delta, current_k, current_sample=None, switch=True)
        # print(f'result at the beginning:  \n {result}')

        while result == 'More data':
            current_k += 1
            # print('now k =', current_k)

            feat_pairs = extract_feat_pairs(feat, pre_process.feature_id(file_sigma), training_data, current_k)
            result = minimal_sample_feat(feat, feat_pairs, training_data, FST,
                file_sigma, file_delta, current_k, current_sample=None, switch=True)

            if result != 'More data':
                # print(f'K={k}')
                feat_key = tuple(result[0][0])
                # pprint(sorted(result[1], key=lambda x: len(x[0])))
                if feat_key not in feat_min_s_result.keys():
                    feat_min_s_result[feat_key] = (result[0][1], sorted(result[1], key=lambda x: len(x[0])))
        if type(result) != tuple:
            # print('RESULTTTTTTTTTTTTT:')
            # print(result)
            result = sorted(result, key=lambda x: x[1])
            for i in result:
                feat_key = tuple(i[0][0])
                if feat_key not in feat_min_s_result.keys():
                    feat_min_s_result[feat_key] = (i[0][1], sorted(i[1], key=lambda x: len(x[0])))

        feat_key = tuple(result[0][0])
        # pprint(sorted(result[1], key=lambda x: len(x[0])))
        if feat_key not in feat_min_s_result.keys():
            feat_min_s_result[feat_key] = (result[0][1], sorted(result[1], key=lambda x: len(x[0])))


    return feat_min_s_result


def feat_pairs_to_seg_pairs(data, pairs):

    """input: minimal_sample_feat output for each feature, list of lists of tuples

    Args:
        data: Encoded input-output examples.
        pairs: Input-output examples.

    Returns:
        None.
    """

def satisfies_requirement(original, requirement, positions):
    """Check if the original data point satisfies the given requirement at the specified positions.
        #

        Args:
            original: Original domain or mapping used for comparison.
            requirement: Coverage requirement being evaluated.
            positions: Positions at which a symbol occurs in the examples.

        Returns:
            The output produced by `satisfies_requirement`.
        """
    # print('-----------------------------------------')
    # print(f'BASE CASE')
    # print(f'string: {original} \nsubstring: {requirement}')
    if len(original) != len(requirement):
        return False  # Length mismatch

    for i, req_tuple in enumerate(requirement):
        for j, pos in enumerate(positions):
            if pos < len(original[i][0]):  # Ensure position is within bounds
                if req_tuple[j] != original[i][0][pos]:
                    return False
    # print(f'The requirement {requirement} for the string {original} is satisfied at position {positions}')
    return True

def satisfies_tuple_requirement(original, requirement, positions):
    """Special case for constraints where key is a tuple, checking multiple positions at once.
        Ensures each required character is at the correct position in the respective string.

        Args:
            original: Original domain or mapping used for comparison.
            requirement: Coverage requirement being evaluated.
            positions: Positions at which a symbol occurs in the examples.

        Returns:
            The output produced by `satisfies_tuple_requirement`.
        """
    # print('+++++++++++++++++++++++++++++++++++++++++')
    # print(f'TUPLE CASE')
    # print(f'string: {original} \nsubstring: {requirement}')
    if len(original) != len(requirement):
        # print('Len of string is less than the requirement')
        return False  # Not enough data points to compare

    for i, req_tuple in enumerate(requirement):  # Iterate over required strings
        for j, pos in enumerate(positions):  # Iterate over required positions
            if pos >= len(original[i][0]):  # Ensure position is within bounds
                return False
            if req_tuple[0][j] != original[i][0][pos]:  # Check required character at position
                return False
    # print(f'The requirement {requirement} for the string {original} is satisfied at position {positions}')

    return True



def construct_coverage_table(original_data, feature_dict):
    """Constructs a binary coverage table where rows are original data points and columns are dictionary constraints.

        Args:
            original_data: Unprojected input-output examples.
            feature_dict: Mapping between segments and feature values.

        Returns:
            The output produced by `construct_coverage_table`.
        """
    original_data = [tuple(map(tuple, row)) for row in original_data]  # Normalize data format

    requirements = []  # List of (positions, requirement, key)
    for key, values in feature_dict.items():
        positions = key if isinstance(key, tuple) else (key,)
        for req in values:
            requirements.append((positions, req, key))  # Store key for indexing

    table = np.zeros((len(original_data), len(requirements)), dtype=int)

    for i, original in enumerate(original_data):
        for j, (positions, requirement, key) in enumerate(requirements):
            if isinstance(key, tuple):
                if satisfies_tuple_requirement(original, requirement, positions):
                    table[i, j] = 1
            else:
                if satisfies_requirement(original, requirement, positions):
                    table[i, j] = 1

    return table, requirements, original_data

def find_minimal_satisfying_subset(df):
    """Identifies the minimal subset of original data points that collectively satisfy all constraints.

        Args:
            df: Coverage matrix used by sample selection.

        Returns:
            The output produced by `find_minimal_satisfying_subset`.
        """
    remaining_constraints = set(df.columns[1:])  # Exclude the first column (original data points)
    satisfying_subset = []

    for index, row in df.iterrows():
        # print(f'index: {index}\nrow: {row}')
        satisfied_constraints = set(row[row == 1].index)
        len_before = len(remaining_constraints)
        # print(f'Length of remaining constraints: {len(remaining_constraints)}')
        # print(f'satisfied_constraints: {satisfied_constraints}')
        # pprint(remaining_constraints)
        remaining_constraints -= satisfied_constraints  # Remove satisfied constraints
        len_after = len(remaining_constraints)
        # print(f'AFTER:          Length of remaining constraints: {len(remaining_constraints)}')

        if len_before != len_after:
            # print(index)
            # print(f"\n\nDatapoint: {index} gets added YAYAYAYAY\n\n")
            # satisfying_subset.append(list(index))
            satisfying_subset.append(index)
        # else:
        #     print(f"\n\nDatapoint: {index} is useless \n SAD PANDA\n\n")

        # Convert string representation of tuples back into actual tuples
        if isinstance(index, str):
            index = eval(index)  # Safely evaluate the string as a tuple

        # satisfying_subset.append(list(index))  # Ensure output format as list of tuples

        if not remaining_constraints:  # Stop once all constraints are satisfied
            break

    # print("Minimal subset of data points satisfying all constraints:")
    result = []
    for item in satisfying_subset:
        # print('before: ', item)
        new_data_point = [('<',)]
        for i in eval(item):
            new_data_point.append(i)
        new_data_point.append(('>',))
        # print(new_data_point)
        result.append(new_data_point)


    # return satisfying_subset
    return result

def save_gen_pairs(gen_pairs, file_name):

    """combines all features to represent segments

    Args:
        gen_pairs: Input-output examples.
        file_name: Path to the data file being written or read.

    Returns:
        None.
    """

    with open(file_name, 'w', encoding='UTF8') as f:
    # create the csv writer
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(["Input", "Output"])
        for i in gen_pairs:
            writer.writerow([i[0], i[1]])
