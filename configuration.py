#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Module docstring
"""

import os, sys, json, posixpath, time, datetime, json, codecs, logging
from os.path import relpath
from abc import ABCMeta
from enum import Enum

from dom_analyzer import DomAnalyzer, Tag
from clickable import Clickable, InputField, SelectField, Checkbox, CheckboxField, Radio, RadioField
from automata import Automata, State, Edge
from normalizer import AttributeNormalizer, TagNormalizer, TagWithAttributeNormalizer

class Configuration:
    __metaclass__ = ABCMeta

    def __init__(self):
        self._invariants = []
        self._max_depth = 3
        self._max_states = 10
        self._max_time = 2000
        self._sleep_time = 2

    def set_max_depth(self, depth):
        self._max_depth = depth

    def get_max_depth(self):
        return self._max_depth

    def set_max_states(self, state_num):
        self._max_states = state_num

    def get_max_states(self):
        return self._max_states

    def set_max_time(self, time_in_second):
        self._max_time = time_in_second

    def get_max_time(self):
        return self._max_time

    def set_sleep_time(self, time_in_second):
        self._sleep_time = time_in_second

    def get_sleep_time(self):
        return self._sleep_time

#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
class SeleniumConfiguration(Configuration):
    def __init__(self, browserID, other_browserID, url, folderpath=None, dirname=None ):
        super(SeleniumConfiguration, self).__init__()
        self._browserID = browserID
        self._other_browserID = other_browserID
        self._url = url
        self._dirname = dirname
        self._folderpath = folderpath
        self._root_path = ''
        self._file_path = {}
        self.set_file_path()
        self._browsersize = {
            'x':1280,
            'y':960,
        }
        self._automata_fname = 'automata.json'
        self._traces_fname = 'traces.json'
        self._dom_inside_iframe = True
        self._before_trace_fname = ''
        self._frame_tags = []
        self._domains = []
        self._scripts = []
        self._trace_amount = 1
        self._max_length = 1
        self._analyzer = {
            'simple_clickable_tags': False,
            'simple_inputs_tags': False,
            'simple_normalizers': False,
            'clickable_tags': [],
            'inputs_tags': [],
            'tag_normalizers': [],
            'attributes_normalizer': [],
            'tag_with_attribute_normalizers': []
        }
        self._mutation = {
            'mutation_method': MutationMethod.Simple,
            'modes': 0,
            'mutant_scripts': []
        }


    def set_folderpath(self, folderpath):
        self._folderpath = folderpath
        self.set_file_path()

    def set_dirname(self, dirname):
        self._dirname = dirname
        self.set_file_path()

    def set_file_path(self):
        self._dirname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') if not self._dirname else self._dirname
        self._root_path = os.path.join('trace', self._dirname ) if not self._folderpath else os.path.join( self._folderpath, self._dirname )
        self._file_path = {
            'root': self._root_path,
            'dom': os.path.join(self._root_path, 'dom'),
            'state': os.path.join(self._root_path, 'screenshot', 'state'),
            'log': os.path.join(self._root_path, 'log'),
            'coor': os.path.join(self._root_path, 'coor')
        }

    def get_abs_path(self, my_type):
        abs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self._file_path[my_type])
        return abs_path

    def get_path(self, my_type):
        return self._file_path[my_type]

    def set_browserID(self, app_name):
        self._browserID = browserID

    def set_other_browserID(self, app_name):
        self._other_browserID = other_browserID

    def get_browserID(self):
        return self._browserID

    def get_other_browserID(self):
        return self._other_browserID

#==============================================================================================================
# crawler configuration
#==============================================================================================================
    def set_url(self, app_id):
        self._url = _url

    def get_url(self):
        return self._url

    def set_domains(self, domains):
        self._domains = domains

    def get_domains(self):
        return self._domains

    def set_trace_amount(self, amount):
        self._trace_amount = amount

    def get_trace_amount(self):
        return self._trace_amount

    def set_max_length(self, length):
        self._max_length = length

    def get_max_length(self):
        return self._max_length

#==============================================================================================================
# Dom analysis configuration
#==============================================================================================================
    def set_dom_inside_iframe(self, is_inside):
        self._dom_inside_iframe = is_inside

    def is_dom_inside_iframe(self):
        return self._dom_inside_iframe

    def set_frame_tags(self, tags):
        self._frame_tags += tags

    def get_frame_tags(self):
        return self._frame_tags

#==============================================================================================================
# Dom normalize configuration
#==============================================================================================================
    def set_clickable_tag(self, tag_name, attr=None, value=None):
        self._analyzer['clickable_tags'].append({'tag':tag_name, 'attr':attr, 'value':value})
        DomAnalyzer.add_clickable_tag(tag_name, attr, value)

    def set_inputs_tag(self, input_type):
        self._analyzer['inputs_tags'].append(input_type)
        DomAnalyzer.add_inputs_tag(input_type)

    def set_tags_normalizer(self, tags):
        self._analyzer['tag_normalizers'] += tags
        DomAnalyzer.add_tags_normalizer(tags)

    def set_attributes_normalizer(self, attrs):
        self._analyzer['attributes_normalizer'] += attrs
        DomAnalyzer.add_attributes_normalizer(attrs)

    def set_tag_with_attribute_normalizer(self, tag_name, attr=None, value=None, mode=None):
        self._analyzer['tag_with_attribute_normalizers'].append({'tag':tag_name, 'attr':attr, 'value':value, 'mode':mode})
        DomAnalyzer.add_tag_with_attribute_normalizer(tag_name, attr, value, mode)

    def set_simple_clickable_tags(self):
        self._analyzer['simple_clickable_tags'] = True
        DomAnalyzer.set_simple_clickable_tags()

    def set_simple_inputs_tags(self):
        self._analyzer['simple_inputs_tags'] = True
        DomAnalyzer.set_simple_inputs_tags()

    def set_simple_normalizers(self):
        self._analyzer['simple_normalizers'] = True
        DomAnalyzer.set_simple_normalizers()
        
#==============================================================================================================
# filename configuration
#==============================================================================================================
    def set_automata_fname(self, automata_fname):
        self._automata_fname = automata_fname

    def get_automata_fname(self):
        return self._automata_fname

    def set_traces_fname(self, traces_fname):
        self._traces_fname = traces_fname

    def get_traces_fname(self):
        return self._traces_fname

    def get_before_trace(self):
        return self._scripts

    def set_before_script_by_fname(self, trace_fname):
        data = self.load_json(trace_fname)
        self._scripts = self.build_trace(data)

    def get_before_script(self):
        return self._scripts

#==============================================================================================================
# mutation configuration
#==============================================================================================================
    def set_mutation_trace(self, traces_fname, trace_id):
        data = self.load_json(traces_fname)
        self._mutation['mutant_scripts'] = self.build_trace(data['traces'][int(trace_id)])

    def get_mutation_trace(self):
        return self._mutation['mutant_scripts']

    def set_mutation_modes(self, modes):
        self._mutation['modes'] = []
        for i in modes.split('#'):
            self._mutation['modes'].append(int(i))

    def get_mutation_modes(self):
        return self._mutation['modes']

    def set_mutation_method(self, method):
        if type(method) == type(MutationMethod):
            self._mutation['mutation_method'] = method
        elif method == '1':
            self._mutation['mutation_method'] = MutationMethod.Simple
        elif method == '2':
            self._mutation['mutation_method'] = MutationMethod.AllInputsOneState
        elif method == '3':
            self._mutation['mutation_method'] = MutationMethod.OneInputsAllState
        elif method == '4':
            self._mutation['mutation_method'] = MutationMethod.OneInputsOneState

    def get_mutation_method(self):
        return self._mutation['mutation_method']

    def load_json(self, json_file):
        try:
            with open(json_file) as data_file:      
                data = json.load(data_file)
                return data
        except Exception as e:
            logging.error('can not read json: %s', str(e))

    def build_trace(self, data):
        try:
            edges = []
            for edge in data['edges']:
                state_from = edge['from']
                state_to = edge['to']
                c = edge['clickable']
                clickable = Clickable( c['id'], c['name'], c['xpath'], c['tag'] )
                inputs = []
                for i in edge['inputs']:
                    inputs.append( InputField( i['id'], i['name'], i['xpath'], i['type'], i['value'] ) )
                selects = []
                for s in edge['selects']:
                    selects.append( SelectField( s['id'], s['name'], s['xpath'], s['value'], s['selected'] ) )
                checkboxes = []
                for c_field in edge['checkboxes']:
                    c_list = []
                    for c in c_field['checkbox_list']:
                        c_list.append( Checkbox( c['id'], c['name'], c['xpath'], c['value'] ) )
                    checkboxes.append( CheckboxField(c_list, c_field['checkbox_name'], c_field['checkbox_selected_list']) )
                radios = []
                for r_field in edge['radios']:
                    r_list = []
                    for r in r_field['radio_list']:
                        r_list.append( Radio( r['id'], r['name'], r['xpath'], r['value'] ) )
                    radios.append( RadioField(r_list, r_field['radio_name'], r_field['radio_selected']) )
                iframe_list = edge['iframe_list']
                edges.append( Edge( state_from, state_to, clickable, inputs, selects, checkboxes, radios, iframe_list ) )
            return edges
        except Exception as e:
            logging.error('can not build trace: %s', str(e))

    def save_config(self, fname):
        config_data = {}
        config_data['max_depth'] = self._max_depth
        config_data['max_states'] = self._max_states
        config_data['max_time'] = self._max_time
        config_data['sleep_time'] = self._sleep_time
        config_data['url'] = self._url
        config_data['browser_id'] = str(self._browserID)
        config_data['other_browser_id'] = str(self._other_browserID)
        config_data['dirname'] = self._dirname
        config_data['folderpath'] = self._folderpath
        config_data['browser_size'] = self._browsersize
        #=============================================================================================
        config_data['automata_fname'] = self._automata_fname
        config_data['root_path'] = posixpath.join(
            posixpath.join(*(self.get_path('root').split(os.sep)))
        )
        config_data['dom_path'] = posixpath.join(
            posixpath.join(*(self.get_path('dom').split(os.sep)))
        )
        config_data['state_path'] = posixpath.join(
            posixpath.join(*(self.get_path('state').split(os.sep)))
        )
        config_data['log_path'] = posixpath.join(
            posixpath.join(*(self.get_path('log').split(os.sep)))
        )
        config_data['coor_path'] = posixpath.join(
            posixpath.join(*(self.get_path('coor').split(os.sep)))
        )
        #=============================================================================================
        #new config
        config_data['domains'] = self._domains
        config_data['dom_inside_iframe'] = self._dom_inside_iframe
        config_data['traces_fname'] = self._traces_fname
        config_data['before_trace_fname'] = self._before_trace_fname

        config_data['analyzer'] = self._analyzer
        config_data['mutation'] = {
            "modess": str( self._mutation['modes'] ),
            "mutation_method": str( self._mutation['mutation_method'] )
        }
        #=============================================================================================
        with codecs.open(os.path.join(self.get_abs_path('root'), fname), 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, sort_keys=True, ensure_ascii=False)
#==============================================================================================================================

#==============================================================================================================================
# class for Enum clearly
#==============================================================================================================================
class Browser(Enum):
    FireFox = 1
    Chrome = 2
    Ie = 3
    PhantomJS = 4

class MutationMethod(Enum):
    Simple = 1
    AllInputsOneState = 2
    OneInputsAllState = 3
    OneInputsOneState = 4
    EachInputsOneState = 5

class MutationMode(Enum):
    Empty               = 1
    MaxLength           = 2
    RandomString        = 3
    MalformedSymbol     = 4
    SQLInjection        = 5
