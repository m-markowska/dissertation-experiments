import csv
from itertools import product
import itertools
import random


def feature_list_sigma(file_sigma):
    """reads the segments/features data and saves it to a list
        output: list, e.g. ['Segment', 'a', 'm', 't', 'ą', '>'], ['nasal', '-', '+', '-', '+', ''], ...

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `feature_list_sigma`.
        """

    list_segs = []
    with open(file_sigma, newline='') as csvfile:
        segments = csv.reader(csvfile, delimiter='\t')
        for row in segments:
            list_segs.append(row)
    return list_segs

def feature_list_delta(file_delta):
    """reads the segments/features data and saves it to a list
        output: list, e.g. ['Segment', 'a', 'm', 't', 'ą', '>'], ['nasal', '-', '+', '-', '+', ''], ...

        Args:
            file_delta: Output feature-inventory path.

        Returns:
            The output produced by `feature_list_delta`.
        """

    list_segs = []
    with open(file_delta, newline='') as csvfile:
        segments = csv.reader(csvfile, delimiter='\t')
        for row in segments:
            list_segs.append(row)
    return list_segs

def features(file_sigma):
    """outputs features for a given dataset
        output: str, e.g. ['nasal', 'coronal', ...]

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `features`.
        """

    output = [lst[0] for lst in feature_list_sigma(file_sigma)[1:]]
    return output


def feature_values(file_sigma):
    """creates embedded dictionary with keys as features and all the values
        observed in data per feature, as values
        output: dict. e.g. {'nas': {'+', '-'}, 'len': {'+', '-', '0'}}

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `feature_values`.
        """

    feature_list = feature_list_sigma(file_sigma)
    feat_dict = dict()
    for i in feature_list[1:]:
        i_copy = i.copy()
        for j in i:
            if j == ' ':
                i_copy.remove(j)
            max_val = set(i_copy[1:])
            feat_dict[i[0]] = max_val

    return feat_dict

def feature_id(file_sigma):
    """associates every feature with an id number
        output: dict, e.g. {0: 'nas', 1: 'con'}

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `feature_id`.
        """

    dictionary = {}
    for i, item in enumerate(features(file_sigma)):
        dictionary[i] = item
    return dictionary


def seg_dict(file_sigma):
    """creates a dictionary where the key is a segment and values consist of another dictionary,
        where a feature is a key and a value is a value for that feature of the segment
        input: list
        output: dict of dict, e.g. {'a': {'con': '-', 'nas': '-'}, 'm': {...}

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `seg_dict`.
        """

    seg_list = feature_list_sigma(file_sigma)
    segments_dict = {}
    for seg in seg_list[0][1:]:
        features_dict = {}
        idx = seg_list[0][1:].index(seg)+1
        if seg_list[0][idx] == seg:
            for i in range(len(seg_list)-1):
                i += 1
                features_dict[seg_list[i][0]] = seg_list[i][idx]
                segments_dict[seg] = features_dict
        segments_dict[seg] = features_dict

    return segments_dict

def seg_dict_delta(file_delta):
    """creates a dictionary where the key is a segment and values consist of another dictionary,
        where a feature is a key and a value is a value for that feature of the segment
        input: list
        output: dict of dict, e.g. {'a': {'con': '-', 'nas': '-'}, 'm': {...}

        Args:
            file_delta: Output feature-inventory path.

        Returns:
            The output produced by `seg_dict_delta`.
        """

    seg_list = feature_list_delta(file_delta)
    segments_dict = {}
    for seg in seg_list[0][1:]:
        features_dict = {}
        idx = seg_list[0][1:].index(seg)+1
        if seg_list[0][idx] == seg:
            for i in range(len(seg_list)-1):
                i += 1
                features_dict[seg_list[i][0]] = seg_list[i][idx]
                segments_dict[seg] = features_dict
        segments_dict[seg] = features_dict

    return segments_dict

def feat_temp(file_sigma):
    """creates an empty template for each feature
        output: list of empty strings, e.g. ['', '', ...]

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `feat_temp`.
        """

    return [""] * len(features(file_sigma))

def feat_temp_delta(file_delta):
    """creates an empty template for each feature
        output: list of empty strings, e.g. ['', '', ...]

        Args:
            file_delta: Output feature-inventory path.

        Returns:
            The output produced by `feat_temp_delta`.
        """

    return [""] * len(features(file_delta))

def seg_to_feat(file_sigma):
    """returns segments as keys and two featureal representations (string and list of strings) as values
        output: dict, e.g. {'a': ['---++-', ['-', '-', '-', '+', '+', '-']], ...}

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `seg_to_feat`.
        """

    dict_out = dict()
    for k,v in seg_dict(file_sigma).items():
        features = v.values()
        if k == '>':
            dict_out[k] = ['', feat_temp(file_sigma)]
        elif k == '<':
            dict_out[k] = ['', feat_temp(file_sigma)]
        else:
            dict_out[k] = [''.join(features), list(features)]

    return dict_out

def seg_to_feat_delta(file_delta):
    """returns segments as keys and two featureal representations (string and list of strings) as values
        output: dict, e.g. {'a': ['---++-', ['-', '-', '-', '+', '+', '-']], ...}

        Args:
            file_delta: Output feature-inventory path.

        Returns:
            The output produced by `seg_to_feat_delta`.
        """

    dict_out = dict()
    for k,v in seg_dict_delta(file_delta).items():
        features = v.values()
        if k == '>':
            dict_out[k] = ['', feat_temp_delta(file_delta)]
        elif k == '<':
            dict_out[k] = ['', feat_temp_delta(file_delta)]
        else:
            dict_out[k] = [''.join(features), list(features)]

    return dict_out

def feat_to_seg(string, file_sigma):
    """stringifies the featural representations of data, e.g.
        output: 'aa'
        input: ['-0', '-0', '-0', '+0', '-0', '--', '-0', '-+', '++', '+-', '00', '0-', '++', '++', '0+', '0-', '0-', '00', '00', '00', '0-', '0-'] --> 'aa'

        Args:
            string: Source string or prefix being transformed.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `feat_to_seg`.
        """

    #print(self.seg_to_feat().items())
    max_len = len(string[0])

    output = ''
    for i in range(max_len):
        #print(i)
        segment = ''
        for feat in string:
            segment += feat[i]
            #print(segment)
        for k,v in seg_to_feat(file_sigma).items():

            if v[0] == segment:
                #print(v[0], k)
                output += k
    return output

def featstring_to_seg(featstring, file_sigma):

    """input: "+---0-++"
        output: "a"

        Args:
            featstring: Feature bundle string to decode.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `featstring_to_seg`.
        """

    output = []
    for i in featstring:
        # print(f"----------------------------------featstring:      {i}")
        for j in seg_to_feat(file_sigma):
            # print(f"letter in dict is:      {j}")
            # print(f"{self.seg_to_feat()[j]} is NOT equal to {i}")
            if seg_to_feat(file_sigma)[j][0] == i:
                output.append(j)
    return tuple(output)





def sigma(file_sigma):
    """returns alphabet consisting of feature bundles representing segment for the full machine
        output: list of lists of strings of features, e.g. [['---+'],['+--+'], ...]

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `sigma`.
        """

    sigma = []
    for key, val in seg_to_feat(file_sigma).items():
        #print(val)
        if key == '>' or key == '<':
            sigma.append([key])
        else:
            sigma.append([val[0]])
    # sigma.append(['<<'])
    return sigma

def sigma_seg(file_sigma):
    """outputs input alphabet represents with segments, e.g. [m, o, ...]

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `sigma_seg`.
        """

    # return [[k] for k, v in seg_to_feat(file_sigma).items()] + [['<<']]
    return [[k] for k, v in seg_to_feat(file_sigma).items()]

def delta_seg(file_delta):
    """outputs output alphabet represents with segments, e.g. [m, o, ...]

        Args:
            file_delta: Output feature-inventory path.

        Returns:
            The output produced by `delta_seg`.
        """

    return [[k] for k, v in seg_to_feat_delta(file_delta).items()]

def delta(file_delta):
    """returns output alphabet (sigma without boundary symbols)
        output: list of lists of strings, e.g. [['---+'], ['+--+'], ...]

        Args:
            file_delta: Output feature-inventory path.

        Returns:
            The output produced by `delta`.
        """

    return [[val[0]] for key, val in seg_to_feat(file_delta).items()]

def sigma_feat(features, file_sigma):
    """outputs an alphabet for single feature or multiple features
        input: str, e.g. 'len' or a list, e.g. ['len', 'nasal']
        output: list of lists of strings of features,
                e.g. [['+-'], ['0+'], ['0-'], ['++'], ['-+'], ['--'], ['>'], ['<'], ['<<']]

        Args:
            features: Ordered selected feature names.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `sigma_feat`.
        """

    # if type(features) == str:
    #     feat_set = self.feature_values()[features]
    #     output = [[i] for i in feat_set]
    #     output.append(['>'])
    #     output.append(['<'])
    #     output.append(['<<'])
    #     return output

    temp_l = []
    feat_list = feature_list_sigma(file_sigma)
    # print('feat_list:', feat_list)

    for feature in features:
        # print(feature)
        for i in feat_list:
            # print('i:      ', i)
            if feature in i:
                temp_l.append(i[1:-2])
    # print(temp_l)
    prod_set = set(["".join(items) for items in zip(*temp_l)])
    output = [[i] for i in prod_set]
    output.append(['>'])
    output.append(['<'])
    # output.append(['<<'])
    return output

def delta_feat(features, file_delta):
    """Project the output alphabet onto selected features.

        Args:
            features: Ordered selected feature names.
            file_delta: Output feature-inventory path.

        Returns:
            The output produced by `delta_feat`.
        """


    temp_l = []
    feat_list = feature_list_delta(file_delta)
    for feature in features:
        for i in feat_list:
            if feature in i:
                temp_l.append(i[1:])
    prod_set = set(["".join(items) for items in zip(*temp_l)])
    output = [[i] for i in prod_set]
    return output



def check_if_distinct(file_sigma):
    """checks if every segment has a uniqe feature specification
        output: bool True or the repeated segments and their feature values

        Args:
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `check_if_distinct`.
        """

    alpha = sigma(file_sigma)
    bundles = [a[0] for a in alpha]
    check = []
    if len(bundles) == len(set(bundles)):
        return True
    else:
        for b in bundles:
            if b not in check:
                check.append(b)
            else:
                for k,v in seg_to_feat(file_sigma).items():
                    if b == v[0]:
                        print("Repeated segment:", k, v)


def concat_feat(lists):
    """merges all features together

        Args:
            lists: Sequences to concatenate position by position.

        Returns:
            The output produced by `concat_feat`.
        """

    return ["".join(items) for items in zip(*lists)]




def ngrams(n, sigma):
    """creates all logically plausible ngrams up until n-size
        input: int
        output: ngrams with boundary symbols

        Args:
            n: Requested string length or recursion count.
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `ngrams`.
        """

    ngrams = []
    #n = self.k + 1
    # sigma = self.sigma()
    temp_sigma = []
    for i in sigma:
        if i != ['>'] and i != ['<'] and i != ['<<']:
            i = list(product([i[0]], repeat=1))[0]
            temp_sigma.append(i)

    begin = list(product(['<'], repeat=1))[0]
    end = list(product(['>'], repeat=1))[0]

    while n > 0:
        grams = list(itertools.product(temp_sigma, repeat=n))
        for gram in grams:
            temp_l = []
            temp_l.append(begin)
            for i in gram:
                temp_l.append(i)
            temp_l.append(end)
            ngrams.append(temp_l)
        n -= 1
    return ngrams


def stringify(gen_pairs, file_sigma):
    """stringifies the featural representations of data
        output: list, e.g.
        [([('<',), ('---++-',), ('---++-',), ('---++-',), ('>',)],
        ['---', '---', '---', '+++', '+++', '---']), ...)} ---> [['aaa', 'aaa'], ...]

        Args:
            gen_pairs: Input-output examples.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `stringify`.
        """

    #print(self.seg_to_feat().items())
    words_seg = []
    for word in gen_pairs:
        #print(word)
        word_in = word[0][1:-1]
        word_out = word[1]
        temp_in = ''
        temp_out = ''
        for letter_in in word_in:
            for k,v in seg_to_feat(file_sigma).items():
                if letter_in[0] in v[0]:
                    temp_in += k

        for i in range(len(word_out[0])):
            new_out = ''.join([string[i] for string in word_out])
            for k_out,v_out in seg_to_feat(file_sigma).items():
                if new_out in v_out[0]:
                    temp_out += k_out
        words_seg.append([temp_in, temp_out])
    return words_seg


def states_gen(sigma, k):
    """generates states according to k-size
        input: feature bundles, or individual/selected features
        output: list of tuples, e.g. [('-+0-', '-+0-'), ('---+',), ...]
                or for just 2 features: ('++', '++'), ('-+',), ('--',),

        Args:
            sigma: Input alphabet or feature bundles.
            k: Locality or memory bound.

        Returns:
            The output produced by `states_gen`.
        """

    alphabet = sigma
    # print(f'alphabet: {alphabet}')
    alphabet_new = [i[0] for i in alphabet]
    alphabet_new.remove('>')
    alphabet_new.remove('<')
    # alphabet_new.remove('<<')
    # k = self.k
    states = []
    while k > 2:
        seg_product = list(product(alphabet_new, repeat=k-1)) #letters in tuples separately
        # print(f'inside of states_gen function for k ={k}')
        # print(seg_product)
        k -= 1
        states += seg_product
        #print(states, "when k >2")
    else:
        if k == 2:
            states += alphabet
            #print(states, "when k==2")
        elif k == 1:
            states = ['>'] + ['X']

    output = [tuple(i) for i in states]
    return output + [('<<',)]

def correct_transitions(transitions, file_sigma):
    """Normalize transition outputs into feature-list form.

        Args:
            transitions: Transition records to inspect or transform.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `correct_transitions`.
        """

    # transitions = self.transitions_gen(sigma)
    # pprint(transitions)
    temp_f = feat_temp(file_sigma)
    trans_corrected = []
    for trans in transitions:
        #if trans[0][0] == '<<':
        #    trans_corrected.append(trans)
        #else:
        state_in = trans[0]
        read = trans[1]
        output = trans[2]
        state_out = trans[3]
        new_output = []
        if output[0] != '>':

            for i in output:
                for j in i:
                    new_output.append(j)
                new_trans = [state_in, read, new_output, state_out]
                trans_corrected.append(new_trans)
        else:

            new_output = temp_f
            new_trans = [state_in, read, new_output, state_out]
            trans_corrected.append(new_trans)
    # print(transitions == trans_corrected)
    return trans_corrected



def transitions_gen(sigma, k, file_sigma):
    """generates identity transitions
        input: alphabet
        output: list of lists, e.g. [[('-+', '-+'), ('++',), ('++',), ('-+', '++')],
                                    [('-+', '-+'), ('>',), ('>',), ('>',)], ...]

        Args:
            sigma: Input alphabet or feature bundles.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `transitions_gen`.
        """



    states = states_gen(sigma, k)
    alphabet = [tuple(i) for i in sigma]

    list_of_trans = []


    for state in states:
        if state[0] == '<<':
            tr  = [state, list(product('<', repeat=1))[0], list(product('<', repeat=1))[0], list(product('<', repeat=1))[0]]
            list_of_trans.append(tr)
        elif state[-1] != '>':
            #print(state)
            for a in alphabet:
                if a[0] == '<<':
                    continue
                elif a[0] != '<':
                    if k ==1 :
                        if state[0] == '<':
                            if a[0] == '>':
                                tr  = [state, a, a, list(product(a, repeat=1))[0]]
                                list_of_trans.append(tr)
                            else:
                                tr  = [state, a, a, list(product('X', repeat=1))[0]]
                                list_of_trans.append(tr)
                        elif state[0] == 'X':
                            if a[0] == '>':
                                tr  = [state, a, a, list(product(a, repeat=1))[0]]
                                list_of_trans.append(tr)
                            else:
                                out = state
                                tr  = [state, a, a, out]
                                list_of_trans.append(tr)
                        elif state[0] == '>':
                            continue
                    if k == 2:
                        if a[0] != '>':
                            out = a
                            tr  = [state, a, a, out]
                            list_of_trans.append(tr)
                        else:
                            out = a
                            tr  = [state, a, a, out]
                            list_of_trans.append(tr)
                    elif k >= 3:
                        if state[0] == '<':
                            if a[0] != '>':
                                out = a
                                tr  = [state, a, a, out]
                                list_of_trans.append(tr)
                            else:
                                out = list(product('>', repeat=1))[0]
                                tr  = [state, a, out, out]
                                list_of_trans.append(tr)
                        else:
                            rep = k-2
                            if len(state) > rep:
                                out = state[-rep:] + a
                                if a != '>':
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, a, out]
                                    list_of_trans.append(tr)
                                else:
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, out, out]
                                    list_of_trans.append(tr)
                            else:
                                out = state + a
                                if a != '>':
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, a, out]
                                    list_of_trans.append(tr)
                                else:
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, out, out]
                                    list_of_trans.append(tr)

    transitions = []
    for trans in list_of_trans:
        if trans not in transitions:
            if trans[0] == ('<<',):
                if trans[1] == ('<',):
                    transitions.append(trans)
                else:
                    continue
            if trans[1] == ('<',) or trans[1] == ('<<',):
                continue
            else:
                transitions.append(trans)

    return correct_transitions(transitions, file_sigma)


def remove_repetitions(lst):

    """removes repetitions for a list of list (for selected features transitions extraction)
        input: list of lists
        output: list of lists

        Args:
            lst: Sequence or collection being transformed.

        Returns:
            The output produced by `remove_repetitions`.
        """

    result = []
    for sublist in lst:
        if sublist not in result:
            result.append(sublist)

    return result


def extract_feats_trans(full_trans, features, file_sigma, k):


    """given the full-feature transitions, it returns transitions for particular feature(s)
        input: full transitions and a list of feature(s)
        output: a list of lists of transitions for selected features

        Args:
            full_trans: Complete transition set used as evaluation target.
            features: Ordered selected feature names.
            file_sigma: Input feature-inventory path.
            k: Locality or memory bound.

        Returns:
            The output produced by `extract_feats_trans`.
        """
    # print(f'Inside of extract_feats_trans key \t\t\t\t\t\t\t K={k}')

    features_ids = feature_id(file_sigma)
    result = []
    new_transitions = []
    if len(features) == 1:
        feat_id = 0
        for key,v in features_ids.items():
            if features[0] == v:
                feat_id = key
                # print(feat_id)
        for trans in full_trans:
            # print("TRANSITION IS:           ", trans)
            state_from = trans[0]
            reading = trans[1]
            writing = trans[2]
            state_to = trans[3]
            if len(state_from) == 1:
                if (state_from[0] == '<<') or (state_from[0] == '<' and reading[0] == '>'):
                    new_trans = [state_from, reading, len(features) * [""], state_to]
                    new_transitions.append(new_trans)
                elif (state_from[0] == '<' or state_from[0] == 'X'):
                    if (state_to[0] == 'X' or state_to[0] == '>'):
                        if reading[0] == '>':
                            new_trans = [state_from, reading, [writing[feat_id]], state_to]
                            new_transitions.append(new_trans)
                        else:
                            new_trans = [state_from, list(product([reading[0][feat_id]], repeat=1))[0], [writing[feat_id]], state_to]
                            new_transitions.append(new_trans)

                    else:
                        new_trans = [state_from, list(product([reading[0][feat_id]], repeat=1))[0], [writing[feat_id]], list(product([state_to[0][feat_id]], repeat=1))[0]]
                        new_transitions.append(new_trans)
                else:
                    if (reading[0] == '>' or reading[0] == 'X'):
                        new_trans = [list(product([state_from[0][feat_id]], repeat=1))[0], reading, [writing[feat_id]], state_to]#list(product([state_to[0][feat_id]], repeat=1))[0]]
                        new_transitions.append(new_trans)
                    else:
                        new_state_to = []
                        for s in state_to:
                            #print('                     state:  ',s)
                            new_s = s[feat_id]
                            new_state_to.append(new_s)

                        new_trans = [list(product([state_from[0][feat_id]], repeat=1))[0], list(product([reading[0][feat_id]], repeat=1))[0], [writing[feat_id]], tuple(new_state_to)]
                        new_transitions.append(new_trans)
            else: # if len(state_from) > 1
                new_state_from = []
                new_state_to = []
                for state in state_from:
                    temp = state[feat_id]
                    new_state_from.append(temp)
                if reading[0] == '>':
                    new_trans = [tuple(new_state_from), reading, [writing[feat_id]], state_to]
                    new_transitions.append(new_trans)
                else:
                    for state in state_to:
                        temp = state[feat_id]
                        new_state_to.append(temp)
                    new_trans = [tuple(new_state_from), list(product([reading[0][feat_id]], repeat=1))[0], [writing[feat_id]], tuple(new_state_to)]
                    new_transitions.append(new_trans)
        #print("transitions before merge", len(new_transitions))
        new_transitions = merge_states(remove_repetitions(new_transitions))
        #print("transitions after merge", len(new_transitions))
        for i in new_transitions:
            if len(i[2]) == 1:
                trans = [i[0], i[1], i[2][0], i[3]]
                result.append(trans)
            else:
                result.append(i)

    else: # if more than 1 feature
        feat_id = []

        for feature in features:
            for key,v in features_ids.items():
                if feature == v:
                    feat_id.append(key)

        for trans in full_trans:
            # print("TRANSITION IS:           ", trans)
            state_from = trans[0]
            reading = trans[1]
            writing = trans[2]
            state_to = trans[3]
            if len(state_from) == 1:
                if (state_from[0] == '<<') or (state_from[0] == '<' and reading[0] == '>'):
                    # print("IF condition \n")
                    new_trans = [state_from, reading, len(features) * [''], state_to]
                    #print('                     and the new one is: ', new_trans)
                    new_transitions.append(new_trans)
                elif state_from[0] == '<' or state_from[0] == 'X':

                    if state_to[0] == 'X' or state_to[0] == '>':
                        temp_read = ''
                        temp_write = []
                        temp_state_to = ''
                        for f_id in feat_id:
                            if reading[0] == '>':
                                temp_state_from = ''
                                temp_write = []
                                for f_id in feat_id:
                                    #temp_state_from += state_from[0][f_id]
                                    temp_write.append(writing[f_id])
                                new_trans = [state_from, reading, temp_write, state_to]#list(product([state_to[0][feat_id]], repeat=1))[0]]
                                # print('      1               and the new one is: ', new_trans)
                                new_transitions.append(new_trans)
                            else:
                                temp_read += reading[0][f_id]
                                temp_write.append(writing[f_id])
                                #temp_state_to += state_to[0][f_id]
                                new_trans = [state_from, list(product([temp_read], repeat=1))[0], temp_write, state_to]
                                # print('         2            and the new one is: ', new_trans)
                        new_transitions.append(new_trans)
                    else:
                        temp_read = ''
                        temp_write = []
                        temp_state_to = ''
                        for f_id in feat_id:
                            temp_read += reading[0][f_id]
                            temp_write.append(writing[f_id])
                            temp_state_to += state_to[0][f_id]
                        new_trans = [state_from, list(product([temp_read], repeat=1))[0], temp_write, list(product([temp_state_to], repeat=1))[0]]
                        # print('         3            and the new one is: ', new_trans)
                        new_transitions.append(new_trans)
                else:
                    # print('ELSE condition \n')
                    # print(f'State: {state_from}')
                    if reading[0] == '>':
                        temp_state_from = ''
                        temp_write = []
                        for f_id in feat_id:
                            temp_state_from += state_from[0][f_id]
                            temp_write.append(writing[f_id])
                        # print(f'Temp state from: {temp_state_from}')
                        new_trans = [list(product([temp_state_from], repeat=1))[0], reading, temp_write, state_to]#list(product([state_to[0][feat_id]], repeat=1))[0]]
                        # print('                     and the new one is: ', new_trans)
                        new_transitions.append(new_trans)
                    else:
                        # print('\n\n WTF is this transition \n\n')
                        # print(trans)
                        temp_state_from = ''
                        temp_read = ''
                        temp_write = []
                        # temp_state_to = ''

                        for f_id in feat_id:
                            temp_state_from += state_from[0][f_id]
                            temp_read += reading[0][f_id]
                            temp_write.append(writing[f_id])
                        #     temp_state_to += state_to[0][f_id]
                        # new_trans = [list(product([temp_state_from], repeat=1))[0], list(product([temp_read], repeat=1))[0], temp_write, list(product([temp_state_to], repeat=1))[0]]
                        #print('                     and the new one is: ', new_trans)
                        # new_transitions.append(new_trans)
                        new_state_to = []
                        # for f_id in feat_id:
                        #     new_writing.append(writing[f_id])
                        #     new_reading += reading[0][f_id]
                        for state in state_to:
                            #print("this is state to: ", state)
                            temp_full_state_to = ''
                            for f_id in feat_id:
                                #new_reading += reading[0][f_id]
                                temp_state_to = state[f_id]
                                temp_full_state_to += temp_state_to
                            new_state_to.append(temp_full_state_to)
                        # new_reading = list(product([new_reading], repeat=1))[0]
                        new_trans = [list(product([temp_state_from], repeat=1))[0], list(product([temp_read], repeat=1))[0], temp_write, tuple(new_state_to)]
                        # print('                     and the new one is: ', new_trans)
                        new_transitions.append(new_trans)
            else: # mor than one state more than one feature
                # [[('---', '--0'), ('-+0',), ['--', '+', '0'], ('--0', '-+0')]
                new_state_from = []
                new_state_to = []
                new_reading = ''
                new_writing = []


                for state in state_from:
                    temp_full_state = ''
                    for f_id in feat_id:
                        # print(f_id)
                        temp_state = state[f_id]
                        temp_full_state += temp_state
                    new_state_from.append(temp_full_state)

                if reading[0] == '>':
                    for f_id in feat_id:
                        new_writing.append(writing[f_id])
                    new_trans = [tuple(new_state_from), reading, new_writing, state_to]
                    # print('                     and the new one is: ', new_trans)
                    new_transitions.append(new_trans)
                else:
                    for f_id in feat_id:
                        new_writing.append(writing[f_id])
                        new_reading += reading[0][f_id]
                    for state in state_to:
                        #print("this is state to: ", state)
                        temp_full_state_to = ''
                        for f_id in feat_id:
                            #new_reading += reading[0][f_id]
                            temp_state_to = state[f_id]
                            temp_full_state_to += temp_state_to
                        new_state_to.append(temp_full_state_to)
                    new_reading = list(product([new_reading], repeat=1))[0]
                    new_trans = [tuple(new_state_from), new_reading, new_writing, tuple(new_state_to)]
                    # print('                     and the new one is: ', new_trans)
                    new_transitions.append(new_trans)
        new_transitions = merge_states(remove_repetitions(new_transitions))
        for i in new_transitions:
            if len(i[2]) == 1:
                trans = [i[0], i[1], i[2][0], i[3]]
                result.append(trans)
            else:
                result.append(i)
    # return remove_repetitions(result)
    return k_transitions(remove_repetitions(result), k, features)


def merge_states(transitions):

    """given the same _state_from and _reading_input, it merges the states;
        if different inputs given the same _state_from and _reading_input, the outputs will be appended to a list of list
        to differentaite between the good outputs with various features

        input: list of lists of extracted transitions (with repetitions)
        output: list of lists of transitions WITHOUT repetitions, e.g. [[('++',), ('-+',), ['-+'], ('-+',)],
                                                                         [('--',), ('--',), ['--'], ('--',)], ...]

        Args:
            transitions: Transition records to inspect or transform.

        Returns:
            The output produced by `merge_states`.
        """

    from_read = set()
    result = []
    for transition in transitions:
        tup = (transition[0], transition[1])
        if tup not in from_read:
            from_read.add(tup)
    for pair in from_read:
        outputs = []
        for transition in transitions:
            if pair[0] == transition[0] and pair[1] == transition[1]:
                outputs.append(transition[2])
                new_trans = [transition[0], transition[1], outputs, transition[3]]
        result.append(new_trans)
    return result


def identify_k(transitions):

    """identifys k value given transitions
        input: list of lists
        oupputL k=int

        Args:
            transitions: Transition records to inspect or transform.

        Returns:
            The output produced by `identify_k`.
        """

    return max(len(tran[0]) for tran in transitions) + 1

def is_list_of_lists(x):
    """Test whether a value is a list whose members are lists.

        Args:
            x: Value being converted or inspected.

        Returns:
            The output produced by `is_list_of_lists`.
        """
    return isinstance(x, list) and all(isinstance(i, list) for i in x)


def k_transitions(transitions, k, features):

    """takes transitions and compresses them to particular k value
        input: transitions with fixed k
        output: transitions for particular k

        Args:
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            features: Ordered selected feature names.

        Returns:
            The output produced by `k_transitions`.
        """

    new_result = []
    state_len = k-1
    feats_len = len(features)

    # print(f'\n\n\n k={k}')
    if identify_k(transitions) == k:
        # print('\n\n\n\n we got it \n\n\n')
        return transitions

    if k == 1:

        # new_result = []

        for trans in transitions:
            trans = list(trans)  # Ensure it's mutable
            if trans[0] == ('<<',):
                # print('In state ("<<",)')
                # print(f'trans before: {trans}')
                trans[3] = ('X',)
                # print(f'trans after: {trans}')
                new_result.append(trans)
                # print(f'------------Appended: {trans} \n')

            elif trans[1] == ('>',):
                # print('Going to final state:  (">",)')
                # print(f'trans before: {trans}')
                trans[0] = ('X',)
                trans[3] = ('>',)
                # print(f'trans after: {trans}')
                matched = False
                for tr in new_result:
                    if trans[:2] == tr[:2]:
                        # print(f'In the same state and reading the same symbol: {trans}')
                        if trans[2] == tr[2]:
                            # continue
                            # print(f'Ident trans is already here: {trans}')
                            matched = True
                            break
                        elif all(type(output) == list for output in trans[2]):
                            # print(f'All outputs are lists for : {trans}')
                            for i in trans[2]:
                                if i not in tr[2]:
                                    tr[2].append(i)
                        else:
                            if trans[2] not in tr[2]:
                                tr[2].append(trans[2])  # append, not extend
                                # print(f'------$$$---Appended {trans[2]} to {tr[2]} \n')
                        matched = True
                        break
                if not matched:
                    # print('Transition not matched')
                    if len(trans[2]) == feats_len and all(type(item) == str for item in trans[2]):
                        # print(f'\n\n\n thats the one \n\n\n')
                        # print(trans)
                        trans[2] = [trans[2]]  # wrap in a list to keep nesting consistent

                    # print(f'new transition: {trans}')
                    new_result.append(trans)
                    # print(f'------------Appended: {trans} \n')

            else:
                # print('CALL IN: Else condition')
                # print(f'trans before: {trans}')
                trans[0] = ('X',)
                trans[3] = ('X',)
                # print(f'trans after: {trans}')
                matched = False
                for tr in new_result:
                    if trans[:2] == tr[:2]:
                        # print(f'In the same state and reading the same symbol: {trans}')
                        if trans[2] == tr[2]:
                            # continue
                            # print(f'trans[2]={trans[2]}')
                            # print(f'tr[2]={tr[2]}')
                            # print(f'Ident trans is already here: {trans}')
                            matched = True
                            break
                        elif all(type(output) == list for output in trans[2]):
                            # print(f'All outputs are lists for : {trans}')

                            for i in trans[2]:
                                # print("555555555555555555555: ", i)
                                if i not in tr[2]:
                                    tr[2].append(i)
                        else:
                            if trans[2] not in tr[2]:
                                tr[2].append(trans[2])  # append, not extend
                        # print(f'------$$$---Appended {trans[2]} to {tr[2]} \n')
                        matched = True
                        break
                        # else:
                        #     if trans[2] not in tr[2]:
                        #         tr[2].append(trans[2])  # append, not extend
                        #         print(f'------$$$---Appended {trans[2]} to {tr[2]} \n')
                        #         matched = True
                        #         break
                if not matched:
                    # print('Transition not matched')
                    if len(trans[2]) == feats_len and all(type(item) == str for item in trans[2]):
                        trans[2] = [trans[2]]  # wrap in a list to keep nesting consistent

                    # print(f'new transition: {trans}')
                    new_result.append(trans)
                    # print(f'------------Appended: {trans} \n')

    else:
        # new_result = []
        for trans in transitions:
            if trans[0] == ('<<',):
                # print('In state ("<<",)')
                # print(f'trans before: {trans}')
                new_result.append(trans)
                # print(f'trans after: {trans}')
                # print(f'------------Appended: {trans} \n')
            elif trans[0] == ('<',):
                # print('In state ("<",)')
                # print(f'trans before: {trans}')
                new_result.append(trans)
                # print(f'trans after: {trans}')
                # print(f'------------Appended: {trans} \n')
            elif trans[1] == ('>',):
                # print('********************************')
                # print(f'In trans to final state (">",): {trans} \n\n')

                if len(trans[0]) > 1:
                    # print('Len of current state > 1')
                    # print(f'trans before: {trans}')
                    trans[0] = trans[0][state_len:]
                    # print(f'trans after: {trans}')
                matched = False
                for tr in new_result:
                    if trans[:2] == tr[:2]:
                        # print(f'In the same state and reading the same symbol: {trans}')
                        if trans[2] == tr[2]:
                            # continue
                            # print(f'Ident trans is already here: {trans}')
                            matched = True
                            break
                        elif all(type(output) == list for output in trans[2]):
                            # print(f'All outputs are lists for : {trans}')
                            for i in trans[2]:
                                tr[2].append(i)
                        else:
                            if trans[2] not in tr[2]:
                                tr[2].append(trans[2])  # append, not extend
                        # tr[2].append(trans[2])  # append, not extend
                        # print(f'------$$$---Appended {trans[2]} to {tr[2]} \n')
                        matched = True
                        break
                if not matched:
                    # print('Transition not matched')
                    # if len(trans[2]) == 1:
                    if len(trans[2]) == feats_len and all(type(item) == str for item in trans[2]):
                        trans[2] = [trans[2]]  # wrap in a list to keep nesting consistent

                    # print(f'new transition: {trans}')
                    new_result.append(trans)
                    # print(f'------------Appended: {trans} \n')
            else:
                # print(f'Not in ("<",) and not going to final')

                # print(f'trans before: {trans}')
                if len(trans[0]) > 1:
                    # print('Let of current state > 1')
                    # print(f'trans before: {trans}')
                    trans[0] = trans[0][state_len:]
                trans[3] = trans[3][state_len:]
                # print(f'trans after: {trans}')
                matched = False
                for tr in new_result:
                    if trans[:2] == tr[:2]:
                        # print(f'In the same state and reading the same symbol: {trans}')
                        if trans[2] == tr[2]:
                            # continue
                            # print(f'Ident trans is already here: {trans}')
                            matched = True
                            break
                        elif all(type(output) == list for output in trans[2]):
                            # print(f'All outputs are lists for : {trans}')
                            for i in trans[2]:
                                tr[2].append(i)
                        else:
                            if trans[2] not in tr[2]:
                                tr[2].append(trans[2])  # append, not extend
                        # tr[2].append(trans[2])  # append, not extend
                        # print(f'------$$$---Appended {trans[2]} to {tr[2]} \n')
                        matched = True
                        break
                if not matched:
                    # print('Transition not matched')
                    # if len(trans[2]) == 1:
                    if len(trans[2]) == feats_len and all(type(item) == str for item in trans[2]):
                        trans[2] = [trans[2]]  # wrap in a list to keep nesting consistent

                    # print(f'new transition: {trans}')
                    new_result.append(trans)
                    # print(f'------------Appended: {trans} \n')


    for result in new_result:
        if len(result[2]) == 1 and type(result[2][0]) == list:
            # print('Get reid of this list')
            # print(result)
            result[2] = result[2][0]


    return remove_repetitions(new_result)
