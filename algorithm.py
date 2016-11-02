#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, codecs, logging, random
from abc import ABCMeta, abstractmethod
from configuration import Browser
from dom_analyzer import DomAnalyzer
from executor import SeleniumExecutor,CBTExecutor
from PIL import Image

class AlgoCrawler:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_utility(self, crawler, configuration, executor, automata):
        pass

    @abstractmethod
    def prepare(self):
        pass

    @abstractmethod
    def add_new_events(self, state, prev_state, depth):
        pass  
        
    @abstractmethod
    def get_next_action(self, action_events):
        pass  

    @abstractmethod
    def trigger_action(self, state, new_edge, action, depth):
        pass  

    @abstractmethod
    def update_with_same_state(self, current_state, new_edge, action, depth, dom_list, url):
        pass  

    @abstractmethod
    def update_with_out_of_domain(self, current_state, new_edge, action, depth, dom_list, url):
        pass  

    @abstractmethod
    def update_with_new_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        pass  

    @abstractmethod
    def update_with_old_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        pass  

    @abstractmethod
    def save_traces(self):
        pass

    @abstractmethod
    def end(self):
        pass

class DFScrawler(AlgoCrawler):
    def __init__(self):
        pass
        #self.other_executor = SeleniumExecutor(Browser.Chrome, "http://140.112.42.145:2000/demo/nothing/main.html")


    def set_utility(self, crawler, configuration, executor, automata):
        self.crawler = crawler
        self.configuration = configuration
        self.executor = executor
        self.automata = automata

    def prepare(self):
        #executor
        self.executor.start()
        self.executor.goto_url()

        #initial state
        initial_state = self.crawler.get_initail_state()
        self.crawler.run_script_before_crawl(initial_state)

    def add_new_events(self, state, prev_state, depth):
        for clickables, iframe_key in DomAnalyzer.get_clickables(state, prev_state if prev_state else None):
            for clickable in clickables:
                self.crawler.action_events.append( {
                        'state'  : state,
                        'action' : { 'clickable':clickable, 'iframe_key':iframe_key },
                        'depth'  : depth,
                    } )

    def get_next_action(self, action_events):
        event = action_events.pop()
        return event

    def change_state(self, state, action, depth):
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,state.get_id() )
        self.crawler.backtrack(state)
        logging.info('==========< BACKTRACK END   >==========')

    def trigger_action(self, state, new_edge, action, depth):
        logging.info(' |depth:%s state:%s| fire element in iframe(%s)', depth, state.get_id(), action['iframe_key'])
        self.crawler.make_value(new_edge)
        self.executor.click_event_by_edge(new_edge)

    def update_with_same_state(self, current_state, new_edge, action, depth, dom_list, url):
        # Do Nothing when same state
        return None

    def update_with_out_of_domain(self, current_state, new_edge, action, depth, dom_list, url):
        # back if state out of domain
        logging.info(' |depth:%s state:%s| out of domain: %s', depth, current_state.get_id(), url)
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,current_state.get_id() )
        self.crawler.backtrack(current_state)
        logging.info('==========< BACKTRACK END   >==========')

    def update_with_new_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        # automata save new state 
        logging.info(' |depth:%s state:%s| add new state %s of : %s', depth, current_state.get_id(), new_state.get_id(), url )

        self.automata.save_state(new_state, depth)
        
        self.automata.save_state_shot(self.executor, new_state)


        if depth < self.configuration.get_max_depth():
            self.crawler.add_new_events(new_state, current_state, depth)

    def update_with_old_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        #check if old state have a shorter depth
        if depth < new_state.get_depth():
            new_state.set_depth(depth)
            self.crawler.add_new_events(new_state, current_state, depth)

    def save_traces(self):
        self.automata.save_simple_traces()

    def end(self):
        pass

class MonkeyCrawler(AlgoCrawler):
    def __init__(self):
        self.trace_length_count = 0
        self.traces = []
        self.trace_history = {}

    def set_utility(self, crawler, configuration, executor, automata):
        self.crawler = crawler
        self.configuration = configuration
        self.executor = executor
        self.automata = automata

    def prepare(self):
        #executor
        self.executor.start()
        self.executor.goto_url()
        #initial state
        initial_state = self.crawler.get_initail_state()
        #save trace
        self.trace_length_count = 0
        self.trace_history = { 'states': [ initial_state ], 'edges': [] }

        self.crawler.run_script_before_crawl(initial_state)

    def add_new_events(self, state, prev_state, depth):
        candidate_clickables = []

        for clickables, iframe_key in DomAnalyzer.get_clickables(state, prev_state if prev_state else None):
            for clickable in clickables:
                candidate_clickables.append( (clickable, iframe_key) )

        if not candidate_clickables:
            return

        clickable, iframe_key = random.choice( candidate_clickables )
        #print(state.get_id(),clickable.get_id(), clickable.get_xpath())
        self.crawler.action_events.append( {
            'state'  : state,
            'action' : { 'clickable':clickable, 'iframe_key':iframe_key },
            'depth'  : depth,
        } )
        
    def get_next_action(self, action_events):
        event = action_events.pop()
        return event

    def change_state(self, state, action, depth):
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,state.get_id() )
        self.crawler.backtrack(state)
        logging.info('==========< BACKTRACK END   >==========')

    def trigger_action(self, state, new_edge, action, depth):
        logging.info(' |depth:%s state:%s| fire element in iframe(%s)', depth, state.get_id(), action['iframe_key'])
        self.trace_length_count += 1

        self.crawler.make_value(new_edge)
        self.executor.click_event_by_edge(new_edge)

    def update_with_same_state(self, current_state, new_edge, action, depth, dom_list, url):
        #save trace
        self.trace_history['states'].append(current_state)
        self.trace_history['edges'].append(new_edge)
        #get new event again
        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(current_state, None, depth)

    def update_with_out_of_domain(self, current_state, new_edge, action, depth, dom_list, url):
        # back if state out of domain
        logging.info(' |depth:%s state:%s| out of domain: %s', depth, current_state.get_id(), url)
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,current_state.get_id() )
        self.crawler.backtrack(current_state)
        logging.info('==========< BACKTRACK END   >==========')

        #get new event again
        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(current_state, None, depth)

    def update_with_new_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        #save trace
        self.trace_history['states'].append(new_state)
        self.trace_history['edges'].append(new_edge)
        # automata save new state 
        logging.info(' |depth:%s state:%s| add new state %s of : %s', depth, current_state.get_id(), new_state.get_id(), url )
        self.automata.save_state(new_state, depth)
        self.automata.save_state_shot(self.executor, new_state)

        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(new_state, None, depth)

    def update_with_old_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        #save trace
        self.trace_history['states'].append(new_state)
        self.trace_history['edges'].append(new_edge)
        #check if old state have a shorter depth
        if depth < new_state.get_depth():
            new_state.set_depth(depth)
        if depth > new_state.get_depth():
            depth = new_state.get_depth()
        
        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(new_state, None, depth)

    def save_traces(self):
        self.automata.save_traces(self.traces)

    def end(self):
        self.traces.append( self.trace_history )
        self.trace_length_count = 0
        self.trace_history = {}


class Monkey2Crawler(AlgoCrawler):
    def __init__(self):
        self.trace_length_count = 0
        self.traces = []
        self.trace_history = {}

        self.other_executor = SeleniumExecutor(Browser.Chrome, "http://140.112.42.145:2000/demo/nothing/main.html")

    def set_utility(self, crawler, configuration, executor, automata):
        self.crawler = crawler
        self.configuration = configuration
        self.executor = executor
        self.automata = automata

    def prepare(self):
        #executor
        self.executor.start()
        self.executor.goto_url()

        self.other_executor.start()
        self.other_executor.goto_url()
        #initial state
        initial_state = self.crawler.get_initail_state()


        self.other_executor.get_screenshot("pic/pic.png")
        #save trace
        self.trace_length_count = 0
        self.trace_history = { 'states': [ initial_state ], 'edges': [] }

        self.crawler.run_script_before_crawl(initial_state)

    def add_new_events(self, state, prev_state, depth):
        candidate_clickables = []

        for clickables, iframe_key in DomAnalyzer.get_clickables(state, prev_state if prev_state else None):
            for clickable in clickables:
                candidate_clickables.append( (clickable, iframe_key) )

        if not candidate_clickables:
            return

        clickable, iframe_key = random.choice( candidate_clickables )
        print(state.get_id(),clickable.get_id(), clickable.get_xpath())
        self.crawler.action_events.append( {
            'state'  : state,
            'action' : { 'clickable':clickable, 'iframe_key':iframe_key },
            'depth'  : depth,
        } )
        
    def get_next_action(self, action_events):
        event = action_events.pop()
        return event

    def change_state(self, state, action, depth):
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,state.get_id() )
        self.crawler.other_executor_backtrack(state, self.other_executor)
        logging.info('==========< BACKTRACK END   >==========')

    def trigger_action(self, state, new_edge, action, depth):
        logging.info(' |depth:%s state:%s| fire element in iframe(%s)', depth, state.get_id(), action['iframe_key'])
        self.trace_length_count += 1

        self.crawler.make_value(new_edge)
        self.executor.click_event_by_edge(new_edge)
        self.other_executor.click_event_by_edge(new_edge)



    def update_with_same_state(self, current_state, new_edge, action, depth, dom_list, url):
        #save trace
        self.trace_history['states'].append(current_state)
        self.trace_history['edges'].append(new_edge)
        #get new event again
        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(current_state, None, depth)

    def update_with_out_of_domain(self, current_state, new_edge, action, depth, dom_list, url):
        #save trace
        self.trace_history['states'].append(current_state)
        self.trace_history['edges'].append(new_edge)
        # back if state out of domain
        logging.info(' |depth:%s state:%s| out of domain: %s', depth, current_state.get_id(), url)
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,current_state.get_id() )
        self.crawler.other_executor_backtrack(current_state, self.other_executor)
        logging.info('==========< BACKTRACK END   >==========')

        #get new event again
        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(current_state, None, depth)

    def update_with_new_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        #save trace
        self.trace_history['states'].append(new_state)
        self.trace_history['edges'].append(new_edge)
        # automata save new state 
        logging.info(' |depth:%s state:%s| add new state %s of : %s', depth, current_state.get_id(), new_state.get_id(), url )
        self.automata.save_state(new_state, depth)
        self.automata.save_state_shot(self.executor, new_state)


        self.check_diff_browser()


        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(new_state, None, depth)

    def update_with_old_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        #save trace
        self.trace_history['states'].append(new_state)
        self.trace_history['edges'].append(new_edge)
        #check if old state have a shorter depth
        if depth < new_state.get_depth():
            new_state.set_depth(depth)
        if depth > new_state.get_depth():
            depth = new_state.get_depth()
        
        if self.trace_length_count < self.configuration.get_max_length():
            self.crawler.add_new_events(new_state, None, depth)

    def save_traces(self):
        self.automata.save_traces(self.traces)

    def end(self):
        self.traces.append( self.trace_history )
        self.trace_length_count = 0
        self.trace_history = {}
        self.other_executor.close()

    def check_difff_browser(self):
        #should not be active
        # 1. check executor other_executor is same state
        # 2. if same , analsis 
        self.analysis_elements( self.executor )
        self.analysis_elements( self.other_executor )

        self.analysis_with_other_browser( self.executor, self.other_executor )

    def analysis_with_other_browser( self,executor, other_executor ):

        if self.executor.get_url()==self.other_executor.get_url():
            print("url is same")

    #def analysis_elements( self,executor ):

        #self.executor.get_screenshot("pic/ana.png")
        #self.executor

#-------------------------------------------------------------------------------------------------------------------
#Cross Browser Testing#-------------------------------------------------------------------------------------------------------------------

#acually it's CBT algorithm
class CBTCrawler(AlgoCrawler):
    def __init__(self,other_browserID,url):
        self.other_browserID = int(other_browserID)
        string='Starting 2nd browser, browser ID is: '+ str(self.other_browserID)
        print(string)
        logging.info(' CBT_events : '+ string )
        #not sure init exe and other_exe together
        #self.executor = executor
        if self.other_browserID != 0 :
            self.other_executor = CBTExecutor(int(self.other_browserID), url)
        else:
            print("single browser")
        

    def set_utility(self, crawler, configuration, executor, automata):
        self.crawler = crawler
        self.configuration = configuration
        self.executor = executor
        self.automata = automata

    def prepare(self):
        #executor
        self.executor.start()
        self.executor.goto_url()
        if self.other_browserID != 0 :
            self.other_executor.start()
            self.other_executor.goto_url()

        #initial state
        initial_state = self.crawler.get_initail_state()

        #should check different browser first
        if self.other_browserID != 0 :
            self.check_diff_browser(initial_state)

        self.crawler.run_script_before_crawl(initial_state)

    def add_new_events(self, state, prev_state, depth):
        for clickables, iframe_key in DomAnalyzer.get_clickables(state, prev_state if prev_state else None):
            for clickable in clickables:
                self.crawler.action_events.append( {
                        'state'  : state,
                        'action' : { 'clickable':clickable, 'iframe_key':iframe_key },
                        'depth'  : depth,
                    } )

    def get_next_action(self, action_events):
        event = action_events.pop()
        return event

    def change_state(self, state, action, depth):
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,state.get_id() )
        print('===change state, start backtrack')
        #will ananlyzing this state,dom is same to the original one
        if self.other_browserID != 0 :
            self.crawler.other_executor_backtrack(state, self.other_executor)
        
        #!!!!!!!!!!!!!!CBT analysis here
        #self.crawler.cbt_is_same_state_dom(self.other_executor )
        #self.check_dom_tree()

        logging.info('==========< BACKTRACK END   >==========')

    def trigger_action(self, state, new_edge, action, depth):
        logging.info(' |depth:%s state:%s| fire element in iframe(%s)', depth, state.get_id(), action['iframe_key'])
        self.crawler.make_value(new_edge)
        self.executor.click_event_by_edge(new_edge)
        if self.other_browserID != 0 :
            self.other_executor.click_event_by_edge(new_edge)

    def update_with_same_state(self, current_state, new_edge, action, depth, dom_list, url):
        # Do Nothing when same state
        return None

    def update_with_out_of_domain(self, current_state, new_edge, action, depth, dom_list, url):
        # back if state out of domain
        logging.info(' |depth:%s state:%s| out of domain: %s', depth, current_state.get_id(), url)
        logging.info('==========< BACKTRACK START >==========')
        logging.info('==<BACKTRACK> depth %s -> backtrack to state %s',depth ,current_state.get_id() )
        if self.other_browserID != 0 :
            self.crawler.other_executor_backtrack(current_state, self.other_executor)
        logging.info('==========< BACKTRACK END   >==========')

    def update_with_new_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        # automata save new state 
        logging.info(' |depth:%s state:%s| add new state %s of : %s', depth, current_state.get_id(), new_state.get_id(), url )

        #save mix pic instead
        self.automata.save_state(new_state, depth)
        self.automata.save_state_shot(self.executor, new_state)



        #!!!!!!!!!!!!!!CBT analysis here
        
        if self.other_browserID != 0 :
            print('===CBT check state')
            self.check_diff_browser(new_state)
        
        #self.check_dom_tree()
        #str = self.crawler.cbt_is_same_state_dom(self.other_executor )
        #pr_str=''.join(str)
        #print(pr_str.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding));
        if depth < self.configuration.get_max_depth():
            self.crawler.add_new_events(new_state, current_state, depth)

    def update_with_old_state(self, current_state, new_state, new_edge, action, depth, dom_list, url):
        #check if old state have a shorter depth
        if depth < new_state.get_depth():
            new_state.set_depth(depth)
            self.crawler.add_new_events(new_state, current_state, depth)

    def save_traces(self):
        self.automata.save_simple_traces()

    def end(self):
        pass

    
    
    def check_diff_browser(self, new_state):
        
        # 0. get photo
        self.compare_screenshot(new_state)
        # 1. check executor other_executor is same state
        #self.automata.save_state_CBT(new_state, depth)
        #self.automata.save_state(new_state, depth)
        # 2. if same , analsis 
        
        self.analysis_with_other_browser()

    
    
    def analysis_with_other_browser( self ):
        # 1. check url is the same or not : should be the same
        # 2. check state is the same or not : should be the same
        
        dom_list1,url1 =self.executor.get_dom_list(self.configuration)
        dom_list2,url2 =self.other_executor.get_dom_list(self.configuration)

        if url1!=url2:
            print ("===different pages")
            logging.info('CBT:browser 1 page:%s browser 2 page:%s| page are different', url1, url2 )
        elif url1==url2:
            string="url is same: "+self.executor.get_url()
            print(string)
            logging.info(' CBT_events : '+ string )
        '''
        if dom_list1==dom_list2:
            string="dom tree is same: "+self.executor.get_url()
            print(string)
            logging.info(' CBT_events : '+ string )
        '''
        if DomAnalyzer.is_equal(dom_list1[0]['dom'],dom_list2[0]['dom']):
            print("===same dom tree")
            logging.info('CBT: same dom tree')
        else:
            print ("===different dom_tree")
            #need domtree mapping
            logging.info('CBT: browser 1 dom:%s browser 2 dom:%s| dom trees are different', url1, url2 )

        log_list1,url1=self.executor.get_log_list(self.configuration)
        log_list2,url2=self.other_executor.get_log_list(self.configuration)

    def compare_screenshot(self, new_state):
        pathPng =self.save_screenshot(self.executor,new_state)
        pathPng2=self.save_screenshot(self.other_executor,new_state)

        #im1 = Image.open( pathPng  )
        #im2 = Image.open( pathPng2 )
        #ims = map(Image.open, [pathPng ,pathPng2])
        ims =[Image.open(pathPng), Image.open(pathPng2)]
        widths,heights =zip(*(i.size for i in ims))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for im in ims:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]        

        pathDIR = os.path.join(self.configuration.get_abs_path('state'), new_state.get_id() + '.png')
        new_im.save(pathDIR)

    #no use
    def check_dom_tree(self):
      
        
        if url1!=url2:
            print ("===different pages")
            logging.info('CBT:browser 1 page:%s browser 2 page:%s| page are different', url1, url2 )
        if DomAnalyzer.is_equal(dom_tree1,dom_tree2):
            print("===same dom tree")
            logging.info('CBT: same dom tree')
        else:
            print ("===different dom_tree")
            #need domtree mapping
            logging.info('CBT: browser 1 dom:%s browser 2 dom:%s| dom trees are different', url1, url2 )
        
    
    def save_screenshot( self, executor , new_state ):
        
        try:
            #make dir for each screen shot
            pathDir = os.path.join(self.configuration.get_abs_path('state'), 'browser_'+str(executor.browserID) )
            pathPng = os.path.join(self.configuration.get_abs_path('state'), 'browser_'+str(executor.browserID), new_state.get_id()+'.png')
            if not os.path.isdir(pathDir):
                os.makedirs(pathDir)

            executor.get_screenshot(pathPng )
        except Exception as e:  
            logging.error(' save screen : %s \t\t__from automata.py save_dom()', str(e))

        return pathPng
    







    