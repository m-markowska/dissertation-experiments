import csv
from itertools import product
import itertools
import random
from . import preprocessing as pre_process
import copy
from pprint import pprint


def nasalize(sigma, transitions, k, file_sigma):
    """nasalizes a vowel followed by a nasal consonant

        k=2, right context

        input: list of lists of features
        output: nasalized transitions, list of lists of transitions,
                e.g. [[('---+', '---+'), ('---+',), ['-', '-', '-', '+'], ('---+', '---+')], ...]

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `nasalize`.
        """


    # get identity transitions
    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    #print("Those are originial transitions: ", transitions[0]) #[('---+', '---+'), ('---+',), ('---+',), ('---+', '---+')]
    # get features ids
    features_ids = pre_process.feature_id(file_sigma)
    id_cons = 0
    id_nasal = 0
    for i, f in features_ids.items():
        if f == 'nasal':
            id_nasal = i
        if f == 'cons':
            id_cons = i

    # change outputs s.t. every feature is treated as a separate string
    # pprint(trans_corrected)

    if k <= 1:
        return 'k-value must be bigger than 1'

    result = []
    for transition in transitions:
        if transition[0][0] == '<<':
            t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
            result.append(t)
        elif transition[0][0] == '<': # if <
            if transition[1][0] == '>': #if <>
                t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
                result.append(t)
            elif transition[1][0][id_nasal] == '-' and transition[1][0][id_cons] == '-': #if < non-nasalV
                t_copy = transition.copy()
                if t_copy:
                    t_copy[2][id_nasal] = ''
                    #t_copy[2][id_cons] = ''
                result.append(t_copy)

            else:
                t = [transition[0], transition[1], transition[2], transition[3]]
                result.append(t)
        elif transition[0][0][id_nasal] == '-' and transition[0][0][id_cons] == '-': # if in non-nasal non-cons state
            #print(transition)
            if transition[1][0] == '>': # if reading end of the word
                #t_copy = []
                #for i in transition[0][0]:
                #    t_copy.append(i)
                t_copy = pre_process.feat_temp(file_sigma)
                if t_copy:
                    t_copy[id_nasal] = transition[0][0][id_nasal]
                t = [transition[0], transition[1], t_copy, transition[3]]
                result.append(t)
            elif transition[1][0][id_nasal] == '+' and transition[1][0][id_cons] == '+': # if reading nasal cons
                t_copy = transition.copy()
                if t_copy:
                    t_copy[2][id_nasal] = '++'
                    #t_copy[2][id_cons] = '-+'
                #t = [transition[0], transition[1], [('+', '-'), ('+', '+')], transition[3]]
                result.append(t_copy)

            elif transition[1][0][id_nasal] == '-' and transition[1][0][id_cons] == '-': # if reading non-nasal non-cons
                t = [transition[0], transition[1], transition[2] , transition[3]]
                result.append(t)
            else:
                t_copy = transition.copy()
                current_nas = t_copy[2][id_nasal]
                #current_cons = t_copy[2][id_cons]
                #print(t_copy)
                if t_copy:
                    t_copy[2][id_nasal] = '-' + current_nas
                    #t_copy[2][id_cons] = '-' + current_cons
                #t = [transition[0], transition[1], [('-', '-'), transition[2]], transition[3]]
                result.append(t_copy)
        else:
            if transition[1][0] == '>': # if reading end of the word
                t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
                result.append(t)
            elif transition[1][0][id_nasal] == '-' and transition[1][0][id_cons] == '-': # if reading non-nasal non-cons
                t_copy = transition.copy()
                if t_copy:
                    t_copy[2][id_nasal] = ''
                    #t_copy[2][id_cons] = ''
                result.append(t_copy)
            else:
                t = [transition[0], transition[1], transition[2], transition[3]]
                result.append(t)

    return result


def nasalize_reverse(sigma, transitions, k, file_sigma):
    """nasalizes a vowel followed by a nasal consonant
        reverse processing

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `nasalize_reverse`.
        """


    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    #print("Those are originial transitions: ", transitions[0]) #[('---+', '---+'), ('---+',), ('---+',), ('---+', '---+')]
    # get features ids
    features_ids = pre_process.feature_id(file_sigma)
    id_cons = 0
    id_nasal = 0
    for i, f in features_ids.items():
        if f == 'nasal':
            id_nasal = i
        if f == 'cons':
            id_cons = i



    if k <= 1:
        return 'k-value must be bigger than 1'

    for transition in transitions:
        # print('transition ', transition)
        if transition[1] == ('>',) or transition[1] == ('<',):
            # print(transition)
            transition[2] = pre_process.feat_temp(file_sigma)
        elif transition[0] == ('<',):
            continue

        elif transition[0][0][id_nasal] == '+' and transition[0][0][id_cons] == '+': # if in nasal cons state
            if transition[1] == ('>',):
                transition[2] = pre_process.feat_temp(file_sigma)

            elif transition[1][0][id_cons] == '-': # if reading vowel
                # print(transition)
                transition[2][id_nasal] = '+'



    return transitions


def nasalize_seg(self, sigma):
    """nasalizes a vowel followed by a nasal consonant

        # k=2, right context

        # input: list of lists of features
        # output: nasalized transitions, list of lists of transitions,
        #         e.g. [[('---+', '---+'), ('---+',), ['-', '-', '-', '+'], ('---+', '---+')], ...]

        Args:
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `nasalize_seg`.
        """

    vowels_oral = [('æ',), ('ɑ',), ('ɔ',), ('ɪ',), ('ɛ',), ('ʌ',), ('ʊ',), ('u',), ('i',)]
    vowels_nasal = [('æ̃',), ('ɑ̃',), ('ɔ̃',), ('ɪ̃',), ('ɛ̃',), ('ʌ̃',), ('ʊ̃',), ('ũ',), ('ĩ',)]
    cons_nasal = [('ŋ',), ('m',), ('n',)]

    transitions = self.transitions_gen(sigma)
    #print("Those are originial transitions: ", transitions[0]) #[('---+', '---+'), ('---+',), ('---+',), ('---+', '---+')]
    # get features ids

    if self.k <= 1:
        return 'k-value must be bigger than 1'

    result = []
    for transition in transitions:
        if transition[0][0] == '<<':
            t = [transition[0], transition[1], [''], transition[3]]
            result.append(t)
        elif transition[0][0] == '<': # if <
            if transition[1][0] == '>': #if <>
                t = [transition[0], transition[1], [''], transition[3]]
                result.append(t)
            elif transition[1] in vowels_oral: #if < non-nasalV
                idx_oral = vowels_oral.index(transition[1])
                t = [transition[0], transition[1], [''], transition[3]]
                result.append(t)
            else:
                t = [transition[0], transition[1], list(transition[2]), transition[3]]
                result.append(t)
        elif transition[0] in vowels_oral: # if in non-nasal non-cons state
            #print(transition)
            idx_oral = vowels_oral.index(transition[0])
            if transition[1][0] == '>': # if reading end of the word
                t = [transition[0], transition[1], list(vowels_oral[idx_oral]), transition[3]]
                result.append(t)
            elif transition[1] in cons_nasal: # if reading nasal cons
                t_copy = transition.copy()
                if t_copy:
                    t_copy[2] = list(vowels_nasal[idx_oral]) + list(transition[1])
                result.append(t_copy)

            elif transition[1] in vowels_oral: # if reading non-nasal non-cons
                t = [transition[0], transition[1], list(transition[0]), transition[3]]
                result.append(t)
            else:
                t_copy = transition.copy()
                if t_copy:
                    t_copy[2] = list(vowels_oral[idx_oral]) + list(transition[1])
                result.append(t_copy)
        else:
            if transition[1][0] == '>': # if reading end of the word
                t = [transition[0], transition[1], [''], transition[3]]
                result.append(t)
            elif transition[1] in vowels_oral: # if reading non-nasal non-cons
                t_copy = transition.copy()
                if t_copy:
                    t_copy[2] = ['']
                result.append(t_copy)
            else:
                t = [transition[0], transition[1], list(transition[2]), transition[3]]
                result.append(t)

    return result

def nasalize_seg_reverse(self, sigma):
    """nasalizes a vowel followed by a nasal consonant

        # k=2, right context

        # input: list of lists of features
        # output: nasalized transitions, list of lists of transitions,
        #         e.g. [[('---+', '---+'), ('---+',), ['-', '-', '-', '+'], ('---+', '---+')], ...]

        Args:
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `nasalize_seg_reverse`.
        """

    vowels_oral = [('æ',), ('ɑ',), ('ɔ',), ('ɪ',), ('ɛ',), ('ʌ',), ('ʊ',), ('u',), ('i',)]
    vowels_nasal = [('æ̃',), ('ɑ̃',), ('ɔ̃',), ('ɪ̃',), ('ɛ̃',), ('ʌ̃',), ('ʊ̃',), ('ũ',), ('ĩ',)]
    cons_nasal = [('ŋ',), ('m',), ('n',)]

    transitions = self.transitions_gen(sigma)
    #print("Those are originial transitions: ", transitions[0]) #[('---+', '---+'), ('---+',), ('---+',), ('---+', '---+')]
    # get features ids

    if self.k <= 1:
        return 'k-value must be bigger than 1'


    for transition in transitions:
        if transition[0] in cons_nasal: # if in non-nasal non-cons state
            # print(transition)
            if transition[1] in vowels_oral:
                idx_oral = vowels_oral.index(transition[1])
                transition[2] = list(vowels_nasal[idx_oral])
            elif transition[1] == ('>',):
                transition[2] = ['']
        elif transition[1] == ('>',) or transition[1] == ('<',):
            # print(transition)
            transition[2] = ['']

        transition[2] = list(transition[2])

    return transitions






def shorten_vowel(sigma, transitions, k, file_sigma):

    """shortens vowels before a cluster of 2 consonants k = 3, right context

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `shorten_vowel`.
        """

    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    # for t in transitions:
    #     print(t)
    # get features ids\n",
    features_ids = pre_process.feature_id(file_sigma)
    #feat_temp = data_shorten.feat_temp()\n",
    id_cons = 0
    id_len = 0
    for i, f in features_ids.items():
        if f == 'long':
            id_len = i
            #print(\"len\", id_len)\n",
        if f == 'cons':
            id_cons = i
            #print(\"cons\", id_cons)\n",

    result = []
    for transition in transitions:
        # print(\"PRINRINT ALL TRANSITIONS: \", transition)\n",
        if len(transition[0]) == 2:
            if (transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '-') and (transition[0][1][id_cons] == '-' and transition[0][1][id_len] == '-'): #if in VV\n",
                if len(transition[1][0]) == 1: #if VV>\n",
                    result.append(transition)
                elif transition[1][0][id_len] == '+': # if VVV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif (transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '-') and (transition[0][1][id_cons] == '-' and transition[0][1][id_len] == '+'): #if in VV:\n",
                if transition[1][0] == '>': #if VV:>\n",
                    out = pre_process.feat_temp(file_sigma)
                    out[id_len] = '+'
                    result.append([transition[0], transition[1], out, transition[3]])
                elif transition[1][0][id_len] == '+': # if VV:V:\n",
#                     t_copy = transition.copy()\n",
#                     if t_copy:\n",
#                         t_copy[2][id_len] = '+'\n",
#                     result.append(t_copy)\n",
                    result.append(transition)
                elif transition[1][0][id_cons] == '+': # if VV:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                        t_copy[2][id_cons] = '+'
                    result.append(t_copy)
                else: # if VV:V\n",
                    t_copy = transition.copy()
                    current_len = t_copy[2][id_len]
                    if t_copy:
                        t_copy[2][id_len] = '+' + current_len
                    result.append(t_copy)
            elif (transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '-') and (transition[0][1][id_cons] == '+'): #if in VC\n",
                if transition[1][0] == '>': #if VC>\n",
                    result.append(transition)
                elif transition[1][0][id_len] == '+': # if VCV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '+': # if VCC\n",
                    result.append(transition)
                elif transition[1][0][id_len] == '-': # if VCV\n",
                    result.append(transition)
            elif (transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '+') and (transition[0][1][id_cons] == '-' and transition[0][1][id_len] == '-'): #if in V:V\n",
                if transition[1][0] == '>': #if V:V>\n",
                    result.append(transition)
                elif transition[1][0][id_len] == '+': # if V:VV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif (transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '+') and (transition[0][1][id_cons] == '-' and transition[0][1][id_len] == '+'): #if in V:V:\n",
                if transition[1][0] == '>': #if VV:>\n",
                    out = pre_process.feat_temp(file_sigma)
                    out[id_len] = '+'
                    result.append([transition[0], transition[1], out, transition[3]])
                elif transition[1][0][id_len] == '+': # if V:V:V:\n",
                    result.append(transition)
#                     t_copy = transition.copy()\n",
#                     if t_copy:\n",
#                         t_copy[2][id_len] = '+'\n",
#                     result.append(t_copy)              \n",
                elif transition[1][0][id_cons] == '+': # if V:V:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                        t_copy[2][id_cons] = '+'
                    result.append(t_copy)
                else: # if V:V:V\n",
                    t_copy = transition.copy()
                    current_len = t_copy[2][id_len]
                    if t_copy:
                        t_copy[2][id_len] = '+' + current_len
                    result.append(t_copy)
            elif (transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '+') and (transition[0][1][id_cons] == '+'): #if in V:C\n",
                if transition[1][0] == '>': #if V:C>\n",
                    out = pre_process.feat_temp(file_sigma)
                    out[id_len] = '+0'
                    out[id_cons] = ''
                    result.append([transition[0], transition[1], out, transition[3]])
#                     t_copy = transition.copy()\n",
#                     if t_copy:\n",
#                         t_copy[2][id_len] = '+0'\n",
#                         t_copy[2][id_cons] = '-+'\n",
#                     result.append(t_copy)\n",
                elif transition[1][0][id_len] == '+': # if V:CV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = '+0'
                        t_copy[2][id_cons] = '-'
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '+': # if V:CC\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = '-00'
                        t_copy[2][id_cons] = '+'
                    result.append(t_copy)
                elif transition[1][0][id_len] == '-': # if V:CV\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = '+0-'
                        t_copy[2][id_cons] = '-'
                    result.append(t_copy)
            elif (transition[0][0][id_cons] == '+') and (transition[0][1][id_cons] == '-' and transition[0][1][id_len] == '-'): #if in CV\n",
                if transition[1][0] == '>': #if CV>\n",
                    result.append(transition)
                elif transition[1][0][id_len] == '+': # if CVV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '+': # if CVC\n",
                    result.append(transition)
                else: #if CVV\n",
                    result.append(transition)
            elif (transition[0][0][id_cons] == '+') and (transition[0][1][id_cons] == '-' and transition[0][1][id_len] == '+'): #if in CV:\n",
                if transition[1][0] == '>': #if CV:>\n",
                    out = pre_process.feat_temp(file_sigma)
                    out[id_len] = '+'
                    result.append([transition[0], transition[1], out, transition[3]])
                elif transition[1][0][id_len] == '+': # if CV:V:\n",
                    result.append(transition)
#                     t_copy = transition.copy()\n",
#                     if t_copy:\n",
#                         t_copy[2][id_len] = '+'\n",
#                     result.append(t_copy)\n",
                elif transition[1][0][id_cons] == '+': # if CV:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                        t_copy[2][id_cons] = '+'
                    result.append(t_copy)
                else: #if CV:V\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = '+-'
                        t_copy[2][id_cons] = '-'
                    result.append(t_copy)
            elif (transition[0][0][id_cons] == '+') and transition[0][1][id_cons] == '+': #if in CC\n",
                if transition[1][0] == '>': #if CC>\n",
                        result.append(transition)
                elif transition[1][0][id_len] == '+': # if CCV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '+': # if CCC\n",
                    result.append(transition)
                else: #if CCV\n",
                    result.append(transition)
        else:
            if transition[0][0] == '<': #if in <:\n",
                if transition[1][0] == '>':
                    result.append(transition)
                elif transition[1][0][id_len] == '+': # if <V:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif transition[0][0] == '<<': #if in <:\n",
                result.append([('<<',), ('<',), len(features_ids)*[''] , ('<',)])
            elif transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '-': #if in V\n",
                #print(transition)\n",
                if transition[1][0] == '>': #if >\n",
                    out = pre_process.feat_temp(file_sigma)
                    result.append([transition[0], transition[1], out, transition[3]])
                elif transition[1][0][id_len] == '+': #if VV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif transition[0][0][id_cons] == '-' and transition[0][0][id_len] == '+': #if in V:\n",
                if transition[1][0] == '>': #if V:>\n",
                    out = pre_process.feat_temp(file_sigma)
                    out[id_len] = '+'
                    result.append([transition[0], transition[1], out, transition[3]])
                elif transition[1][0][id_len] == '+': #if V:V:\n",
                    result.append(transition)
                elif transition[1][0][id_len] == '-': #if V:V\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = '+-'
                        t_copy[2][id_cons] = '-'
                    result.append(t_copy)
                else: #if V:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                        t_copy[2][id_cons] = '+'
                    result.append(t_copy)
            elif transition[0][0][id_cons] == '+': #if in V\n",
                if transition[1][0] == '>': #if >\n",
                    out = pre_process.feat_temp(file_sigma)
                    result.append([transition[0], transition[1], out, transition[3]])
                elif transition[1][0][id_len] == '+': #if VV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = ''
                    result.append(t_copy)
                else:
                    result.append(transition)

    return result



def shorten_vowel_reverse(sigma, transitions, k, file_sigma):

    """shortens vowels before a cluster of 2 consonants k = 3, right context

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `shorten_vowel_reverse`.
        """

    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    # for t in transitions:
    #     print(t)
    # get features ids\n",
    features_ids = pre_process.feature_id(file_sigma)
    #feat_temp = data_shorten.feat_temp()\n",
    id_cons = 0
    id_len = 0
    for i, f in features_ids.items():
        if f == 'long':
            id_len = i
            #print(\"len\", id_len)\n",
        if f == 'cons':
            id_cons = i
            #print(\"cons\", id_cons)\n",

    result = []
    for transition in transitions:
        # print(\"PRINRINT ALL TRANSITIONS: \", transition)\n",
        if transition[1] == ('>',) or transition[1] == ('<',):
            t_copy = transition.copy()
            if t_copy:
                t_copy[2] = pre_process.feat_temp(file_sigma)
            result.append(t_copy)
        # elif transition[0] == ('<',):
        #     continue
        elif len(transition[0]) == 2:
            if (transition[0][0][id_cons] == '+') and (transition[0][1][id_cons] == '+'): #if in VV\n",
                # print(f'Trans with state in: two consoannts \n {transition}')
                if transition[1] == ('>',):
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = pre_process.feat_temp(file_sigma)
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '-': # if VVV:\n",
                    # print('BEFORE: ', transition)

                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2][id_len] = '-'
                    result.append(t_copy)
                    # print('AFTER: ', t_copy)
                else:
                    result.append(transition)
            else:
                result.append(transition)
        else:
            result.append(transition)

    return result

def shorten_vowel_seg(self, sigma):

    """shortens vowels before a cluster of 2 consonants k = 3, right context

        Args:
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `shorten_vowel_seg`.
        """

    # transitions = self.correct_transitions(sigma)
    short_vowels = [('o',), ('i',)]
    long_vowels = [('o:',), ('i:',)]
    consonants = [('ʈˀ',), ('g',), ('n',)]

    transitions = self.transitions_gen(sigma)
    result = []
    for transition in transitions:
        if len(transition[0]) == 2:
            new_from_state = []
            for i in transition[0]:
                new = []
                new.append(i)
                new_from_state.append(new)
            transition[0] = new_from_state
            if (tuple(transition[0][0]) in short_vowels) and (tuple(transition[0][1]) in short_vowels): #if in VV\n",
                if transition[1] in long_vowels: # if VVV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1][0] == '>':
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in short_vowels and tuple(transition[0][1]) in long_vowels: #if in VV:\n",
                # print('IN state: short vowel+long vowel', transition)
                if transition[1][0] == '>': #if VV:>\n"
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = transition[0][1]
                    result.append(t_copy)
                elif transition[1] in long_vowels: # if VV:V:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = transition[0][1]
                    result.append(t_copy)
                elif transition[1] in consonants: # if VV:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else: # if VV:V\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0][1]) + list(transition[1])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in short_vowels and tuple(transition[0][1]) in consonants: #if in VC\n",
                if transition[1] in long_vowels: # if VCV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1][0] == '>': #if VC>\n"
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in long_vowels and tuple(transition[0][1]) in short_vowels: #if in V:V\n",
                if transition[1] in long_vowels: # if V:VV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1][0] == '>':
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in long_vowels and tuple(transition[0][1]) in long_vowels: #if in V:V:\n",
                if transition[1][0] == '>' or transition[1] in long_vowels: #if VV:>\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0][1])
                    result.append(t_copy)
                elif transition[1] in consonants: # if V:V:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else: # if V:V:V\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0][1]) + list(transition[1][0])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in long_vowels and tuple(transition[0][1]) in consonants: #if in V:C\n",
                idx_long = long_vowels.index(tuple(transition[0][0]))
                if transition[1][0] == '>' or transition[1] in long_vowels: #if V:C>\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0][0]) + list(transition[0][1])
                    result.append(t_copy)
                elif transition[1] in consonants: # if V:CC\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(short_vowels[idx_long]) + list(transition[0][1]) + list(transition[1])
                    result.append(t_copy)
                elif transition[1] in short_vowels: # if V:CV\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0][0]) + list(transition[0][1]) + list(transition[1])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in consonants and tuple(transition[0][1]) in short_vowels: #if in CV\n",
                if transition[1] in long_vowels: # if CVV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1][0] == '>':
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in consonants and tuple(transition[0][1]) in long_vowels: #if in CV:\n",
                if transition[1] in consonants: # if CV:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1] in short_vowels: # if CV:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0][1]) + list(transition[1])
                    result.append(t_copy)

                else: #if CV:V\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0][1])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in consonants and tuple(transition[0][1]) in consonants: #if in CC\n",
                if transition[1] in long_vowels: # if CCV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1][0] == '>':
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
        else:
            if transition[0][0] == '<': #if in <:\n",
                if transition[1][0] == '>':
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1] in long_vowels: # if <V:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
            elif transition[0][0] == '<<': #if in <:\n",
                # print('THSI IS THE ONE!!:', transition)
                t_copy = transition.copy()
                # print(f'coopy: {t_copy}')
                if t_copy:
                    t_copy[2] = ['']
                # print(f'coopy after: {t_copy}')
                result.append(t_copy)
            elif transition[0] in short_vowels or transition[0] in consonants: #if in V\n",
                if transition[1] in long_vowels: #if VV:\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1][0] == '>': #if V>\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)

            elif transition[0] in long_vowels: #if in V:\n",
                if transition[1][0] == '>' or transition[1] in long_vowels: #if V:>\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0])
                    result.append(t_copy)
                elif transition[1] in short_vowels: #if V:V\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = list(transition[0]) + list(transition[1])
                    result.append(t_copy)
                else: #if V:C\n",
                    t_copy = transition.copy()
                    if t_copy:
                        t_copy[2] = ['']
                    # result.append(t_copy)
                    else:
                        if t_copy:
                            t_copy[2] = list(t_copy[2])
                    result.append(t_copy)


    for i in result:
        if len(i[0]) == 2:
            new_st_from = tuple(item[0] for item in i[0])
            i[0] = new_st_from
        if '' in i[2]:
            i[2] = ['']


    return result





def schwa_epen(sigma, transitions, k, file_sigma):

    """inserts schwa in between Cs in the the following context CC>
        k=3, right and left context

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `schwa_epen`.
        """


    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    features_ids = pre_process.feature_id(file_sigma)



    if k <= 1:
        return 'k-value must be bigger than 1'


    id_high = 0
    id_low = 0
    id_tense = 0
    id_front = 0
    id_back = 0
    id_round = 0
    id_long = 0
    id_cons = 0
    id_son = 0
    id_cont = 0
    id_delrel = 0
    id_approx = 0
    id_nasal = 0
    id_voice = 0
    id_lab = 0
    id_labdent = 0
    id_cor = 0
    id_ant = 0
    id_distr = 0
    id_strid = 0
    id_lat = 0
    id_dor = 0
    #all_feat = [id_cons, id_high, id_low, id_nasal, id_cont, id_front, id_son, id_approx, id_voice, id_lab, id_cor, id_ant]
    #schwa = '----++0-+000'

    for i, f in features_ids.items():
        if f == 'high':
            id_high = i
        if f == 'low':
            id_low = i
        if f == 'tense':
            id_tense = i
        if f == 'front':
            id_front = i
        if f == 'back':
            id_back = i
        if f == 'round':
            id_round = i
        if f == 'long':
            id_long = i
        if f == 'cons':
            id_cons = i
        if f == 'son':
            id_son = i
        if f == 'cont':
            id_cont = i
        if f == 'delrel':
            id_delrel = i
        if f == 'approx':
            id_approx = i
        if f == 'nasal':
            id_nasal = i
        if f == 'voice':
            id_voice = i
        if f == 'lab':
            id_lab = i
        if f == 'labdent':
            id_labdent = i
        if f == 'cor':
            id_cor = i
        if f == 'ant':
            id_ant = i
        if f == 'distr':
            id_distr = i
        if f == 'strid':
            id_strid = i
        if f == 'lat':
            id_lat = i
        if f == 'dor':
            id_dor = i

    #all_feat = [id_cons, id_high, id_low, id_nasal]
    #schwa = '----'
    all_feat = [id_high, id_low, id_tense, id_front, id_back, id_round, id_long, id_cons, id_son, id_cont, id_delrel, id_approx, id_nasal, id_voice, id_lab, id_labdent, id_cor, id_ant, id_distr, id_strid, id_lat, id_dor]
    schwa = '--+-----++00-+00000000'

    #template = self.feat_temp()
    result = []
    result.append([('<<',), ('<',), len(features_ids) * [''], ('<',)])

    for transition in transitions:
        #print(transition)
        if len(transition[0]) == 1:
            if transition[0][0] == '<<':
                continue
            elif transition[0][0] == '<': # in < states
                result.append(transition) # identity
            elif transition[0][0][id_cons] == '+': # in C state
                if transition[1][0] == '>': # reading >
                    result.append(transition)
                elif transition[1][0][id_cons] == '-': # reading v
                    result.append(transition)
                elif transition[1][0][id_cons] == '+':# reading C
                    t_copy = copy.deepcopy(transition)
                    for feature in all_feat:
                        t_copy[2][feature] = ''
                    result.append(t_copy)
            elif transition[0][0][id_cons] == '-': # in V states
                result.append(transition) # identity
        elif len(transition[0]) == 2: # in states of len 2
            if transition[0][1][id_cons] == '-': # in states ending in V
                result.append(transition)
            elif transition[0][0][id_cons] == '-' and transition[0][1][id_cons] == '+': # state VC
                if transition[1][0] == '>': # reading >
                    result.append(transition)
                elif transition[1][0][id_cons] == '-': # reading V
                    result.append(transition)
                elif transition[1][0][id_cons] == '+': # reading C
                    t_copy = copy.deepcopy(transition)
                    for feature in all_feat:
                        t_copy[2][feature] = ''
                    result.append(t_copy)
            elif transition[0][0][id_cons] == '+' and transition[0][1][id_cons] == '+': # state CC
                # print('In CC state')
                if transition[1][0] == '>': # reading >
                    t_copy = copy.deepcopy(transition)
                    for feature in all_feat:
                        t_copy[2][feature] = schwa[feature] + transition[0][1][feature]
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '-': # reading V
                    t_copy = copy.deepcopy(transition)
                    for feature in all_feat:
                        t_copy[2][feature] = transition[0][1][feature] + transition[1][0][feature]
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '+':# reading C
                    # print('reading C:')
                    # print(transition)
                    t_copy = copy.deepcopy(transition)
                    for feature in all_feat:
                        t_copy[2][feature] = transition[0][1][feature]
                    result.append(t_copy)
                    # print(f'transition after: {t_copy}')
            else: # states CV and VV
                result.append(transition)
                # if transition[1][0] == '>': # reading >
                #     result.append(transition)
                # elif transition[1][0][id_cons] == '-': # reading V
                #     result.append(transition)
                # elif transition[1][0][id_cons] == '+':# reading C
                    # t_copy = copy.deepcopy(transition)
                    # for feature in all_feat:
                    #     t_copy[2][feature] = ''
                    # result.append(t_copy)

    return result

def schwa_epen_reverse(sigma, transitions, k, file_sigma):

    """inserts schwa in the the following context C__C>
        k=4, right and left context

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `schwa_epen_reverse`.
        """

    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    features_ids = pre_process.feature_id(file_sigma)

    if k <= 1:
        return 'k-value must be bigger than 1'

    id_high = 0
    id_low = 0
    id_tense = 0
    id_front = 0
    id_back = 0
    id_round = 0
    id_long = 0
    id_cons = 0
    id_son = 0
    id_cont = 0
    id_delrel = 0
    id_approx = 0
    id_nasal = 0
    id_voice = 0
    id_lab = 0
    id_labdent = 0
    id_cor = 0
    id_ant = 0
    id_distr = 0
    id_strid = 0
    id_lat = 0
    id_dor = 0
    #all_feat = [id_cons, id_high, id_low, id_nasal, id_cont, id_front, id_son, id_approx, id_voice, id_lab, id_cor, id_ant]
    #schwa = '----++0-+000'

    for i, f in features_ids.items():
        if f == 'high':
            id_high = i
        if f == 'low':
            id_low = i
        if f == 'tense':
            id_tense = i
        if f == 'front':
            id_front = i
        if f == 'back':
            id_back = i
        if f == 'round':
            id_round = i
        if f == 'long':
            id_long = i
        if f == 'cons':
            id_cons = i
        if f == 'son':
            id_son = i
        if f == 'cont':
            id_cont = i
        if f == 'delrel':
            id_delrel = i
        if f == 'approx':
            id_approx = i
        if f == 'nasal':
            id_nasal = i
        if f == 'voice':
            id_voice = i
        if f == 'lab':
            id_lab = i
        if f == 'labdent':
            id_labdent = i
        if f == 'cor':
            id_cor = i
        if f == 'ant':
            id_ant = i
        if f == 'distr':
            id_distr = i
        if f == 'strid':
            id_strid = i
        if f == 'lat':
            id_lat = i
        if f == 'dor':
            id_dor = i

    #all_feat = [id_cons, id_high, id_low, id_nasal]
    #schwa = '----'
    all_feat = [id_high, id_low, id_tense, id_front, id_back, id_round, id_long, id_cons, id_son, id_cont, id_delrel, id_approx, id_nasal, id_voice, id_lab, id_labdent, id_cor, id_ant, id_distr, id_strid, id_lat, id_dor]
    schwa = '--+-----++00-+00000000'

    #template = self.feat_temp()
    result = []
    # result.append([('<<',), ('<',), len(features_ids) * [''], ('<',)])

    for transition in transitions:
        # print(f'Here is the TRANS: {transition}')
        if len(transition[0]) == 1:
            if transition[1] == ('>',) or transition[1] == ('<',):
                t_copy = transition.copy()
                if t_copy:
                    t_copy[2] = pre_process.feat_temp(file_sigma)
                result.append(t_copy)
            elif transition[0] == ('<',):
                result.append(transition)
            elif transition[0][0][id_cons] == '+': # state C
                if transition[1] == ('>',):
                    result.append(transition)
                elif transition[1][0][id_cons] == '+': # reading C
                    t_copy = copy.deepcopy(transition)
                    for feature in all_feat:
                        t_copy[2][feature] = schwa[feature] + transition[1][0][feature]
                    result.append(t_copy)
                else:
                    result.append(transition)
            else:
                result.append(transition)
        else:
            result.append(transition)


    return result


def schwa_epen_seg(self, sigma):

    """inserts schwa in the the following context C__C>
        k=3, right and left context

        Args:
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `schwa_epen_seg`.
        """


    #all_feat = [id_cons, id_high, id_low, id_nasal]
    #schwa = '----'
    schwa = ['ə']
    consonants = [('m',), ('β',), ('ɬ',), ('t͡ʃ',), ('p',)]
    vowels = [('i',), ('o',)]

    #template = self.feat_temp()
    result = []
    result.append([('<<',), ('<',), [''], ('<',)])
    transitions = self.transitions_gen(sigma)

    for transition in transitions:
        # print(f' #############################################################\nTRANSITION: {transition}')
        if len(transition[0]) == 1:
            if transition[0][0] == '<<':
                continue
            elif transition[0][0] == '<': # in < states
                if transition[1][0] == '>': # reading >
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy) # identity
            elif transition[0] in consonants: # in C state
                if transition[1][0] == '>': # reading >
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1] in vowels: # reading v
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy) # identity
                elif transition[1] in consonants:# reading C
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                        # t_copy[2] = schwa + list(transition[1])
                    result.append(t_copy)
            elif tuple(transition[0][0]) in vowels: # in V states
                if transition[1][0] == '>': # reading >
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else: # reading v or c
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy) # identity
        elif len(transition[0]) == 2: # in states of len 2
            new_from_state = []
            for i in transition[0]:
                new = []
                new.append(i)
                new_from_state.append(new)
            transition[0] = new_from_state
            # print(f'NEW state in: {transition[0]}')
            # print(f'\t\t\t for transition: {transition}')
            # print(f'tuple(transition[0][1]): {tuple(transition[0][1])} is in consonants {tuple(transition[0][1]) in consonants}\n')
            if tuple(transition[0][1]) in vowels: # in states ending in V
                # print(f'transition in _V: {transition}')
                if transition[1][0] == '>': # reading >
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy) # identity
            elif (tuple(transition[0][0]) in vowels) and (tuple(transition[0][1]) in consonants): # state VC
                # print(f'------transition in VC: {transition}------')
                # print(f'+++++++++ and that what Im reading: {tuple(transition[1][0])}+++++++++ihaaaaa')
                if transition[1][0] == '>': # reading >
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif tuple(transition[1][0]) in vowels: # reading V
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy) # identity
                elif tuple(transition[1]) in consonants: # reading C
                    # print(f'\n------Im reading a consonant: {tuple(transition[1][0])}------\n')
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy) # identity
                    # print(f't_copy: {t_copy}')
            elif (tuple(transition[0][0]) in consonants) and (tuple(transition[0][1]) in consonants): # state CC
                # print(f'transition in CC: {transition}')
                if transition[1][0] == '>': # reading >
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = schwa + transition[0][1]
                    result.append(t_copy)
                elif transition[1] in vowels: # reading V
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = transition[0][1] + list(transition[1][0])
                    result.append(t_copy)
                elif transition[1] in consonants:# reading C
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = transition[0][1]
                    result.append(t_copy)
    #         else: # states CV and VV
    #             print(f'transition in CV or VV: {transition}')
    #             if transition[1][0] == '>': # reading >
    #                 t_copy = copy.deepcopy(transition)
    #                 if t_copy:
    #                     t_copy[2] = ['']
    #                 result.append(t_copy)
    #             # elif transition[1][0][id_cons] == '-': # reading V
    #             else:
    #                 t_copy = copy.deepcopy(transition)
    #                 if t_copy:
    #                     t_copy[2] = list(t_copy[2])
    #                 result.append(t_copy) # identity
    #             # elif transition[1][0][id_cons] == '+':# reading C
    #             #     t_copy = copy.deepcopy(transition)
    #             #     for feature in all_feat:
    #             #         t_copy[2][feature] = ''
    #             #     result.append(t_copy)
    for i in result:
        if len(i[0]) == 2:
            new_st_from = tuple(item[0] for item in i[0])
            i[0] = new_st_from

    return result



def final_dev(self, sigma):

    """inserts schwa in the the following context C__C>
        k=4, right and left context

        Args:
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `final_dev`.
        """

    trans_corrected = self.correct_transitions(sigma)
    features_ids = self.feature_id()

    if self.k <= 1:
        return 'k-value must be bigger than 1'

    features_ids = self.feature_id()
    id_voice = 0
    id_son = 0
    for i, f in features_ids.items():
        if f == 'voice':
            id_voice = i
        if f == 'son':
            id_son = i

    #template = self.feat_temp()
    result = []
    result.append([('<<',), ('<',), len(features_ids) * [''], ('<',)])

    for transition in trans_corrected:
        #print(transition)
        #if len(transition[0]) == 1:
        if transition[0][0] == '<<': # in << state
            continue
        elif transition[0][0] == '<': # in < states
            if transition[1][0] == '>':
                t = [transition[0], transition[1], self.feat_temp(), transition[3]]
                result.append(t)
            elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': # reading voiced obst
                t_copy = copy.deepcopy(transition)
                t_copy[2][id_voice] = ''
                result.append(t_copy)
            else: # reading voiceless obstr
                result.append(transition)
        elif transition[0][0][id_son] == '-' and transition[0][0][id_voice] == '+': # in voiced obstruent state
            if transition[1][0] == '>':
                t_copy = copy.deepcopy(transition)
                t_copy[2][id_voice] = '-'
                result.append(t_copy)
            elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '-': # if reading a voiceless obstruent
                t_copy = copy.deepcopy(transition)
                t_copy[2][id_voice] = transition[0][0][id_voice] + transition[1][0][id_voice]
                result.append(t_copy)
            elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': # if reading a voiced obstruent
                t_copy = copy.deepcopy(transition)
                t_copy[2][id_voice] = transition[0][0][id_voice]
                result.append(t_copy)
            else: # if reading non-obstruent
                t_copy = copy.deepcopy(transition)
                t_copy[2][id_voice] = transition[0][0][id_voice] + transition[1][0][id_voice]
                result.append(t_copy)
        else: # in non-obstruent state
            if transition[1][0] == '>':
                result.append(transition)
            elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': # if reading a voiced obstruent
                t_copy = copy.deepcopy(transition)
                t_copy[2][id_voice] = ''
                result.append(t_copy)
            else: # if reading non-obstruent
                result.append(transition)


    return result

def o_raising(self, sigma):
    """Apply the Polish vowel-raising rule to transition outputs.

        Args:
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `o_raising`.
        """


    trans_corrected = self.correct_transitions(sigma)
    features_ids = self.feature_id()

    if self.k <= 1:
        return 'k-value must be bigger than 1'

    features_ids = self.feature_id()
    id_voice = 0
    id_son = 0
    for i, f in features_ids.items():
        if f == 'voice':
            id_voice = i
        if f == 'son':
            id_son = i
        if f == 'cons':
            id_cons = i
        if f == 'nasal':
            id_nasal = i
        if f == 'cont':
            id_cont = i
        if f == 'tense':
            id_tense = i
        if f == 'round':
            id_round = i
        if f == 'low':
            id_low = i
        if f == 'back':
            id_back = i
        if f == 'high':
            id_high = i

    result = []
    result.append([('<<',), ('<',), len(features_ids) * [''], ('<',)])

    #o = '++--+-+'
    #u = '++--+++'
    all_feat = [id_voice, id_son, id_cons, id_nasal, id_cont, id_tense, id_round, id_low, id_back, id_high]

    for transition in trans_corrected:
        if len(transition[0]) == 1:
            if transition[0][0] == '<<': # in << state
                continue
            elif transition[0][0] == '<': # in < states
                if transition[1][0] == '>':
                    t = [transition[0], transition[1], self.feat_temp(), transition[3]]
                    result.append(t)
                elif transition[1][0][id_low] == '-' and transition[1][0][id_tense] == '-' and transition[1][0][id_nasal] == '-' and transition[1][0][id_back] == '+'  and transition[1][0][id_high] == '-': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = ''
                    t_copy[2][id_tense] = ''
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif transition[0][0][id_low] == '-' and transition[0][0][id_tense] == '-' and transition[0][0][id_nasal] == '-' and transition[0][0][id_back] == '+'  and transition[0][0][id_high] == '-': # in o state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '-'
                    t_copy[2][id_tense] = '-'
                    result.append(t_copy)
                elif transition[1][0][id_low] == '-' and transition[1][0][id_tense] == '-' and transition[1][0][id_nasal] == '-' and transition[1][0][id_back] == '+'  and transition[1][0][id_high] == '-': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '-'
                    t_copy[2][id_tense] = '-'
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '+' and transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': # reading voiced obstruent
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = ''
                    t_copy[2][id_tense] = ''
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '-' + transition[1][0][id_high]
                    t_copy[2][id_tense] = '-' + transition[1][0][id_tense]
                    result.append(t_copy)
            else:
                result.append(transition)
        elif len(transition[0]) == 2:
            if transition[0][1][id_low] == '-' and transition[0][1][id_tense] == '-' and transition[0][1][id_nasal] == '-' and transition[0][1][id_back] == '+'  and transition[0][1][id_high] == '-': # states ending in o
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '-'
                    t_copy[2][id_tense] = '-'
                    result.append(t_copy)
                elif transition[1][0][id_low] == '-' and transition[1][0][id_tense] == '-' and transition[1][0][id_nasal] == '-' and transition[1][0][id_back] == '+'  and transition[1][0][id_high] == '-': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '-'
                    t_copy[2][id_tense] = '-'
                    result.append(t_copy)
                elif transition[1][0][id_cons] == '+' and transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': # reading voiced obstruent
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '' #+ transition[1][0][id_high]
                    t_copy[2][id_tense] = '' #+ transition[1][0][id_tense]
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '-' + transition[1][0][id_high]
                    t_copy[2][id_tense] = '-' + transition[1][0][id_tense]
                    result.append(t_copy)
            elif transition[0][0][id_low] == '-' and transition[0][0][id_tense] == '-' and transition[0][0][id_nasal] == '-' and transition[0][0][id_back] == '+' and transition[0][0][id_high] == '-' and transition[0][1][id_cons] == '+' and transition[0][1][id_son] == '-' and transition[0][1][id_voice] == '+': # in o Voiced Obstr state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '+' + transition[0][1][id_high]
                    t_copy[2][id_tense] = '+' + transition[0][1][id_tense]
                    result.append(t_copy)
                elif transition[1][0][id_low] == '-' and transition[1][0][id_tense] == '-' and transition[1][0][id_nasal] == '-' and transition[1][0][id_back] == '+'  and transition[1][0][id_high] == '-': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high]
                    t_copy[2][id_tense] = transition[0][0][id_high] + transition[0][1][id_tense]
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high] + transition[1][0][id_high]
                    t_copy[2][id_tense] = transition[0][0][id_high] + transition[0][1][id_tense] + transition[1][0][id_tense]
                    result.append(t_copy)
            else:
                if transition[1][0] == '>':
                    result.append(transition)
                elif transition[1][0][id_low] == '-' and transition[1][0][id_tense] == '-' and transition[1][0][id_nasal] == '-' and transition[1][0][id_back] == '+'  and transition[1][0][id_high] == '-': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = ''
                    t_copy[2][id_tense] = ''
                    result.append(t_copy)
                else:
                    result.append(transition)

    return result

def o_raise_devoice_new(sigma, transitions, k, file_sigma):
    """Apply Polish raising and final devoicing to feature transitions.

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `o_raise_devoice_new`.
        """


    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    features_ids = pre_process.feature_id(file_sigma)

    if k <= 1:
        return 'k-value must be bigger than 1'


    id_voice = 0
    id_son = 0
    for i, f in features_ids.items():
        if f == 'voice':
            id_voice = i
        if f == 'son':
            id_son = i
        if f == 'cons':
            id_cons = i
        if f == 'cor':
            id_cor = i
        if f == 'cont':
            id_cont = i
        if f == 'ant':
            id_ant = i
        if f == 'dor':
            id_dor = i
        if f == 'lab':
            id_lab = i
        if f == 'distr':
            id_distr = i
        if f == 'delrel':
            id_delrel = i
        if f == 'nasal':
            id_nasal = i
        if f == 'lat':
            id_lat = i
        if f == 'high':
            id_high = i
        if f == 'back':
            id_back = i
        if f == 'low':
            id_low = i
        if f == 'tense':
            id_tense = i
        if f == 'round':
            id_round = i



    result = []
    result.append([('<<',), ('<',), len(features_ids) * [''], ('<',)])

    #o = '++--+-+-+-'
    all_feat = [id_voice, id_son, id_cons, id_nasal, id_cont, id_tense, id_round, id_low, id_back, id_high]

    for transition in transitions:
        if len(transition[0]) == 1:
            if transition[0][0] == '<<': # in << state
                continue
            elif transition[0][0] == '<': # in < states
                if transition[1][0] == '>':
                    t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
                    result.append(t)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif transition[0][0] == '++-+000000-0-+--+': # in O state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                elif transition[1][0][id_son] == '+' and transition[1][0][id_cons] == '+' and transition[1][0][id_nasal] == '-': #reading S non N
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[1][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son] + transition[1][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons] + transition[1][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont] + transition[1][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor] + transition[1][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant] + transition[1][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor] + transition[1][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab] + transition[1][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr] + transition[1][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[1][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[1][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat] + transition[1][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high] + transition[1][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back] + transition[1][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low] + transition[1][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense] + transition[1][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round] + transition[1][0][id_round]
                    result.append(t_copy)
            elif transition[0][0][id_son] == '-' and transition[0][0][id_voice] == '+': # in D state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = '-'
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[1][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son] + transition[1][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons] + transition[1][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont] + transition[1][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor] + transition[1][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant] + transition[1][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor] + transition[1][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab] + transition[1][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr] + transition[1][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[1][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[1][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat] + transition[1][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high] + transition[1][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back] + transition[1][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low] + transition[1][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense] + transition[1][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round] + transition[1][0][id_round]
                    result.append(t_copy)
            else: # in ELSE state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                else:
                    result.append(transition)
        elif len(transition[0]) == 2:
            #if transition[0][0][id_voice] == '+' and transition[0][0][id_son] == '+' and transition[0][0][id_cons] == '-' and transition[0][0][id_nasal] == '-' and transition[0][0][id_cont] == '+' and transition[0][0][id_tense] == '-' and transition[0][0][id_round] == '+' and transition[0][0][id_low] == '-' and transition[0][0][id_back] == '+' and transition[0][0][id_high] == '-':
            if transition[0][0] == '++-+000000-0-+--+':
                if transition[0][1] == '++-+000000-0-+--+': # in OO states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '+' and transition[1][0][id_cons] == '+' and transition[1][0][id_nasal] == '-': #reading S
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                elif transition[0][1][id_son] == '-' and transition[0][1][id_voice] == '+': # in OD states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ '-'
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = '+' + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = '+' + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                elif transition[0][1][id_son] == '+' and transition[0][1][id_cons] == '+': # in OS states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = '+' + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = '+' + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)

                else: # in Oelse state
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    else:
                        result.append(transition)


            else:
                if transition[0][1] == '++-+000000-0-+--+': # in elseO states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        #print("reading o ", transition)
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '+' and transition[1][0][id_cons] == '+' and transition[1][0][id_nasal] == '-': #reading S
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                elif transition[0][1][id_son] == '-' and transition[0][1][id_voice] == '+': # in elseD states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = '-'
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                else: # in ELSEelse state
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    else:
                        result.append(transition)
    return result



def o_raise_devoice(sigma, transitions, k, file_sigma):
    """Apply the original Polish raising and devoicing implementation.

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `o_raise_devoice`.
        """


    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    features_ids = pre_process.feature_id(file_sigma)

    if k <= 1:
        return 'k-value must be bigger than 1'


    id_voice = 0
    id_son = 0
    for i, f in features_ids.items():
        if f == 'voice':
            id_voice = i
        if f == 'son':
            id_son = i
        if f == 'cons':
            id_cons = i
        if f == 'cor':
            id_cor = i
        if f == 'cont':
            id_cont = i
        if f == 'ant':
            id_ant = i
        if f == 'dor':
            id_dor = i
        if f == 'lab':
            id_lab = i
        if f == 'distr':
            id_distr = i
        if f == 'delrel':
            id_delrel = i
        if f == 'nasal':
            id_nasal = i
        if f == 'lat':
            id_lat = i
        if f == 'high':
            id_high = i
        if f == 'back':
            id_back = i
        if f == 'low':
            id_low = i
        if f == 'tense':
            id_tense = i
        if f == 'round':
            id_round = i



    result = []
    result.append([('<<',), ('<',), len(features_ids) * [''], ('<',)])

    #o = '++--+-+-+-'
    all_feat = [id_voice, id_son, id_cons, id_nasal, id_cont, id_tense, id_round, id_low, id_back, id_high]

    for transition in transitions:
        if len(transition[0]) == 1:
            if transition[0][0] == '<<': # in << state
                continue
            elif transition[0][0] == '<': # in < states
                if transition[1][0] == '>':
                    t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
                    result.append(t)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif transition[0][0] == '++-+000000-0-+--+': # in O state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                # elif transition[1][0][id_son] == '+' and transition[1][0][id_cons] == '+': #reading S
                #     t_copy = copy.deepcopy(transition)
                #     t_copy[2] = len(features_ids) * ['']
                #     result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[1][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son] + transition[1][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons] + transition[1][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont] + transition[1][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor] + transition[1][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant] + transition[1][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor] + transition[1][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab] + transition[1][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr] + transition[1][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[1][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[1][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat] + transition[1][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high] + transition[1][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back] + transition[1][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low] + transition[1][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense] + transition[1][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round] + transition[1][0][id_round]
                    result.append(t_copy)
            elif transition[0][0][id_son] == '-' and transition[0][0][id_voice] == '+': # in D state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = '-'
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = '+'
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round]
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[1][0][id_voice]
                    t_copy[2][id_son] = transition[0][0][id_son] + transition[1][0][id_son]
                    t_copy[2][id_cons] = transition[0][0][id_cons] + transition[1][0][id_cons]
                    t_copy[2][id_cont] = transition[0][0][id_cont] + transition[1][0][id_cont]
                    t_copy[2][id_cor] = transition[0][0][id_cor] + transition[1][0][id_cor]
                    t_copy[2][id_ant] = transition[0][0][id_ant] + transition[1][0][id_ant]
                    t_copy[2][id_dor] = transition[0][0][id_dor] + transition[1][0][id_dor]
                    t_copy[2][id_lab] = transition[0][0][id_lab] + transition[1][0][id_lab]
                    t_copy[2][id_distr] = transition[0][0][id_distr] + transition[1][0][id_distr]
                    t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[1][0][id_delrel]
                    t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[1][0][id_nasal]
                    t_copy[2][id_lat] = transition[0][0][id_lat] + transition[1][0][id_lat]
                    t_copy[2][id_high] = transition[0][0][id_high] + transition[1][0][id_high]
                    t_copy[2][id_back] = transition[0][0][id_back] + transition[1][0][id_back]
                    t_copy[2][id_low] = transition[0][0][id_low] + transition[1][0][id_low]
                    t_copy[2][id_tense] = transition[0][0][id_tense] + transition[1][0][id_tense]
                    t_copy[2][id_round] = transition[0][0][id_round] + transition[1][0][id_round]
                    result.append(t_copy)
            else: # in ELSE state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2] = len(features_ids) * ['']
                    result.append(t_copy)
                else:
                    result.append(transition)
        elif len(transition[0]) == 2:
            #if transition[0][0][id_voice] == '+' and transition[0][0][id_son] == '+' and transition[0][0][id_cons] == '-' and transition[0][0][id_nasal] == '-' and transition[0][0][id_cont] == '+' and transition[0][0][id_tense] == '-' and transition[0][0][id_round] == '+' and transition[0][0][id_low] == '-' and transition[0][0][id_back] == '+' and transition[0][0][id_high] == '-':
            if transition[0][0] == '++-+000000-0-+--+':
                if transition[0][1] == '++-+000000-0-+--+': # in OO states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    # elif transition[1][0][id_son] == '+' and transition[1][0][id_cons] == '+': #reading S
                    #     t_copy = copy.deepcopy(transition)
                    #     t_copy[2] = len(features_ids) * ['']
                    #     result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                elif transition[0][1][id_son] == '-' and transition[0][1][id_voice] == '+': # in OD states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ '-'
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = '+' + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = '+' + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][0][id_voice]+ transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][0][id_son] + transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][0][id_cons] + transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][0][id_cont] + transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][0][id_cor] + transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][0][id_ant] + transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][0][id_dor] + transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][0][id_lab] + transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][0][id_distr] + transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][0][id_delrel] + transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][0][id_nasal] + transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][0][id_lat] + transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][0][id_high] + transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][0][id_back] + transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][0][id_low] + transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][0][id_tense] + transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][0][id_round] + transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                else: # in Oelse state
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    else:
                        result.append(transition)
            else:
                if transition[0][1] == '++-+000000-0-+--+': # in elseO states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        #print("reading o ", transition)
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    # elif transition[1][0][id_son] == '+' and transition[1][0][id_cons] == '+': #reading S
                    #     t_copy = copy.deepcopy(transition)
                    #     t_copy[2] = len(features_ids) * ['']
                    #     result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                elif transition[0][1][id_son] == '-' and transition[0][1][id_voice] == '+': # in elseD states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = '-'
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        t_copy[2][id_voice] = transition[0][1][id_voice] + transition[1][0][id_voice]
                        t_copy[2][id_son] = transition[0][1][id_son] + transition[1][0][id_son]
                        t_copy[2][id_cons] = transition[0][1][id_cons] + transition[1][0][id_cons]
                        t_copy[2][id_cont] = transition[0][1][id_cont] + transition[1][0][id_cont]
                        t_copy[2][id_cor] = transition[0][1][id_cor] + transition[1][0][id_cor]
                        t_copy[2][id_ant] = transition[0][1][id_ant] + transition[1][0][id_ant]
                        t_copy[2][id_dor] = transition[0][1][id_dor] + transition[1][0][id_dor]
                        t_copy[2][id_lab] = transition[0][1][id_lab] + transition[1][0][id_lab]
                        t_copy[2][id_distr] = transition[0][1][id_distr] + transition[1][0][id_distr]
                        t_copy[2][id_delrel] = transition[0][1][id_delrel] + transition[1][0][id_delrel]
                        t_copy[2][id_nasal] = transition[0][1][id_nasal] + transition[1][0][id_nasal]
                        t_copy[2][id_lat] = transition[0][1][id_lat] + transition[1][0][id_lat]
                        t_copy[2][id_high] = transition[0][1][id_high] + transition[1][0][id_high]
                        t_copy[2][id_back] = transition[0][1][id_back] + transition[1][0][id_back]
                        t_copy[2][id_low] = transition[0][1][id_low] + transition[1][0][id_low]
                        t_copy[2][id_tense] = transition[0][1][id_tense] + transition[1][0][id_tense]
                        t_copy[2][id_round] = transition[0][1][id_round] + transition[1][0][id_round]
                        result.append(t_copy)
                else: # in ELSEelse state
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = len(features_ids) * ['']
                        result.append(t_copy)
                    else:
                        result.append(transition)
    return result




def o_raise_devoice_reverse(sigma, transitions, k, file_sigma):
    """Apply Polish raising and devoicing for right-to-left processing.

        Args:
            sigma: Input alphabet or feature bundles.
            transitions: Transition records to inspect or transform.
            k: Locality or memory bound.
            file_sigma: Input feature-inventory path.

        Returns:
            The output produced by `o_raise_devoice_reverse`.
        """


    transitions = pre_process.transitions_gen(sigma, k, file_sigma)
    features_ids = pre_process.feature_id(file_sigma)

    if k <= 1:
        return 'k-value must be bigger than 1'


    id_voice = 0
    id_son = 0
    for i, f in features_ids.items():
        if f == 'voice':
            id_voice = i
        if f == 'son':
            id_son = i
        if f == 'cons':
            id_cons = i
        if f == 'cor':
            id_cor = i
        if f == 'cont':
            id_cont = i
        if f == 'ant':
            id_ant = i
        if f == 'dor':
            id_dor = i
        if f == 'lab':
            id_lab = i
        if f == 'distr':
            id_distr = i
        if f == 'delrel':
            id_delrel = i
        if f == 'nasal':
            id_nasal = i
        if f == 'lat':
            id_lat = i
        if f == 'high':
            id_high = i
        if f == 'back':
            id_back = i
        if f == 'low':
            id_low = i
        if f == 'tense':
            id_tense = i
        if f == 'round':
            id_round = i



    result = []
    result.append([('<<',), ('<',), len(features_ids) * [''], ('<',)])

    #o = '++--+-+-+-'
    all_feat = [id_voice, id_son, id_cons, id_nasal, id_cont, id_tense, id_round, id_low, id_back, id_high]

    for transition in transitions:
        if len(transition[0]) == 1:
            if transition[0][0] == '<<': # in << state
                continue
            elif transition[0][0] == '<': # in < states
                if transition[1][0] == '>':
                    t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
                    result.append(t)
                elif transition[1][0][id_son] == '-' and transition[1][0][id_voice] == '+': #reading D
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_voice] = '-'
                    result.append(t_copy)
                else:
                    result.append(transition)

            elif transition[0][0][id_son] == '-' and transition[0][0][id_voice] == '+': # in D state
                if transition[1][0] == '>':
                    t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
                    result.append(t)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '+'
                    t_copy[2][id_tense] = '+'
                    result.append(t_copy)
                else:
                    result.append(transition)
            elif transition[0][0][id_son] == '+' and transition[0][0][id_cons] == '+' and transition[0][0][id_nasal] == '-': # in non-nasal sonorant state
                if transition[1][0] == '>':
                    t = [transition[0], transition[1], pre_process.feat_temp(file_sigma), transition[3]]
                    result.append(t)
                elif transition[1][0] == '++-+000000-0-+--+': # reading 0
                    t_copy = copy.deepcopy(transition)
                    t_copy[2][id_high] = '+'
                    t_copy[2][id_tense] = '+'
                    result.append(t_copy)
                else:
                    result.append(transition)
            else:
                result.append(transition)
        else:
            result.append(transition)
    return result

def o_raise_devoice_seg(self, sigma):
    """Apply Polish raising and devoicing to segment transitions.

        Args:
            sigma: Input alphabet or feature bundles.

        Returns:
            The output produced by `o_raise_devoice_seg`.
        """


    # trans_corrected = self.correct_transitions(sigma)
    # features_ids = self.feature_id()
    transitions = self.transitions_gen(sigma)
    result = []
    result.append([('<<',), ('<',), [''], ('<',)])
    voiced = [('d',),  ('ʐ',), ('b',)]
    voiceless = [('t',),  ('ʂ',), ('p',)]
    nasals = [('m',), ('n',)]
    vowels = [('a',), ('ɔ',), ('ɔ̃',), ('u',)]


    # o = '++--+-+-+-'
    # all_feat = [id_voice, id_son, id_cons, id_nasal, id_cont, id_tense, id_round, id_low, id_back, id_high]

    for transition in transitions:
        if len(transition[0]) == 1:
            if transition[0][0] == '<<': # in << state
                continue
            elif transition[0][0] == '<': # in < states
                if transition[1][0] == '>':
                    t = [transition[0], transition[1], [''], transition[3]]
                    result.append(t)
                elif transition[1] == ('ɔ',): # reading 0
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1] in voiced: #reading D
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
            elif transition[0] == ('ɔ',): # in O state
                if (transition[1][0] == '>') or (transition[1] == ('ɔ',)): # > and reading 0
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(transition[0])
                    result.append(t_copy)
                elif transition[1] in voiced: #reading D
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1] not in voiced and transition[1] not in voiceless and transition[1] not in vowels and transition[1] not in nasals: #reading S
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(('ɔ',)) + list(transition[1])
                    result.append(t_copy)
            elif transition[0] in voiced: # in D state
                if transition[1][0] == '>':
                    idx_voiced = voiced.index(transition[0])
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(voiceless[idx_voiced])
                    result.append(t_copy)
                elif transition[1] == ('ɔ',): # reading 0
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(transition[0])
                    result.append(t_copy)
                elif transition[1] in voiced: #reading D
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(transition[0])
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(transition[0]) + list(transition[1])
                    result.append(t_copy)
            else: # in ELSE state
                if transition[1][0] == '>':
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1] == ('ɔ',): # reading 0
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                elif transition[1] in voiced: #reading D
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = ['']
                    result.append(t_copy)
                else:
                    t_copy = copy.deepcopy(transition)
                    if t_copy:
                        t_copy[2] = list(t_copy[2])
                    result.append(t_copy)
        elif len(transition[0]) == 2:
            new_from_state = []
            for i in transition[0]:
                new = []
                new.append(i)
                new_from_state.append(new)
            transition[0] = new_from_state
            # print(f'new state from: {new_from_state}')
            #if transition[0][0][id_voice] == '+' and transition[0][0][id_son] == '+' and transition[0][0][id_cons] == '-' and transition[0][0][id_nasal] == '-' and transition[0][0][id_cont] == '+' and transition[0][0][id_tense] == '-' and transition[0][0][id_round] == '+' and transition[0][0][id_low] == '-' and transition[0][0][id_back] == '+' and transition[0][0][id_high] == '-':
            if tuple(transition[0][0]) == ('ɔ',):
                if tuple(transition[0][1]) == ('ɔ',): # in OO states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(('ɔ',))
                        result.append(t_copy)
                    elif transition[1] == ('ɔ',): # reading 0
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(('ɔ',))
                        result.append(t_copy)
                    elif tuple(transition[1][0]) in voiced: #reading D
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    elif transition[1] not in voiced and transition[1] not in voiceless and transition[1] not in vowels and transition[1] not in nasals: #reading S
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(('ɔ',)) + list(transition[1])
                        result.append(t_copy)
                elif tuple(transition[0][1]) in voiced: # in OD states
                    if transition[1][0] == '>':
                        idx_voiced = voiced.index(tuple(transition[0][1]))
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(('u',)) + list(voiceless[idx_voiced])
                        result.append(t_copy)
                    elif transition[1] == ('ɔ',): # reading 0
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(('ɔ',)) + transition[0][1]
                        result.append(t_copy)
                    elif transition[1] in voiced: #reading D
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][0] + transition[0][1]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][0] + transition[0][1] + list(transition[1])
                        result.append(t_copy)
                elif tuple(transition[0][1]) not in voiced and tuple(transition[0][1]) not in voiceless and tuple(transition[0][1]) not in vowels and tuple(transition[0][1]) not in nasals: # in OS states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(('u',)) + transition[0][1]

                        result.append(t_copy)
                    elif transition[1] == ('ɔ',): # reading 0
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][0] + transition[0][1]
                        result.append(t_copy)
                    elif transition[1] in voiced: #reading D
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][0] + transition[0][1]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][0] + transition[0][1] + list(transition[1])
                        result.append(t_copy)
                else: # in Oelse state
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    elif transition[1] == ('ɔ',): # reading 0
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    elif transition[1] in voiced: #reading D
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(t_copy[2])
                        result.append(t_copy)
            else:
                if tuple(transition[0][1]) == ('ɔ',): # in elseO states
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        t_copy[2] = list(('ɔ',))
                        result.append(t_copy)
                    elif transition[1] == ('ɔ',): # reading 0
                        #print("reading o ", transition)
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][1]
                        result.append(t_copy)
                    elif tuple(transition[1][0]) in voiced: #reading D
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    elif transition[1] not in voiced and transition[1] not in voiceless and transition[1] not in vowels and transition[1] not in nasals: #reading S
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][1] + list(transition[1])
                        result.append(t_copy)
                elif tuple(transition[0][1]) in voiced: # in elseD states
                    if transition[1][0] == '>':
                        idx_voiced = voiced.index(tuple(transition[0][1]))
                        # print(f'idx_voiced: {idx_voiced}')
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(voiceless[idx_voiced])
                        result.append(t_copy)
                    elif transition[1] == ('ɔ',): # reading 0
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][1]
                        result.append(t_copy)
                    elif transition[1] in voiced: #reading D
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2]= transition[0][1]
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = transition[0][1] + list(transition[1])
                        result.append(t_copy)
                else: # in ELSEelse state
                    if transition[1][0] == '>':
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    elif transition[1] == ('ɔ',): # reading 0
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    elif transition[1] in voiced: #reading D
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = ['']
                        result.append(t_copy)
                    else:
                        t_copy = copy.deepcopy(transition)
                        if t_copy:
                            t_copy[2] = list(t_copy[2])
                        result.append(t_copy)
    for i in result:
        if len(i[0]) == 2:
            new_st_from = tuple(item[0] for item in i[0])
            i[0] = new_st_from

    return result
