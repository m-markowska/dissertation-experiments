import csv
from itertools import product
import itertools
import random
from . import preprocessing as pre_process
from . import rules
from pprint import pprint

class FST_feature:

    def __init__(self, states, in_alphabet, out_alphabet, initial, finals, transitions, feature):
        """Initialize the object from the supplied model data.

        Args:
            states: Finite-state transducer states.
            in_alphabet: Transducer input alphabet.
            out_alphabet: Transducer output alphabet.
            initial: Initial transducer state.
            finals: Accepting transducer state or states.
            transitions: Transition records to inspect or transform.
            feature: Active feature names.

        Returns:
            None.
        """
        #super().__init__()

        self.states = states
        self.in_alphabet = in_alphabet
        self.out_alphabet = out_alphabet
        self.initial = initial
        self.finals = finals
        self.transitions = transitions
        self.feature = feature #list of feature(s)
        self.marked_states = set()


    def mark_state(self, state):
        """Mark a state as visited.

        Args:
            state: Transducer state.

        Returns:
            None.
        """
        self.marked_states.add(state)

    def is_marked(self, state):
        """Check if a state is marked.

                Args:
                    state: Transducer state.

                Returns:
                    The output produced by `is_marked`.
                """
        return state in self.marked_states



    def nested_dict_trans(self):
        """Index transitions by source state and input symbol.

                Args:
                    None.

                Returns:
                    The output produced by `nested_dict_trans`.
                """

        outer_d = {}
        for state in self.states:
            #print(state)
            if state == '>':
                continue
            else:
                inner_d = dict()
                for (q_in, sym, feat, q_out) in self.transitions:
                    feat_q_out = (feat, q_out)
                    #print(feat_q_out)
                    if q_in == state:
                        inner_d[sym] = feat_q_out
                outer_d[state] = inner_d

        #outer_d['<<'] = {'<': ('', '<')} #empty trans
        return outer_d


    def process_input_feature_prod(self, sequence):

        """returns SR given UR
                input: a list of tuples of segments represented with features, e.g. [('<',), ('--++',), ('++0+',), ('>',)]
                output: list of strings of features grouped by feature, e.g. ['++', '-+', '+0', '++']

                Args:
                    sequence: Ordered symbols or values being processed.

                Returns:
                    The output produced by `process_input_feature_prod`.
                """

        q = list(product(['<<'], repeat=1))[0]
        # pprint(sequence)
        # print('STATE:')
        # print(q)
        output_f = []
        concat = lambda x,y: x+y
        if sequence[-1][0] == '>':
            for seg in sequence:
                # print("This is seg:", seg)
                out_state = self.nested_dict_trans().get(q).get(seg)
                # print("out_state: ", out_state)
                q = out_state[1]
                # print("q: ", q)
                # print("This is next state:", q)
                out = out_state[0]
                # print("This is output:", out)
                output_f.append(out)
                #print(features_dict)
        else:
            return 'Incorrect input; must end with ">"'

        # print("This is output_f: ", output_f)

        result = pre_process.concat_feat(output_f)
        return result

    def process_input_feature_seg(self, sequence):

        """returns SR given UR
                input: a list of tuples of segments represented with features, e.g. [('<',), ('--++',), ('++0+',), ('>',)]
                output: list of strings of features grouped by feature, e.g. ['++', '-+', '+0', '++']

                Args:
                    sequence: Ordered symbols or values being processed.

                Returns:
                    The output produced by `process_input_feature_seg`.
                """

        q = list(product(['<<'], repeat=1))[0]
        # print(f'q: {q}')
        output_f = []
        concat = lambda x,y: x+y
        if sequence[-1][0] == '>':
            for seg in sequence:
                # print("This is seg:", seg)
                out_state = self.nested_dict_trans().get(q).get(seg)
                # print("out_state: ", out_state)
                q = out_state[1]
                # print("q: ", q)
                # print("This is next state:", q)
                out = out_state[0]
                # print("This is output:", out)
                output_f += out
                #print(features_dict)
        else:
            return 'Incorrect input; must end with ">"'

        # print("This is output_f: ", output_f)

        return [x for x in output_f if x]



    def gen_pairs(self, grams):

        """generates in--out pairs for training;  all features together

                input: list of lists grouped by segments, e.g. [[('<',), ('---+',), ('---+',), ('>',)], ...]
                output: list of tuples of lists, where first list is UR grouped by segments, and the second is SR feature bundles grouped by feature,
                        e.g. [([('<',), ('---+',), ('++0+',), ('>',)], ['++-', '-+', '-0', '++']), ... ]

                Args:
                    grams: Input n-grams used to generate examples.

                Returns:
                    The output produced by `gen_pairs`.
                """

        pairs = []
        for gram in grams:
            # print(gram)
            out_feat = self.process_input_feature_prod(gram)
            pairs.append((gram, out_feat))
        return pairs


    def gen_pairs_seg(self, grams):

        """generates in--out pairs for training;  all features together

                input: list of lists grouped by segments, e.g. [[('<',), ('---+',), ('---+',), ('>',)], ...]
                output: list of tuples of lists, where first list is UR grouped by segments, and the second is SR feature bundles grouped by feature,
                        e.g. [([('<',), ('---+',), ('++0+',), ('>',)], ['++-', '-+', '-0', '++']), ... ]

                Args:
                    grams: Input n-grams used to generate examples.

                Returns:
                    The output produced by `gen_pairs_seg`.
                """

        pairs = []
        for gram in grams:
            # print(gram)
            out_feat = self.process_input_feature_seg(gram)
            pairs.append((gram, out_feat))
        return pairs


    def extract_feat_pairs(self, features, feature_ids, gen_pairs):

        """extracts training data given the feature(s)

                input: features (list of feature/es), feature_ids (dict)), ngrams (list of lists of tuples)
                output: list of tuples of lists, where first list is UR grouped by segments, and the second is SR feature bundles grouped by feature,
                        e.g. [[[('<',), ('-',), ('-',), ('>',)], ['--']], [[('<',), ('-',), ('+',), ('>',)], ['-+']], ...]

                Args:
                    features: Ordered selected feature names.
                    feature_ids: Mapping from feature indexes to names.
                    gen_pairs: Input-output examples.

                Returns:
                    The output produced by `extract_feat_pairs`.
                """

        #gen_pairs = self.gen_pairs(ngrams)
        feat_data = []
        if len(features) == 1:
            feat_id = 0

            for k,v in feature_ids.items():
                if features[0] == v:
                    feat_id = k
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
                for k,v in feature_ids.items():
                    if feature == v:
                        feat_id.append(k)


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

        return result

    def clear_trans_output(self):

        """returns transitions with empty lists as outputs

                output: list of lists of transitions, e.g. [[('---+',), ('---+',), [], ('---+',)], ...]

                Args:
                    None.

                Returns:
                    The output produced by `clear_trans_output`.
                """

        #print(self.transitions)
        output = []
        for transition in self.transitions:
            transition = [transition[0], transition[1], [], transition[3]]
            output.append(transition)
        return output

    def identity_trans(self, mode='feat'):
        """identity trans.

                Args:
                    mode: Requested representation or learning mode.

                Returns:
                    The output produced by `identity_trans`.
                """

        output = []
        for transition in self.transitions:
            # print(transition)
            state_in = transition[0]
            reading = transition[1]
            out = transition[2]
            state_to = transition[3]
            new_out = []
            if reading != ('>',):
                for i in reading[0]:
                    new_out.append(i)
                new_transition = [state_in, reading, new_out, state_to]
                output.append(new_transition)
            else:
                if mode == 'seg':
                    new_transition = [state_in, reading, [''], state_to]
                else:
                    new_transition = [state_in, reading, [""] * len(self.feature), state_to]
                output.append(new_transition)
        return output
