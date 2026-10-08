import csv
from itertools import product
import itertools
import random
from . import preprocessing as pre_process
from . import rules
from .fst import FST_feature
from collections import deque
# from graphviz import Digraph
from pprint import pprint

class Sosfia:

    def __init__(self, in_out_pairs, fst, features): #in_string, extension):
        """Initialize the object from the supplied model data.

        Args:
            in_out_pairs: Training input-output examples.
            fst: Finite-state transducer providing structure.
            features: Ordered selected feature names.

        Returns:
            None.
        """
        # self.k = k
        #self.in_string = in_string
        #self.extension = extension
        self.in_out_pairs = in_out_pairs
        self.fst = fst
        self.features = features

    def feat_temp(self):
        """Create an empty output string for every active feature.

                Args:
                    None.

                Returns:
                    The output produced by `feat_temp`.
                """
        return [""] * len(self.features)

    def check_pairs(self):
        """Check whether all training pairs have processable outputs.

                Args:
                    None.

                Returns:
                    The output produced by `check_pairs`.
                """

        for i in self.in_out_pairs:
            if i[1] != 'Input impossible to process':
                continue
            else:
                return False

    def single_feats_to_mixed(self, lst_of_lists):
        """Combine separate feature values into segment-sized bundles.

                Args:
                    lst_of_lists: Feature-major sequences combined into segment bundles.

                Returns:
                    The output produced by `single_feats_to_mixed`.
                """
        result = []
        for lst in lst_of_lists:
            temp_result = []
            for i in range(len(lst[0])):
                new_string = ''.join([string[i] for string in lst])
                temp_result.append(new_string)
            result.append(temp_result)
        return result

    def lcp(self, feat_values):
        """Compute the longest common prefix of the supplied sequences.

                Args:
                    feat_values: Feature-output sequences whose common prefix is required.

                Returns:
                    The output produced by `lcp`.
                """

        # print("Calling lcp function")

        # pprint(feat_values)
        if len(feat_values) == 0:
            return ""
        current = feat_values[0] #[('+', '+'), ('+', '+'), ('+', '+')]
        #print(current)
        for i in range(1,len(feat_values)): #i=1
            # print(i)
            temp = []
            if len(current) == 0:
                break
            for j in range(len(feat_values[i])): #j=0
                # print("this is j:", j, "and this is i:", i)
#                 print("this is feat_values[i]:", feat_values[i])
#                 print("this is current[j]:", current[j], 'and this is feat_values[i][j]:', feat_values[i][j])
                if j < len(current) and current[j] == feat_values[i][j]:
                    #temp = []
                    temp.append(current[j])
                    # print("TEMP:", temp)
                else:
                    break
            current = temp
        # print(f'\n \n Returning: {current}')
        return current

    def lcp_feat(self, feat_out):
        """Compute the longest common output prefix independently per feature.

                Args:
                    feat_out: Feature-major output observations.

                Returns:
                    The output produced by `lcp_feat`.
                """

#         for i in feat_out:
#             print(i)
#         print("---------------------------------------")
#         if len(feat_out) == 0:
#             return 'Missing data'

        feats_num = len(self.features)

        all_together = []
        for i in range(feats_num):
            # print(f'feature: {self.features[i]}')
            temp_list = []
            for j in feat_out:
                temp_list.append(j[i])
            all_together.append(temp_list)

        result = []
        for lst in all_together:
            #print('\n')
            # print(f'lst: {lst}')
            #print("for lst in all_together")
            #print("And this is for loop inside the lcp_feat++++ a lst in all_together:  +++  ", lst)
            lcp_single_feat = ''.join(self.lcp(lst))
            # print('lcp_single_feat: ', lcp_single_feat)
            result.append(lcp_single_feat)
        return result

    def common_out_left_boundary(self, in_str):

        """in_str == list of lists of segments

                Args:
                    in_str: Input prefix whose output contribution is queried.

                Returns:
                    The output produced by `common_out_left_boundary`.
                """
#         if self.check_pairs() == False:
#             return 'Cannot proceed; incorrect input pairs'
#         else:
        out = []
        #not_in_data = []
        for p in self.in_out_pairs:
            if in_str == ['<']:
                out.append(p[1])

        if len(out) == 0:
            #print(f"This is the in_str we talkin abut: {in_str}")
            return None
        else:
            # print(f"COMMON OUT: of in_str: {in_str}: {self.lcp_feat(out)}")
            return self.lcp_feat(out) #---> use this when dealing with features
            # return self.lcp(out)


    def common_out(self, in_str):

        """in_str == list of lists of segments

                Args:
                    in_str: Input prefix whose output contribution is queried.

                Returns:
                    The output produced by `common_out`.
                """
#         if self.check_pairs() == False:
#             return 'Cannot proceed; incorrect input pairs'
#         else:
        out = []
        #not_in_data = []
        for p in self.in_out_pairs:
            # print("p: ", p, "\n\n")
            # print(f'in_str: {in_str}')
            # print("in_str: ", in_str)
            #print("p[0].startswith(in_str) ..............................", p[0].startswith(in_str))
#                 if p[0].startswith(in_str) == False:
#                     return 'No such data point'
            #print("pair:         ", p)
            if p[0][:len(in_str)] == in_str:
                # print(p[1])
                out.append(p[1])
#             else:
#                 not_in_data.append(in_str)
                #print("p[0][:len(in_str)]:   ", p[0][:len(in_str)])
#                 #print("in_str:   ",in_str)
#         if len(out) == 0:
#             #return 'X'
#             print(in_str)
#         else:
#             #print(f' \t\t for: {in_str} \n all the outputs are: {out}  \n and this is the lcp \n {self.lcp_feat(out)}')
        # print(f'Here is the in_str: {in_str} and here is its outputs: \n{out}')
        if len(out) == 0:
            #print(f"This is the in_str we talkin abut: {in_str}")
            return None
        else:
            # print(f"COMMON OUT: of in_str: {in_str}: {self.lcp_feat(out)}")
            return self.lcp_feat(out) #---> use this when dealing with features
            # return self.lcp(out)
#



    def subtract_substring(self, string, substring):
        """Remove the first occurrence of one substring from another.

                Args:
                    string: Source string or prefix being transformed.
                    substring: Substring removed from the source string.

                Returns:
                    The output produced by `subtract_substring`.
                """
        return string.replace(substring, "", 1)



    def min_change(self, string, extension):
        """Compute the feature output added by extending an input prefix.

                Args:
                    string: Source string or prefix being transformed.
                    extension: Next symbol appended to the current prefix.

                Returns:
                    The output produced by `min_change`.
                """

        # print("I have been called")
        # print(f'This is string: ----- {string} and this is extension ----- {extension}')
        str_copy = string.copy()
        str_copy.append(extension)
        # print(f"self.common_out({str_copy})", self.common_out(str_copy))
        # print(f"self.common_out({string})", self.common_out(string))
        if self.common_out(str_copy) == None or self.common_out(string) == None:
            # print("Extension is equal to None for:", str_copy)
            return "No data"
        result = []
        for i in range(len(self.features)):
            #print("Counting the range of self.features inside of min_change", i)
            # print("i: ", i)
            # print("self.common_out(str_copy):", self.common_out(str_copy))
            # print("self.common_out(string): ", self.common_out(string))
            x = self.common_out(str_copy)[i]
            y = self.common_out(string)[i]
            # print(f'common out of string: {string} is: {self.common_out(string)[i]}')
            # print(f'common out of extension: {str_copy} is: {self.common_out(str_copy)[i]}')
            temp_feat = self.subtract_substring(x, y)
            result.append(temp_feat)

        #print(f'min_change of {string} and {extension} is :{result}')
        return result

    def min_change_seg(self, string, extension):
        """Compute the segment output added by extending an input prefix.

                Args:
                    string: Source string or prefix being transformed.
                    extension: Next symbol appended to the current prefix.

                Returns:
                    The output produced by `min_change_seg`.
                """

        # print("I have been called")
        # print(f' \n \n This is string: ----- {string} and this is extension ----- {extension}')
        str_copy = string.copy()
        str_copy.append(extension)

        # print(f"self.common_out(string): {self.common_out(string)}")
        # print(f"self.common_out(extension): {self.common_out(str_copy)}")
        if self.common_out(str_copy) == None or self.common_out(string) == None:
            # print("Extension is equal to None for:", str_copy)
            return "No data"
        result = []
        x = self.common_out(str_copy)
        y = self.common_out(string)

        def prefix_difference(list1, list2):
            """Remove a prefix list and return the remaining suffix.

                        Args:
                            list1: Sequence from which a prefix is removed.
                            list2: Sequence tested as a possible prefix.

                        Returns:
                            The output produced by `prefix_difference`.
                        """
            if list1[:len(list2)] == list2:  # Check if list2 is a prefix of list1
                if list1[len(list2):] == []:
                    return ['']
                else:
                    return list1[len(list2):]  # Return the remaining elements
            return ['']  # Otherwise, return an empty list

        return prefix_difference(x,y)
        # print(f'This self.common_out(str_copy): {self.common_out(str_copy)} and this self.common_out(string): {self.common_out(string)}')

        #     print(x, y)
        #     print(f'common out of string: {string} is: {self.common_out(string)[i]}')
        #     print(f'common out of extension: {str_copy} is: {self.common_out(str_copy)[i]}')
        #     temp_feat = self.subtract_substring(x, y)
        #     result.append(temp_feat)

        # #print(f'min_change of {string} and {extension} is :{result}')
        # return result

    def nested_dict_trans(self):
        """Index transitions by source state and input symbol.

                Args:
                    None.

                Returns:
                    The output produced by `nested_dict_trans`.
                """

        outer_d = {}
        for state in self.fst.states:
            #print(state)
            if state == '>':
                continue
            else:
                inner_d = dict()
                for (q_in, sym, feat, q_out) in self.fst.transitions:
                    #print(t)
                    #print(q_in, sym, feat, q_out)
                    feat_q_out = (feat, q_out)
                    #print(feat_q_out)
                    if q_in == state:
                        inner_d[sym] = feat_q_out
                outer_d[state] = inner_d
        #outer_d[('<<',)] = {('<',): ([''], ('<',))} #empty trans
        return outer_d


    def fill_in_trans(self, k=None):
        """Infer feature outputs for the transducer transitions.

                Args:
                    k: Locality or memory bound.

                Returns:
                    The output produced by `fill_in_trans`.
                """

        queue = deque()
        queue.append((('<<',), ['']))
        self.fst.mark_state(('<<',))
        # print(self.fst.is_marked(('<<',)))
        # self.fst.in_alphabet.remove(['<<',])


        # empty_trans = self.fst.transitions

        priority_element = ['<']



        # q = list(product(['<<'], repeat=1))[0]
        # w = [['']]
        # queue = []
        # queue.append((q,w))
        # print(f"queue at start: {queue}")
        #new_transitions = []
        empty_trans = self.fst.transitions
        # for i,j in self.nested_dict_trans().items():
        #     print(i,j)
        # x = 50
        while queue:
        # while x >= 1:
            # print(f'list: {list(queue)}')
            current_state, prefix = queue.popleft()
            # print("************************************************ NEW CURRENT STATE *******************************")
            # print("current state: ", current_state) #, type(current_state), "prefix: ", prefix, type(prefix))


            for symbol in sorted(self.fst.in_alphabet, key=lambda x: (x != priority_element, x)):
                # print(type([list(product(symbol, repeat=1))[0]]))
                # print(f"--------------SYMBOL-------------- {symbol}")

                for transition in self.fst.transitions:
                    # if transition[0] == ('00000-0+--------+-----+-', '----++--++00-+0000000000'):
                    # print(f"!!!!! transition: !!!! {transition} \n")
                    # print(f"@@@@@ current_state: {current_state} \n")
                    #     print(f"$$$$$$$$$. symbol: {symbol} \n")
                    # print(f"%%%%%%%%%transition: {transition}")
                    # if list(product(current_state, repeat=1))[0] == transition[0] and list(product(symbol, repeat=1))[0] == transition[1]:
                    if current_state == transition[0] and list(product(symbol, repeat=1))[0] == transition[1]:
                        # print("                 ||               ")
                        # print("                 ||               ")
                        # print("                 ||               ")
                        # print(f"current_state:  {current_state}")
                        # print(f"transition[0]:  {transition[0]}")
                        # print(f"list(product(symbol, repeat=1))[0]: {list(product(symbol, repeat=1))[0]}")
                        # print(f"transition[1]:  {transition[1]}")
                        # print(f"CONDITION MET IN: {transition}")
                        # if current_state== ('00000-0+--------+-----+-', '00000-0++-0-++--++------'):
                        #     print(list(product(current_state, repeat=1))[0])

                        #     print(transition[0])
                        # print(f'this my transition {transition}')
                        # print(self.nested_dict_trans())

                        # print(f'MIGHT BE a problem: {self.nested_dict_trans().get(current_state)}')
                        if len(self.nested_dict_trans().get(current_state)) > 1:
                            if self.min_change(prefix, list(product(symbol, repeat=1))[0]) == 'No data':
                                # print('NO \n\n\n\n DATA')
                                continue
                            else:
                                transition[2] = self.min_change(prefix, list(product(symbol, repeat=1))[0])
                            # print("\n ")
                            # if transition[0] == ('00000-0+--------+-----+-', '----++--++00-+0000000000'):
                            # print(f"after change:           {transition}")
                            if not self.fst.is_marked(transition[3]):
                                self.fst.mark_state(transition[3])
                                # print(f"MORE THAN ! trsnd: Now appending state: {transition[3]} and prefix: {prefix+symbol}")
                                # print(f"like this: {(transition[3], prefix+[(x,) for x in symbol if x])}")
                                queue.append((transition[3], prefix+[(x,) for x in symbol if x]))
                            # if self.k == 1:
                            #     if (transition[3], prefix+[(x,) for x in symbol if x]) not in list(queue):
                            #         queue.append((transition[3], prefix+[(x,) for x in symbol if x]))
                        else:
                            # print(f"JUST ONE OUTGOING TRANSITION FROM {current_state}")
                            # print(f'current_state: {current_state}, symbol: {symbol}')
                            if current_state == ('<<',) and symbol == ['<']:
                                # print('WE GOT the one')
                                # print(f'common_out("<",): {self.common_out_left_boundary(symbol)}')
                                transition[2] = self.common_out_left_boundary(symbol)
                            # transition[2] = self.feat_temp()

                            # print(f"after change:           {transition}")
                            if not self.fst.is_marked(transition[3]):
                                # print(f"&&&&&&&&&&&&&&&&&&&&&&&&& {transition[3]} not marked")
                                self.fst.mark_state(transition[3])
                                # print(f"JUST ONE TRSNS: Now appending state: {transition[3]} and prefix: {prefix+symbol}")
                                # print(f"like this: {(transition[3], [(x,) for x in prefix+symbol if x])}")
                                queue.append((transition[3], [(x,) for x in prefix+symbol if x]))
                                # print(f"out state {transition[3]} not in marked states")
        #     print(f"QUEUE: ")
        #     for i in queue:
        #         print(i)
        #     # x -= 1
        #     # print(x)
        # print("STOPS")
            # break

        # for i in self.fst.transitions:
        #     if i[0] == ('<',):
        #         if i[1] == ('>',):
        #             i[2] = self.feat_temp()
        # # for i in self.fst.transitions:
        #     print(i)

        return self.fst.transitions


    def fill_in_trans_seg(self):
        """Infer segment outputs for the transducer transitions.

                Args:
                    None.

                Returns:
                    The output produced by `fill_in_trans_seg`.
                """

        queue = deque()
        queue.append((('<<',), ['']))
        self.fst.mark_state(('<<',))
        # print(self.fst.is_marked(('<<',)))
        # self.fst.in_alphabet.remove(['<<',])


        # empty_trans = self.fst.transitions

        priority_element = ['<']

        #new_transitions = []
        empty_trans = self.fst.transitions
        # for i,j in self.nested_dict_trans().items():
        #     print(i,j)
        # x = 50
        while queue:
        # while x >= 1:
            current_state, prefix = queue.popleft()
            # print("************************************************ NEW CURRENT STATE *******************************")
            # print("current state: ", current_state) #, type(current_state), "prefix: ", prefix, type(prefix))


            for symbol in sorted(self.fst.in_alphabet, key=lambda x: (x != priority_element, x)):
                # print(type([list(product(symbol, repeat=1))[0]]))
                # print(f"--------------SYMBOL-------------- {symbol}")

                for transition in self.fst.transitions:
                    # print(f'transition: {transition}')
                    if current_state == transition[0] and list(product(symbol, repeat=1))[0] == transition[1]:

                        if len(self.nested_dict_trans().get(current_state)) > 1: # more than one transitions
                            if self.min_change_seg(prefix, list(product(symbol, repeat=1))[0]) == 'No data':
                                # transition[2] == 'Houston we gotta problem'
                                continue
                            else:
                                transition[2] = self.min_change_seg(prefix, list(product(symbol, repeat=1))[0])
                            # print("\n ")
                            # if transition[0] == ('00000-0+--------+-----+-', '----++--++00-+0000000000'):
                            # print(f"after change:           {transition}")
                            if not self.fst.is_marked(transition[3]):
                                self.fst.mark_state(transition[3])
                                # print(f"MORE THAN ! trsnd: Now appending state: {transition[3]} and prefix: {prefix+symbol}")
                                queue.append((transition[3], prefix+[(x,) for x in symbol if x]))
                        else:
                            # print(f"JUST ONE OUTGOING TRANSITION FROM {current_state}")
                            transition[2] = ['']
                            # print(f"after change:           {transition}")
                            if not self.fst.is_marked(transition[3]):
                                # print(f"&&&&&&&&&&&&&&&&&&&&&&&&& {transition[3]} not marked")
                                self.fst.mark_state(transition[3])
                                # print(f"JUST ONE TRSNS: Now appending state: {transition[3]} and prefix: {prefix+symbol}")
                                queue.append((transition[3], [(x,) for x in prefix+symbol if x]))
                                # print(f"out state {transition[3]} not in marked states")

        # for i in self.fst.transitions:
        #     if i[0] == ('<',):
        #         if i[1] == ('>',):
        #             i[2] = ['']


        return self.fst.transitions


def train_data_prod(t, k, features):

    """returns ngrams up until k+1

        Args:
            t: Transition record or sequence element.
            k: Locality or memory bound.
            features: Ordered selected feature names.

        Returns:
            The output produced by `train_data_prod`.
        """
    output =[]
    x = k + 1
    while x >= 1:
        temp_l = t.gen_pairs_prod(data.ngrams_prod(x, features))
        for i in temp_l:
            output.append(i)
        x -= 1
    return output

def check_the_difference(transitions, sosfia_output):

    """checks the sosfia output agains the original machine

        Args:
            transitions: Transition records to inspect or transform.
            sosfia_output: Transitions inferred by SOSFIA.

        Returns:
            The output produced by `check_the_difference`.
        """

    if len(transitions) == len(sosfia_output):
        unmatched_pairs = []
        for i in transitions:
            for j in sosfia_output:
                if (i[0], i[1]) == (j[0], j[1]):
                    if i[2] == j[2]:
                        continue

                    elif i[2] == [''] and j[2] == []:
                        continue
                    else:
                        unmatched_pairs.append(["gold: ", i, "SOSFIA", j])
        if len(unmatched_pairs) > 0:
#             for pair in unmatched_pairs:
#                 if type(pair[2][0]) == list:
#                     return "Sample not functional! Add more features!"
                    return unmatched_pairs
        else:
            return "It's a match"
    else:
        #print("gold t: ", len(transitions),"sosfia: ", len(sosfia_output))
        return "Transitions are of different length"


#print(temp_train[:10])
def convert_data(file_data):
    """Parse literal-valued input-output pairs from a TSV file.

        Args:
            file_data: Path to a pair-data file.

        Returns:
            The output produced by `convert_data`.
        """

    temp_train = []
    with open(file_data, newline='') as csvfile:
        pairs = csv.reader(csvfile, delimiter='\t')
        for pair in pairs:
            temp_train.append(pair)
    result = []
    for entry in temp_train[1:]:
        # print(f'entry:      {entry}')
        inner_list = []
        for item in entry:
            # print(f'item:                       {item}')
            # print(f'eval_item:                                      {eval(item)}')
            inner_list.append(eval(item))
        result.append(tuple(inner_list))
    return result



def extract_feat_pairs(features, feature_ids, gen_pairs, k=None):

    """extracts training data given the feature(s)

        input: features (list of feature/es), feature_ids (dict)), ngrams (list of lists of tuples)
        output: list of tuples of lists, where first list is UR grouped by segments, and the second is SR feature bundles grouped by feature,
                e.g. [[[('<',), ('-',), ('-',), ('>',)], ['--']], [[('<',), ('-',), ('+',), ('>',)], ['-+']], ...]

        Args:
            features: Ordered selected feature names.
            feature_ids: Mapping from feature indexes to names.
            gen_pairs: Input-output examples.
            k: Locality or memory bound.

        Returns:
            The output produced by `extract_feat_pairs`.
        """


    feat_data = []
    if len(features) == 1:
        feat_id = 0

        for key,v in feature_ids.items():
            if features[0] == v:
                feat_id = key
        feat_data = []
        for pair in gen_pairs:
            word_in = pair[0]
            word_out = pair[1]
            temp_feat_in = []
            temp_feat_out = []
            temp_feat_in.append(list(product(['<'], repeat=1))[0])
            for i in word_in:
                if i[0] == '>' or i[0] == '<':
                    continue
                else:
                    feat_in = i[0][feat_id]
                    temp_feat_in.append(list(product([feat_in], repeat=1))[0])
            temp_feat_in.append(list(product(['>'], repeat=1))[0])
            temp_feat_out.append(word_out[feat_id])
            feat_data.append([temp_feat_in, temp_feat_out])
    else:
        feat_id = []

        for feature in features:
            for key,v in feature_ids.items():
                if feature == v:
                    feat_id.append(key)


        for pair in gen_pairs:

            word_in = pair[0]
            word_out = pair[1]
            temp_feats_in = []
            temp_feats_out = []
            temp_feats_in.append(list(product(['<'], repeat=1))[0])
            for i in word_in:
                if i[0] == '>' or i[0] == '<':
                    continue
                else:
                    temp_bundle = ''
                    for f_id in feat_id:
                        temp_bundle += i[0][f_id]
                    temp_feats_in.append(list(product([temp_bundle], repeat=1))[0])
            temp_feats_in.append(list(product(['>'], repeat=1))[0])
            for f_id in feat_id:
                temp_feats_out.append(word_out[f_id])
            feat_data.append([temp_feats_in, temp_feats_out])

    result = []
    for i in feat_data:
        if i not in result:
            result.append(i)
        else:
            continue
    # return result


    ######## -use below if learning from fake data- #########
    if k:
        updated_res = []
        # print(f'we got some k: {k} ')
        if k == 1:
            # print('k is actually 1')
            length = 1
        else:

            length = (2*k) -1
        # print(f'len: {length}')
        for pair in result:
            if len(pair[0])-2 <= length:
                # print(pair)
                updated_res.append(pair)
        return updated_res
    else:
        return result

def check_if_functional(transitions):
    """Check whether each input has exactly one observed output.

        Args:
            transitions: Transition records to inspect or transform.

        Returns:
            The output produced by `check_if_functional`.
        """

    for trans in transitions:
        if type(trans[2][0]) == list:
            return "Add another feature"

def is_functional(pairs):

    """input: list of input-output pairs
        output: Bool

        checks if for every input there is exactly one output

        Args:
            pairs: Input-output examples.

        Returns:
            The output produced by `is_functional`.
        """

    input_output_map = {}

    for pair in pairs:
        input_sequence, output_sequence = pair

        # Convert input_sequence to a tuple to make it hashable
        input_key = tuple(input_sequence)

        # Check if this input already has an output
        if input_key in input_output_map:
            if input_output_map[input_key] != output_sequence:
                # If a different output is found for the same input, it's not functional
                return False
        else:
            # Store the output for the first occurrence of the input
            input_output_map[input_key] = output_sequence

    return True



def adjust_train(train, k):
    """Add boundary symbols to training inputs that lack them.

        Args:
            train: Training examples used to build a hypothesis.
            k: Locality or memory bound.

        Returns:
            The output produced by `adjust_train`.
        """

    adjusted_train = []
    size = k + 1
    for i in train:
        #print(i)
        if len(i[1][0]) <= size:
            adjusted_train.append(i)
    return adjusted_train




def all_shortest_paths_fst(FST, start_state, target_state):
    """
    Finds all shortest paths from start_state to target_state in a finite-state transducer (FST),
    requiring at least one transition even if the start and target states are the same.

    Args:
        FST: Transducer whose nested transition map is searched.
        start_state: State where each path begins.
        target_state: State each returned path must reach.

    Returns:
        All shortest input-symbol paths from the start state to the target state.
    """
    # Queue for BFS: (current_state, path_so_far)
    fst = FST.nested_dict_trans()
    queue = deque([(start_state, [])])
    shortest_paths = []
    shortest_distance = float('inf')  # Minimum distance found so far
    visited = {}  # Track visited states with their shortest path length

    while queue:
        # print(f'QUEUE right after while: {queue}')
        current_state, symbol_path = queue.popleft()
        # print(f'This is current_state: {current_state} and this is symbol_path: {symbol_path}')
        # Check if we've reached the target state with at least one transition
        if current_state == target_state and len(symbol_path) > 0:
            if len(symbol_path) < shortest_distance:
                shortest_paths = [symbol_path]
                shortest_distance = len(symbol_path)
            elif len(symbol_path) == shortest_distance:
                shortest_paths.append(symbol_path)
            continue

        # Stop exploring paths longer than the shortest found so far
        if len(symbol_path) >= shortest_distance:
            continue

        # Explore outgoing transitions
        for symbol, (output_list, next_state) in fst.get(current_state, {}).items():
            new_symbol_path = symbol_path + [symbol]

            # Allow revisiting the target state, but prevent infinite loops elsewhere
            if (next_state not in visited or len(new_symbol_path) < visited[next_state]) or next_state == target_state:
                visited[next_state] = len(new_symbol_path)
                queue.append((next_state, new_symbol_path))


    return shortest_paths

def reduced_sufficient_sample(FST, training_data):

    """e.g.
            Now we are at transition:
        [('<',), ('i:',), [''], ('i:',)]

        STATE:  ('o', 'o')
        Aaaaaand the shortest string is:
        [[('o',), ('o',)]]

        [[('o',), ('o',)]]
        The full string is:               [('<',), ('i:',), ('o',), ('o',)]

        Args:
            FST: Gold or structural feature transducer used for learning and evaluation.
            training_data: Complete training pairs in the active representation.

        Returns:
            The output produced by `reduced_sufficient_sample`.
        """

    strings = []
    for transition in FST.transitions:
        print("---------------------------------------------")
        print("Now we are at transition:")
        print(transition, '\n')
        for state in FST.states:
            string = []
            if len(state) >= len(transition[3]):
                print("STATE: ", state)
                print("Aaaaaand the shortest string is:")
                # print(all_shortest_paths_fst(FST, transition[3], state), '\n')
                if all_shortest_paths_fst(FST, transition[3], state) == [] or all_shortest_paths_fst(FST, transition[3], state)[0] == [('>',)]:
                    continue
                else:
                    # print(transition[0], transition[1])
                    if len(transition[0]) > 1:
                        for i in transition[0]:
                            string.append((i,))
                    else:
                        if transition[0] != ('<<',):
                            string.append(transition[0])
                    string.append(transition[1])
                    if len(all_shortest_paths_fst(FST, transition[3], state)[0]) > 1:
                        for i in all_shortest_paths_fst(FST, transition[3], state)[0]:
                            string.append(i)
                    else:
                        string.append(all_shortest_paths_fst(FST, transition[3], state)[0][0])
                    if string[0] != ('<',):
                        string.insert(0, ('<',))
                    print(f'\n\n\nAll shortests paths from {transition[3]} to {state}')
                    print(all_shortest_paths_fst(FST, transition[3], state))

                    string.append(('>',))
                    print("\n\nThe full string is:              ", string )
                    if string not in strings:
                        strings.append(string)
    updated_data = []
    # not_need = []
    for i in training_data:
        if i[0] in strings:
            updated_data.append(i)
        # else:
        #     not_need.append(i)

    return updated_data




def visualize_fst(fst, start_state, accept_states):

    """start state: tuple()
        accept_states: list of tuples
        fst: FST.nested_dict_trans()
        e.g.
            dot = visualize_fst(FST.nested_dict_trans(), ('<<',), [('>',)])
            dot.render('fst_horizontal', format='png', view=True)

        Args:
            fst: Finite-state transducer providing structure.
            start_state: Initial state used when processing the input.
            accept_states: States treated as accepting during evaluation.

        Returns:
            The output produced by `visualize_fst`.
        """
    dot = Digraph()

    # Adjust graph for horizontal symmetry
    dot.attr(rankdir='LR', nodesep='0.5', ranksep='0.2')  # More horizontal space

    # Invisible start node for alignment
    dot.node('START', shape='point')
    dot.edge('START', str(start_state), label='')

    # Mark start and accept states
    dot.node(str(start_state), shape='circle', style='bold')
    for accept in accept_states:
        dot.node(str(accept), shape='doublecircle')

    # # Force specific states to be centered
    # with dot.subgraph() as center:
    #     center.attr(rank='same')
    #     center.node(str(('a',)))
    #     center.node(str(('m',)))
    #     center.node(str(('t',)))

    # Add transitions with ":" format
    for state, transitions in fst.items():
        for symbol, (output, next_state) in transitions.items():
            label = f"{symbol[0]} : {''.join(output)}"
            dot.edge(str(state), str(next_state), label=label)

    return dot
