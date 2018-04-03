#!/usr/bin/env python
# -*- coding: utf-8 -*-
           
# description: To collect relationships facts from Freebase

# usage: python easy_freebase_clean.py freebase-easy-facts.txt out_freebase_easy_relationship_file.txt

import re
import fileinput
import sys
from collections import defaultdict

def collect_relationships(data, relationship_file):
    #######################
    # weak entity linking #
    #######################
    # load freebase entities to memory
    # select only a few entities, based on the relationships

    rel_to_consider = [
        # PER-ORG
        'Governance of', 'Leader of',
        'Organization founded', 'Employment history',

        # PER/ORG-ORG
        'Organization acquired',
        #'Venture Investment',
        'Involved in merger',

        # ORG-LOC
        'Place founded',

        # LOC-LOC
        'location/mailing_address/citytown', 'Neighborhood of', 'Capital of',

        # PER-PER
        'Spouse (or domestic partner)', 'Married To', 'Sibling', 'Peer']

    """
    PER-PER
    ==============================
    Spouse (or domestic partner)
    Married To
    Sibling
    Peer

    LOC-LOC
    =================================
    location/mailing_address/citytown
    Neighborhood of
    Capital of

    PER-ORG
    =====================
    Employment history
    Leader of
    Organization founded
    Governance of
    Organization acquired

    ORG-ORG
    =====================
    Organization acquired
    # Venture Investment
    Involved in merger

    ORG-LOC
    =============
    Place founded
    """

    relationships = defaultdict(list)

    count = 0
    numbered = re.compile('#[0-9]+$')
    for line in fileinput.input(data):
        if count % 50000 == 0:
            print len(relationships)

        try:
            e1, r, e2, point = line.split('\t')
        except:
            continue

        if r in rel_to_consider:
            # ignore some entities, which are Freebase
            # identifiers or which are ambigious
            if e1.startswith('/') or e2.startswith('/'):
                continue
            if e1.startswith('m/') or e2.startswith('m/'):
                continue
            if re.search(numbered, e1) or re.search(numbered, e2):
                continue

            # lots of irrelevant stuff in contained_by
            if re.match(r'^[0-9]+$', e1) or re.match(r'^[0-9]+$', e2):
                continue
            if e1.startswith('DVD Region') or e2.startswith('DVD Region'):
                continue
            if e1.startswith('US Census'):
                continue
            if e1.startswith('Area code') or e2.startswith('Area code'):
                continue
            else:
                if "(" in e1:
                    e1 = re.sub(r"\(.*\)", "", e1).strip()
                if "(" in e2:
                    e2 = re.sub(r"\(.*\)", "", e2).strip()
                relationships[(e1, e2)].append(r)
        count += 1
    fileinput.close()

    print "Writing collected relationships to disk"
    f_entities = open(relationship_file, "w")
    for r in relationships.keys():
        for e in relationships[r]:
            f_entities.write(r[0]+'\t'+e+'\t'+r[1]+'\n')
    f_entities.close() 

    return relationships


def main():
    relationships = collect_relationships(sys.argv[1], relationship_file=sys.argv[2])
    print len(relationships)

if __name__ == "__main__":
    main()
