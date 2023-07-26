# cyk-parser
```cyk-parser``` implements the Cocke–Younger–Kasami algorithm to parse a Chomsky Normal Form grammar. Loads a CNF grammar, reads in the example sentences, and for each examplesentence, outputs the following to a file:

- The sentence itself
- The simple bracket structure parse(s) based on the program's implementation of the CKY algorithm
- The number of parses for that sentence.

Args:
* ```grammar_filename```: name of the file holding grammar rules in the NLTK .cfg format in Chomsky Normal Form
* ```test_sentence_filename```: name of the file containing test sentences to parse with CKY algorithm

Returns:
* ```output_filename```: name of the file where system will write the parses and their counts over the test sentences

To run: 
```
hw3_parser.sh input/grammar_cnf.cfg input/sentences.txt output/<output_filename>
```

HW3 OF LING571 (10/25/2021)