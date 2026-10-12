"""Feature-transducer operations used by FxF and SEAL."""

from __future__ import annotations
from itertools import product
from typing import Any, Dict, Hashable, List, Sequence, Tuple, Union
from . import preprocessing as pre_process


class FST_feature:
    """Finite-state transducer with feature-coded inputs and outputs."""

    def __init__(
        self,
        states: Sequence[Hashable],
        in_alphabet: Sequence[Sequence[str]],
        out_alphabet: Sequence[Sequence[str]],
        initial: Hashable,
        finals: Sequence[Hashable],
        transitions: Sequence[Sequence[Any]],
        feature: Sequence[str],
    ) -> None:
        """Initialize a deterministic feature transducer.

        Args:
            states: Transducer states.
            in_alphabet: Tuple-wrapped input symbols.
            out_alphabet: Tuple-wrapped output symbols.
            initial: Initial state identifier.
            finals: Final state identifier or identifiers.
            transitions: Source, input, output, and destination records.
            feature: Ordered features represented by the machine.

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
        self._nested_trans_cache = None

    def nested_dict_trans(self) -> Dict[Hashable, Dict[Hashable, Tuple[Any, Hashable]]]:
        """Index transitions by source state and input symbol.

        Return a nested mapping whose innermost value is the output and
        destination state for a transition.

        Args:
            None.

        Returns:
            Source states mapped to input symbols and output/destination pairs.
        """
        if self._nested_trans_cache is not None:
            return self._nested_trans_cache
        
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
        self._nested_trans_cache = outer_d
        return outer_d

    def process_input_feature_prod(
        self, sequence: Sequence[Sequence[str]]
    ) -> Union[List[str], str]:
        """Process a feature input and concatenate transition outputs.

        Args:
            sequence: Boundary-marked tuple-wrapped feature symbols.

        Returns:
            Output strings grouped by feature, or an input-format error string
            when the right boundary is missing.
        """

        q = list(product(['<<'], repeat=1))[0]
        # pprint(sequence)
        # print('STATE:')
        # print(q)
        output_f = []
        concat = lambda x,y: x+y
        if sequence[-1][0] == '>':
            for seg in sequence:
                out_state = self.nested_dict_trans().get(q).get(seg)
                q = out_state[1]
                out = out_state[0]
                # print("This is seg:", seg)
                # print("out_state: ", out_state)
                # print("This is next state:", q)
                # print("This is output:", out)
                output_f.append(out)
        else:
            return 'Incorrect input; must end with ">"'
        
        # print("This is output_f: ", output_f)

        result = pre_process.concat_feat(output_f)
        return result

    def process_encoded_output(
        self, sequence: Sequence[Sequence[str]]
    ) -> Union[List[Any], str]:
        """Process an input through a placeholder-labeled transducer.

        Args:
            sequence: Boundary-marked tuple-wrapped feature symbols.

        Returns:
            Nonempty placeholder outputs in path order, or an input-format
            error string when the right boundary is missing.
        """
        # print(self.states)
        # print('sequence: ', sequence)
        # pprint(self.nested_dict_trans())
        q = list(product(['<<'], repeat=1))[0]
        # print(f'q: {q}')
        output_f = []
        concat = lambda x,y: x+y
        if sequence[-1][0] == '>':
            for seg in sequence:
                # print("This is seg:", seg)
                out_state = self.nested_dict_trans().get(q).get(seg)
                if out_state is None:
                    raise KeyError(
                        f"Missing transition.\n"
                        f"  current_state={q!r}\n"
                        f"  next_symbol={seg!r} (type={type(seg)})\n"
                        f"  (Hint: check '<' vs ('<',) and overall token types.)\n"
                    )

                # print("out_state: ", out_state)
                q = out_state[1]
                # print("q: ", q)
                # print("This is next state:", q)
                out = [out_state[0]]
                # print("This is output:", out)
                output_f += out
                #print(features_dict)
        else:
            return 'Incorrect input; must end with ">"'
        
        # print("This is output_f: ", output_f)

        return [x for x in output_f if x]

    def gen_encoded_pairs(
        self, feat_pairs: Sequence[Sequence[Any]]
    ) -> List[Tuple[Union[List[Any], str], Any]]:
        """Turn projected examples into placeholder string equations.

        Args:
            feat_pairs: Projected input paths and target output strings.

        Returns:
            Encoded placeholder paths paired with their target strings.
        """
        
        pairs = []
        for pair in feat_pairs:
            # print('pair: ', pair)
            inpt = pair[0]
            outpt = pair[1]
            out_feat = self.process_encoded_output(inpt)
            pairs.append((out_feat, outpt))
        return pairs
