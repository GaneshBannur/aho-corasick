from collections import defaultdict, deque

class node:
    def __init__(self):
        self.transitions: dict[str, node] = dict()
        self.word: str = None
        self.failure_link: node = None
        self.dictionary_link: node|None = None
        self.pattern_ending: bool = False
    
    def set_failure_link(self, root: 'node'):
        suffixes = [self.word[i:] for i in range(1, len(self.word)+1)]
        for suffix in suffixes:
            cur_node = root
            for letter in suffix:
                cur_node = cur_node.transitions.get(letter)
                if cur_node is None:
                    break
            else:
                self.failure_link = cur_node
                break
    
    def set_dictionary_link(self, root: 'node'):
        cur_node = self
        while cur_node is not root:
            cur_node = cur_node.failure_link
            if cur_node.pattern_ending:
                self.dictionary_link = cur_node
                break

class automaton:
    '''Allows building aho-corasick automaton for a set of patterns.
       Doesn't allow adding a pattern to a built automaton.'''

    def __init__(self):
        self.root: node = None
        self.case_sensitive: bool = False
        self.patterns: list[str] = None

    def build_automaton(self, patterns: list[str], case_sensitive=False):
        if not case_sensitive:
            patterns = [pattern.casefold() for pattern in patterns]
        self.case_sensitive = case_sensitive
        self.patterns = patterns
        root = node()
        for pattern in patterns:
            cur_node = root
            for idx, symbol in enumerate(pattern):
                next = cur_node.transitions.get(symbol)
                if next is None:
                    temp = node()
                    temp.word = pattern[:idx+1]
                    cur_node.transitions[symbol] = temp
                    next = temp
                cur_node = next
            cur_node.pattern_ending = True
        self.root = root
        root.failure_link = root
        self.traverse_and_set_failure()
        self.traverse_and_set_dictionary()
    
    def traverse_and_set_failure(self):
        '''traversal of trie using bfs'''

        bfs_q: deque[node] = deque()
        bfs_q.appendleft(self.root)

        while bfs_q:
            parent = bfs_q.pop()

            for transition_symbol, child in parent.transitions.items():
                bfs_q.appendleft(child)

                '''set failure link'''
                cur_node = parent.failure_link
                while cur_node is not self.root:
                    next = cur_node.transitions.get(transition_symbol)
                    if next is None:
                        cur_node = cur_node.failure_link
                    else:
                        child.failure_link = next
                        break
                else:
                    child.set_failure_link(self.root)

    def traverse_and_set_dictionary(self):
        '''traversal of trie using bfs'''

        bfs_q: deque[node] = deque()
        bfs_q.appendleft(self.root)

        while bfs_q:
            parent = bfs_q.pop()

            parent.set_dictionary_link(self.root)

            for child in parent.transitions.values():
                bfs_q.appendleft(child)

    def find(self, text: str):
        cur_node = self.root
        matches = defaultdict(list)
        text_len = len(text)
        if not self.case_sensitive:
            text = text.casefold()
        for idx in range(text_len+1):
            if cur_node.pattern_ending:
                matches[cur_node.word].append(idx-len(cur_node.word))
            next = cur_node.dictionary_link
            while next is not None:
                matches[next.word].append(idx-len(next.word))
                next = next.dictionary_link
            if idx > text_len-1:
                break
            symbol = text[idx]
            next = cur_node.transitions.get(symbol)
            while next is None:
                next = cur_node.failure_link
                cur_node = next
                next = cur_node.transitions.get(symbol)
                if cur_node is self.root and next is None:
                    next = self.root
                    break
            cur_node = next
        
        return matches

    def traverse(self, root=None):
        if root is None:
            root = self.root
        print(root,
              "Transitions: ", root.transitions,
              "Failure link: ", root.failure_link,
              "Dictionary link: ", root.dictionary_link,
              "Word: ", root.word,
              "End of pattern: ", root.pattern_ending)
        for next in root.transitions.values():
            self.traverse(next)

def main(patterns, text):
    automaton_1 = automaton()
    automaton_1.build_automaton(patterns)
    matches = automaton_1.find(text)
    print(matches)

if __name__=="__main__":
    patterns = []
    print("Enter number of patterns")
    n = int(input())
    print("Enter patterns")
    for i in range(n):
        patterns.append(input())
    print("Enter text")
    text = input()
    main(patterns, text)