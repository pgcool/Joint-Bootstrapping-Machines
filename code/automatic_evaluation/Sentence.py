#!/usr/bin/env python
# -*- coding: utf-8 -*-


# description: Extract entities info, clean and filter


import re
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.data import load

# tokens between entities which do not represent relationships
bad_tokens = [",", "(", ")", ";", "''",  "``", "'s", "-", "vs.", "v", "'", ":",
              ".", "--"]
stopwords = stopwords.words('english')
not_valid = bad_tokens + stopwords

regex_clean_simple = re.compile('</?[A-Z]+>', re.U)
regex_simple = re.compile('<[A-Z]+>[^<]+</[A-Z]+>', re.U)

def tokenize_entity(entity):
    parts = word_tokenize(entity)
    if parts[-1] == '.':
        replace = parts[-2] + parts[-1]
        del parts[-1]
        del parts[-1]
        parts.append(replace)
    return parts


def find_locations(entity_string, text_tokens):
    locations = []
    e_parts = tokenize_entity(entity_string)
    for i in range(len(text_tokens)):
        if text_tokens[i:i + len(e_parts)] == e_parts:
            locations.append(i)
    return e_parts, locations


class EntitySimple:
    def __init__(self, _e_string, _e_parts, _e_type, _locations):
        self.string = _e_string
        self.parts = _e_parts
        self.type = _e_type
        self.locations = _locations

    def __hash__(self):
        return hash(self.string) ^ hash(self.type)

    def __eq__(self, other):
        return self.string == other.string and self.type == other.type


class EntityLinked:
    def __init__(self, _e_string, _e_parts, _e_type, _locations, _url=None):
        self.string = _e_string
        self.parts = _e_parts
        self.type = _e_type
        self.locations = _locations
        self.url = _url

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url


class Relationship:
    def __init__(self, _sentence, _before, _between, _after, _ent1, _ent2,
                 e1_type, e2_type):
        self.sentence = _sentence
        self.before = _before
        self.between = _between
        self.after = _after
        self.e1 = _ent1
        self.e2 = _ent2
        self.e1_type = e1_type
        self.e2_type = e2_type

    def __eq__(self, other):
        if self.e1 == other.e1 and self.before == other.before and \
                        self.between == other.between \
                and self.after == other.after:
            return True
        else:
            return False

    def __hash__(self):
        # print('before:%s  between:%s   after:%s' %(self.before, self.between, self.after))
        return hash(self.e1) ^ hash(self.e2) ^ hash(self.before) ^ \
               hash(self.between) ^ hash(self.after)


class Sentence:

    def __init__(self, sentence, e1_type, e2_type, max_tokens, min_tokens,
                 window_size,
                 pos_tagger=None, config=None):

        self.relationships = list()
        self.tagged_text = None

        # determine which type of regex to use according to
        # how named-entities are tagged
        entities_regex = None
        if config is not None:
            if config.tag_type == "simple":
                entities_regex = config.regex_simple
                regex_clean_simple = config.regex_clean_simple
            elif config.tag_type == "linked":
                entities_regex = config.regex_linked
                regex_clean_linked = config.regex_clean_linked

            tag_type = config.tag_type
        else:
            entities_regex = regex_simple
            tag_type = "simple"
            regex_clean_simple = re.compile('</?[A-Z]+>', re.U)
            regex_clean_linked = re.compile('</[A-Z]+>|<[A-Z]+ url=[^>]+>', re.U)

        # find named-entities
        entities = []
		
        # print('start-----------------')
        for m in re.finditer(entities_regex, sentence):
            entities.append(m)
            # print('m:', m)
        # print('End-----------------')

        if len(entities) >= 2:
            # clean tags from text
            sentence_no_tags = None
            if tag_type == "simple":
                sentence_no_tags = re.sub(
                    regex_clean_simple, "", sentence
                )
            elif tag_type == "linked":
                sentence_no_tags = re.sub(
                    regex_clean_linked, "", sentence
                )
            try:
                text_tokens = word_tokenize(sentence_no_tags.decode('utf-8'))
            except UnicodeDecodeError:
                raise

            # extract information about the entity, create an Entity instance
            # and store in a structure to hold information collected about
            # all the entities in the sentence
            entities_info = set()
            for x in range(0, len(entities)):
                if tag_type == "simple":
                    entity = entities[x].group()
                    # the first parenthesized subgroup i.e. entity mention
                    e_string = re.findall('<[A-Z]+>([^<]+)</[A-Z]+>', entity)[0]
                    # the first parenthesized subgroup i.e. entity type
                    e_type = re.findall('<([A-Z]+)', entity)[0]
                    e_parts, locations = find_locations(e_string, text_tokens)
                    e = EntitySimple(e_string, e_parts, e_type, locations)
                    entities_info.add(e)

                elif tag_type == "linked":
                    entity = entities[x].group()
                    e_url = re.findall('url=([^>]+)', entity)[0]
                    e_string = re.findall(
                        '<[A-Z]+ url=[^>]+>([^<]+)</[A-Z]+>', entity)[0]
                    e_type = re.findall('<([A-Z]+)', entity)[0]
                    e_parts, locations = find_locations(e_string, text_tokens)
                    e = EntityLinked(
                        e_string, e_parts, e_type, locations, e_url
                    )
                    entities_info.add(e)

            # create an hash table:
            # - key is the starting index in the tokenized sentence of an entity
            # - value the corresponding Entity instance
            locations = dict()
            for e in entities_info:
                for start in e.locations:
                    locations[start] = e

            # look for pair of entities such that:
            # the distance between the two entities is less than 'max_tokens'
            # and greater than 'min_tokens'
            # the arguments match the seeds semantic types

            # UPDATE: Get all possible pairs of entities,
            # instead of in sequence entity occurrences
            sorted_keys = list(sorted(locations))
            for i in range(len(sorted_keys)-1):
                for i_next in range(i+1,len(sorted_keys)):
                    distance = sorted_keys[i_next] - sorted_keys[i]
                    e1 = locations[sorted_keys[i]]
                    e2 = locations[sorted_keys[i_next]]
                    if max_tokens >= distance >= min_tokens and e1.type == e1_type \
                            and e2.type == e2_type:

                        # ignore relationships between the same entity
                        if tag_type == "simple":
                            if e1.string == e2.string:
                                continue
                        elif tag_type == "linked":
                            if e1.url == e2.url:
                                continue

                        # run PoS-tagger over the sentence only once
                        if self.tagged_text is None:
                            # split text into tokens and tag them using NLTK's
                            # default English tagger
                            # POS_TAGGER = 'taggers/maxent_treebank_pos_tagger/
                            # english.pickle'
                            if pos_tagger is None:
                                pos_tagger = load('taggers/maxent_treebank_pos_tagger/english.pickle')
                            self.tagged_text = pos_tagger.tag(text_tokens)

                        before = self.tagged_text[:sorted_keys[i]]
                        before = before[-window_size:]
                        between = self.tagged_text[sorted_keys[i] +
                                                   len(e1.parts):sorted_keys[i_next]]
                        after = self.tagged_text[sorted_keys[i_next]+len(e2.parts):]
                        after = after[:window_size]

                        if tag_type == "simple":
                            r = Relationship(
                                sentence, before, between, after, e1.string,
                                e2.string, e1_type, e2.type
                            )

                        elif tag_type == "linked":
                            r = Relationship(
                                sentence, before, between, after, e1.url, e2.url,
                                e1.type, e2.type
                            )

                        self.relationships.append(r)
						