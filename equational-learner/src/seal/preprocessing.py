"""Feature inventories and identity-transition helpers for FxF and SEAL."""

from __future__ import annotations
import csv
from itertools import product
from os import PathLike
from typing import Any, Dict, List, Sequence, Tuple, Union

FilePath = Union[str, PathLike[str]]

def feature_list_sigma(file_sigma: FilePath) -> List[List[str]]:
    """Read an input inventory from a tab-separated file.
        
        Return rows of strings; the first row names segments and later rows give
        their feature values.
    
        Args:
            file_sigma: Input feature-inventory path.
    
        Returns:
            The list[list[string]] returned by `feature_list_sigma`.
        """
    
    list_segs = []
    with open(file_sigma, newline='') as csvfile:
        segments = csv.reader(csvfile, delimiter='\t')
        for row in segments:
            list_segs.append(row)
    return list_segs


def features(file_sigma: FilePath) -> List[str]:
    """Return the input inventory's feature names in row order.
    
        Args:
            file_sigma: Input feature-inventory path.
    
        Returns:
            The list[string] returned by `features`.
        """
    
    output = [lst[0] for lst in feature_list_sigma(file_sigma)[1:]]
    return output


def seg_dict(file_sigma: FilePath) -> Dict[str, Dict[str, str]]:
    """Map each input segment to its feature names and string values.
    
        Args:
            file_sigma: Input feature-inventory path.
    
        Returns:
            The dictionary[string, dictionary[string, string]] returned by `seg_dict`.
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


def feat_temp(file_sigma: FilePath) -> List[str]:
    """creates an empty template for each feature
        output: list of empty strings, e.g. ['', '', ...]
    
        Args:
            file_sigma: Input feature-inventory path.
    
        Returns:
            The list[string] returned by `feat_temp`.
        """
    
    return [""] * len(features(file_sigma))


def seg_to_feat(file_sigma: FilePath) -> Dict[str, List[Any]]:
    """Map input segments to [joined feature string, feature value list].
    
        Args:
            file_sigma: Input feature-inventory path.
    
        Returns:
            The dictionary[string, list[structured value]] returned by `seg_to_feat`.
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


def sigma(file_sigma: FilePath) -> List[List[str]]:
    """returns alphabet consisting of feature bundles representing segment for the full machine
        output: list of lists of strings of features, e.g. [['---+'],['+--+'], ...]
    
        Args:
            file_sigma: Input feature-inventory path.
    
        Returns:
            The list[list[string]] returned by `sigma`.
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


def concat_feat(lists: Sequence[Sequence[str]]) -> List[str]:
    """merges all features together
    
        Args:
            lists: Sequences to concatenate position by position.
    
        Returns:
            The list[string] returned by `concat_feat`.
        """
    
    return ["".join(items) for items in zip(*lists)]


def states_gen(sigma: Sequence[Sequence[str]], k: int) -> List[Tuple[str, ...]]:
    """generates states according to k-size
        input: feature bundles, or individual/selected features
        output: list of tuples, e.g. [('-+0-', '-+0-'), ('---+',), ...] 
                or for just 2 features: ('++', '++'), ('-+',), ('--',),
    
        Args:
            sigma: Input alphabet or feature bundles.
            k: Locality or memory bound.
    
        Returns:
            The list[tuple[string, ...]] returned by `states_gen`.
        """
    
    alphabet = sigma
    # print(f'alphabet: {alphabet}')
    alphabet_new = [i[0] for i in alphabet]
    # print(f'alphabet_new: {alphabet_new}')
    # if '<' or '>' in alphabet_new:
    #     print("we got '<')")
    alphabet_new.remove('>')
    if k > 1:
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


def gen_k_trans_ident(sigma: Sequence[Sequence[str]], k: int) -> List[List[Any]]:
    """generates identity transitions
        input: alphabet
        output: list of lists, e.g. [[('-+', '-+'), ('++',), ('++',), ('-+', '++')],
                                    [('-+', '-+'), ('>',), ('>',), ('>',)], ...]
    
        Args:
            sigma: Input alphabet or feature bundles.
            k: Locality or memory bound.
    
        Returns:
            The list[list[structured value]] returned by `gen_k_trans_ident`.
        """

    

    # print('sigma: ', sigma)
    # if k > 1:
    #     sigma.remove(('<<',))


    # print('sigma after remove: ', sigma)
    states = states_gen(sigma, k)
    states.remove(('<<',))
    # print('states:  ', states)
    alphabet = [tuple(i) for i in sigma]

    list_of_trans = []
    if k == 1:
        list_of_trans.append([('<<',), list(product('<', repeat=1))[0], [''], list(product('X', repeat=1))[0]])
    else:
        list_of_trans.append([('<<',), list(product('<', repeat=1))[0], [''], list(product('<', repeat=1))[0]])
    
    for state in states:
        if state[-1] != '>':
            #print(state)
            for a in alphabet:
                if a[0] != '<':
                    if k ==1 :
                        if state[0] == '<':
                            if a[0] == '>':
                                tr  = [state, a, [''], list(product(a, repeat=1))[0]]
                                list_of_trans.append(tr)
                            else:
                                tr  = [state, a, [a[0][0]], list(product('X', repeat=1))[0]]
                                list_of_trans.append(tr)
                        elif state[0] == 'X':
                            if a[0] == '>':
                                tr  = [state, a, [''], list(product(a, repeat=1))[0]]
                                list_of_trans.append(tr)
                            else:
                                out = state
                                tr  = [state, a, [a[0][0]], out]
                                list_of_trans.append(tr)
                        elif state[0] == '>':
                            continue
                    if k == 2:
                        if a[0] != '>':
                            out = a
                            tr  = [state, a, [a[0][0]], out]
                            list_of_trans.append(tr)
                        else:
                            out = a
                            tr  = [state, a, [''], out]
                            list_of_trans.append(tr)
                    elif k >= 3:
                        if state[0] == '<':
                            if a[0] != '>':
                                out = a
                                tr  = [state, a, [a[0][0]], out]
                                list_of_trans.append(tr)
                            else:
                                out = list(product('>', repeat=1))[0]
                                tr  = [state, a, [''], out]
                                list_of_trans.append(tr)
                        else:
                            rep = k-2
                            if len(state) > rep:
                                out = state[-rep:] + a
                                if a[0] != '>':
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, [a[0][0]], out]
                                    list_of_trans.append(tr)
                                else:
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, [''], out]
                                    list_of_trans.append(tr)
                            else:
                                out = state + a
                                if a[0] != '>':
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, [a[0][0]], out]
                                    list_of_trans.append(tr)
                                else:
                                    if out[-1] == '>':
                                        out = list(product('>', repeat=1))[0]
                                    tr  = [state, a, [''], out]
                                    list_of_trans.append(tr)



    return list_of_trans
