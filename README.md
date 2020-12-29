# tense_vocab_sentence_generator
Generates sentences with needed vocabulary and grammar tense.
It works as a sript run from CMD and takes two arguments: 1) a word; 2) a tense (in form of Present_Simple, Past_Perfect_Continuous etc.)
As a result, you're gonna have a .txt file with the sentences that feature both the word and the tense.
Be sure to download the .json file as well for advanced verb search.
Enjoy!

Command example: 
$ Word_GrammarTense_Lookup.py accountant Past_Simple

(List of the featured tense names:
- Present_Simple
- Present_Continuous
- Present_Perfect
- Present_Perfect_Continuous
- Past_Simple
- Past_Continuous
- Past_Perfect
- Past_Perfect_Continuous
- Future_Simple
- Future_Continuous
- Future_Perfect
- Future_Perfect_Continuous)

Requirements:
- Python
- SpaCy
