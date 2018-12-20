import pandas
import json
import collections


parts = pandas.read_table('../tsv/isa_parts_list_e.txt')
find_json_parts = False
if find_json_parts:
    parts_json = []
    for index, part in parts.iterrows():
        t = collections.OrderedDict()
        t['id'] = part['concept_id']
        t['representation_id'] = part['representation_id']
        t['name'] = part['name']
        parts_json.append(t)
    p = json.dumps(parts_json)
    parts_json_file = '../json/isa_parts_list_e.json'
    f = open(parts_json_file,'w')
    print >> f, p


elements = pandas.read_table('../tsv/isa_element_parts.txt')
find_json_elements = False
if find_json_elements:
    elements_json = []
    for index, part in parts.iterrows():
        t = collections.OrderedDict()
        t['id'] = part['concept_id']
        t['name'] = part['name']
        t['element_files'] = elements[elements['name'].str.match(part['name']) & elements['concept_id'].str.match(part['concept_id'])]['element_file_id'].to_json(orient='values')
        #childfiles = elements[elements['name'].str.match(part['name']) & elements['concept_id'].str.match(part['concept_id'])]
        #for cindex, child in childfiles.iterrows():
        #    c = collections.OrderedDict()
        #    c['element'] = child['element_file_id']
        #    t['element_files'].append(c)
        #t['element_file'] = element['element_file_id']
        elements_json.append(t)
    e = json.dumps(elements_json)
    elements_json_file = '../json/isa_element_parts.json'
    f = open(elements_json_file,'w')
    print >> f, e


inclusion = pandas.read_table('../tsv/isa_inclusion_relation_list.txt')
find_json_inclusion = False
if find_json_inclusion:
    inclusion_json = []
    for index, part in parts.iterrows():
        try:
            children = inclusion[inclusion['parent_name'].str.match(part['name']) & inclusion['parent_id'].str.match(part['concept_id'])]
            t = collections.OrderedDict()
            t['id'] = part['concept_id']
            t['name'] = part['name']
            t['children'] = []
            for cindex, child in children.iterrows():
                c = collections.OrderedDict()
                c['id'] = child['child_id']
                c['name'] = child['child_name']
                t['children'].append(c)
            inclusion_json.append(t)
        except:
            no_children = True
    i = json.dumps(inclusion_json)
    inclusion_json_file = '../json/isa_inclusion_relation_list.json'
    f = open(inclusion_json_file,'w')
    print >> f, i


def get_children(prnt):
    tier = []
    try:
        children = inclusion[inclusion['parent_name'].str.match(prnt['name']) & inclusion['parent_id'].str.match(prnt['id'])]
        for cindex, child in children.iterrows():
            part = parts[parts['name'].str.match(child['child_name']) & parts['concept_id'].str.match(child['child_id'])]
            t = collections.OrderedDict()
            t['id'] = part['concept_id'].to_string(index=False)
            t['representation_id'] = part['representation_id'].to_string(index=False)
            t['name'] = part['name'].to_string(index=False)
            t['parent'] = prnt['name']
            t['level'] = prnt['level'] + 1
            if prnt['level'] == 0:
                t['system'] = part['name'].to_string(index=False)
            else:
                t['system'] = prnt['system']
            t['region'] = ''
            #t['element_files'] = elements[elements['name'].str.match(part['name']) & elements['concept_id'].str.match(part['concept_id'])]['element_file_id'].to_json(orient='values')
            t['children'] = get_children(t)
            tier.append(t)
    except:
        print('no children found')
    return tier

find_tree = False
if find_tree:
    tree_json = []
    #body = 'human body'
    body = 'anatomical entity'
    top = collections.OrderedDict()
    top_series = parts[parts['name'].str.match(body)]
    top['id'] = top_series['concept_id'].to_string(index=False)
    top['representation_id'] = top_series['representation_id'].to_string(index=False)
    top['name'] = body
    top['parent'] = ''
    top['level'] = 0
    top['system'] = 'complete anatomy'
    top['region'] = 'entire body'
    #top['element_files'] = elements[elements['name'].str.match(body)]['element_file_id'].to_json(orient='values')
    top['children'] = get_children(top)

    tree_json.append(top)

    t = json.dumps(tree_json)
    tree_json_file = '../json/isa_tree.json'
    f = open(tree_json_file,'w')
    print >> f, t
