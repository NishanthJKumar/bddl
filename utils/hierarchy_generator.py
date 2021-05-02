"""
Purpose:
This is the script that generates the 'hierarchy.json' file that will be necessary
for many purposes like initial/goal state annotation, object shopping list annotation,
and scene generation in iGATUS. 

Output Format:
TODO: Describes output format.
TODO: Generate 3 types of hierarchy.json:
    - Hierarchy of just the owned models for scene generation and object sampling.
    - Hierarchy of the union of all of the owned models + objects extracted from online articles.
    - Hierarchy of just the objects from online articles, this is our most unbiased object distribution.

To Run:
- Make sure that the .csv files and the .json file are updated (see ### Dependencies).
- python3 hierarchy_generator.py

Last Change: 05/02/2021
Created By: Zheng Lian & Cem Gokmen
"""

import csv
import json
import os
from collections import OrderedDict

from nltk.corpus import wordnet as wn

### Dependencies
'''
This .csv file should contain all of the models we currently own.
Should contain an `Object` column and a `Synset` column.
'''
MODELS_CSV_PATH = "objectmodeling.csv"
'''
This .csv file should contain all of the objects we extracted from
online articles.
Should contain an `Object` column and a `Synset` column.
'''
OBJECT_STATS_PATH = "object_stats.csv"
'''
This .json file should contain all of the synsets from the .csv files above
as well as their associated iGibson abilities.
NOTE: Please contact Sanjana (sanjana2@stanford.edu) or Zheng (zhengl@stanford.edu) if
any of the property annotations is missing.
'''
ABILITY_JSON_PATH = "synsets_to_filtered_properties.json"

OUTPUT_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "tasknet", "hierarchy.json")

'''
Load in all of the owned models. Map the synsets to their corresponding object names.
'''
owned_synsets = {}
with open(MODELS_CSV_PATH) as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        synset = row["Synset"].strip()
        # synset = synset[synset.find('\'')+1: synset.rfind('\'')]
        obj = row["Object"].strip()
        if synset in owned_synsets:
            owned_synsets[synset].append(obj)
        else:
            owned_synsets[synset] = [obj]


def add_path(path, node):
    """
    Takes in list of synsets and add it into the overall hierarchy.

    @param path: List of strings, where each string is a synset.
      - The list is in the form of [child, parent, grandparent, ...]
    @param node: Dictionary, contains the overall hierarchy we are building
    """
    if not path:
        return
    # Take out the oldest ancestor in the path.
    oldest_synset = path[-1]
    name = oldest_synset.name()

    # If the current node never had a child before, initialize a list to store them.
    if "children" not in node:
        node["children"] = []
    # Look for an existing child that matches the current synset.
    for child_node in node["children"]:
        if child_node["name"] == name:
            add_path(path[:-1], child_node)
            return
    # If this is a child we have yet to find, append it into our hierarchy.
    node["children"].append({"name": name})
    add_path(path[:-1], node["children"][-1])


def generate_paths(paths, path, word):
    """
    Given a synset, generate all paths this synset can take up to 'entity.n.01'.

    @param paths, List of lists, will be populated with the paths we create here.
    @param path: List, the current path we are building.
    @param word: The current synset we are searching parents for.
    """
    hypernyms = word.hypernyms()
    if not hypernyms:
        paths.append(path)
    else:
        for parent in hypernyms:
            generate_paths(paths, path + [parent], parent)

'''
Below is the script that creates the .json hierarchy
'''
# Every synset we have should theoretically lead up to `entity.n.01`.
hierarchy = {"name": 'entity.n.01', "children": []}

for synset in owned_synsets:
    synset = wn.synset(synset)
    synset_paths = []
    generate_paths(synset_paths, [synset], synset)
    for synset_path in synset_paths:
        # The last word should always be `entity.n.01`, so we can just take it out.
        add_path(synset_path[:-1], hierarchy)


# Go through the hierarchy and add the words associated with the synsets as attributes.
def add_igibson_objects(node):
    categories = []
    if node["name"] in owned_synsets:
        categories = owned_synsets[node["name"]]

    node["igibson_categories"] = categories

    if "children" in node:
        for child_node in node["children"]:
            add_igibson_objects(child_node)

add_igibson_objects(hierarchy)

with open(ABILITY_JSON_PATH) as f:
    ability_map = json.load(f)

def add_abilities(node):
    # At leaf
    if "children" not in node:
        name = node["name"]
        if name in ability_map:
            if isinstance(ability_map[name], dict):
                abilities = ability_map[name]
            else:
                # Support legacy format ability annotations where params are not
                # supported and abilities are in list format.
                abilities = {ability: dict() for ability in ability_map[name]}

            node["abilities"] = OrderedDict(sorted(abilities.items(), key=lambda pair: pair[0]))
            return abilities
        else:
            node["abilities"] = OrderedDict()
            print(f"{name} not found in ability list!")
            return None
    else:
        init = False
        abilities = {}
        for child_node in node["children"]:
            child_abilities = add_abilities(child_node)
            if child_abilities is not None:
                if init:
                    # First merge the ability annotations themselves
                    common_keys = set(abilities.keys()) & set(child_abilities.keys())

                    # Then add the ability annotations & merge common parameters
                    new_abilities = {}
                    for ability_key in common_keys:
                        current_params = set(abilities[ability_key].items())
                        child_params = set(
                            child_abilities[ability_key].items())

                        # Note that this intersection finds pairs where both the param
                        # key and the param value are equal.
                        common_params = current_params & child_params

                        new_abilities[ability_key] = dict(common_params)

                    abilities = new_abilities
                else:
                    abilities = child_abilities
                    init = True
        node["abilities"] = OrderedDict(sorted(abilities.items(), key=lambda pair: pair[0]))
        return abilities

add_abilities(hierarchy)

with open(OUTPUT_JSON_PATH, "w") as f:
    json.dump(hierarchy, f, indent=2)
