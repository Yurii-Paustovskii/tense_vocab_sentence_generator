import requests
import json
from lxml import html
import spacy
import re
import sys
nlp = spacy.load("en_core_web_md")
def get_sents(word, tense):
    result = []                #list of sentences containing the needed word
    res = []                   #final list of word+tense filter
    forms = [word.lower()]
    word_nlp = nlp(word.lower())
    word_nlp_0 = word_nlp[0]
    if word_nlp_0.tag_ in ['VB', 'VBN', 'VBG', 'VBZ', 'VBD']:
        with open('verbs-dictionaries.json') as json_file:
            verbs_json = json.load(json_file)
            for i in verbs_json:
                if word_nlp_0.text in i:
                    forms = i

    irregular_nouns = {'child': 'children',
                       'goose': 'geese',
                       'man': 'men',
                       'woman': 'women',
                       'tooth': 'teeth',
                       'foot': 'feet',
                       'mouse': 'mice'}
    if word_nlp_0.tag_ == 'NN':
        if word_nlp_0.text in irregular_nouns.keys():
            plural = irregular_nouns[word_nlp_0.text]
            forms.append(plural)
        elif word_nlp_0.text in ['series', 'species', 'deer']:
            plural = word_nlp_0.text
            forms.append(plural)
        elif re.search(r'(x|s|ch|sh|z|o)\b', word_nlp_0.text) and not word_nlp_0.text in ['photo', 'piano', 'halo']:
            plural = word_nlp_0.text + 'es'
            forms.append(plural)
        elif re.search(r'[^aouei]y\b', word_nlp_0.text):
            plural = re.sub(r'(y)\b','ies', word_nlp_0.text)
            forms.append(plural)
        elif re.search(r'(f|fe)\b', word_nlp_0.text) and not word_nlp_0.text in ['roof', 'belief', 'chef', 'chief']:
            plural = re.sub(r'(f|fe)\b', r'ves', word_nlp_0.text)
            forms.append(plural)
        elif re.search(r'on\b', word_nlp_0.text):
            plural = re.sub(r'on\b', r'a', word_nlp_0.text)
            forms.append(plural)
        elif re.search(r'us\b', word_nlp_0.text):
            plural = re.sub(r'us\b', r'i', word_nlp_0.text)
            forms.append(plural)
        elif re.search(r'is\b', word_nlp_0.text):
            plural = re.sub(r'is\b', r'es', word_nlp_0.text)
            forms.append(plural)
        else:
            plural = word_nlp_0.text + 's'
            forms.append((plural))


    print('searching for these forms =', forms)

    for form in forms:
        web_page = requests.get('https://sentence.yourdictionary.com/' + form)
        if web_page.status_code == 200:
            tree = html.fromstring(web_page.text)
            sents = tree.xpath('//div[2]/p')
            for i in range(len(sents)):
                result.append(sents[i].text_content())
    print('in total of ',len(result), 'sentences')
    rules = {
        'Present_Simple': lambda token: token.tag_ in ['VBP', 'VBZ'] and token.dep_ == 'ROOT',
        'Present_Continuous': lambda token: re.search(r'be', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and token.text in ["'m", "'re", "'s", "am", "are", "is"] and not 'have' in [i.lemma_ for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Present_Perfect': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and not token.head.text == 'got' and token.head.tag_ == 'VBN' and not re.search(r'd', token.text) and not re.search(r'(\'d|would|might|may|could)', str([i.lemma_ for i in token.head.children])),
        'Present_Perfect_Continuous': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and not token.head.text == 'got' and token.head.tag_ == 'VBG' and not re.search(r'd', token.text),
        'Past_Simple': lambda token: token.tag_ == 'VBD' and token.dep_ == 'ROOT' or token.text in ['Did', 'did'],
        'Past_Continuous': lambda token: re.search(r'be', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and token.text in ['were', 'was'] and not 'have' in [i.lemma_ for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Past_Perfect': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBN' and not re.search(r'(s|v)', token.text),
        'Past_Perfect_Continuous': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and not re.search(r'(s|v)', token.text),
        'Future_Simple': lambda token: re.search(r'will', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBP',
        'Future_Continuous': lambda token: re.search(r'will', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and not 'have' in [i.text for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Future_Perfect': lambda token: re.search(r'will', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBN' and 'have' in [i.text for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Future_Perfect_Continuous': lambda token: re.search(r'will', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and 'have' in [i.text for i in token.head.children]
    }
    for sentence in result:
        sentence_nlp = nlp(str(sentence))
        for token in sentence_nlp:
            if rules[tense](token):
                res.append(str(sentence))
    res = list(set(res))
    if res:
        res_string = '\n'.join(res)
        with open('sents.txt', 'w', encoding='utf-8') as res_file:
            res_file.write(res_string)
        print("The sentences are in the file called 'sents.txt'. Enjoy!")
    else:
        print('Sorry, try another word, form or tense.')


if __name__ == '__main__':
    print(sys.argv)
    get_sents(sys.argv[1], sys.argv[2])

