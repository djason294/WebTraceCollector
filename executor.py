#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Test case executor (a.k.a. robot)
"""

import sys, os, time, logging, json,codecs,logging

from abc import ABCMeta, abstractmethod
from dom_analyzer import DomAnalyzer
from configuration import Browser
from bs4 import BeautifulSoup

#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions 
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
#==============================================================================================================================

class Executor():
    __metaclass__ = ABCMeta

    @abstractmethod
    def fire_event(self, clickable):
        pass

    @abstractmethod
    def fill_form(self, clickable):
        pass

    @abstractmethod
    def empty_form(self, clickable):
        pass

    @abstractmethod
    def get_source(self):
        pass

    @abstractmethod
    def get_screenshot(self):
        pass

    @abstractmethod
    def restart_app(self):
        pass

#==============================================================================================================================
#==============================================================================================================================
# Selenium Web Driver
#==============================================================================================================================
class SeleniumExecutor():
    def __init__(self, browserID, url):
        #choose the type of browser
        self.browserID = browserID
        self.driver = None
        #link to the url
        self.startUrl = url
        self.main_window = None

    #==========================================================================================================================
    # START / END / RESTART
    #==========================================================================================================================
    def start(self):
        #在這裡宣告driver
        try:
            if self.browserID == 1:
                self.driver = webdriver.Firefox()
            elif self.browserID == 2:
                self.driver = webdriver.Chrome()
            elif self.browserID == 3:
                self.driver = webdriver.Ie()    
            else: #default in firefox
                print("go into exception in SeleniumExe")
                self.driver = webdriver.Firefox(); 
            self.driver.set_window_size(1280,960)
            self.driver.implicitly_wait(15)
            self.driver.set_page_load_timeout(15)

            self.main_window = self.driver.current_window_handle
        except Exception as e:
            logging.error(' start driver : %s \t\t__from executor.py start()', str(e))

    def refresh(self):
        try:
            self.driver.refresh()
            self.check_after_click()
        except Exception as e:
            logging.error(' refresh : %s \t\t__from executor.py refresh()', str(e))

    def close(self):
        try:
            for handle in self.driver.window_handles:
                self.driver.switch_to_window(handle)
                logging.info(" closing: %s", str(self.driver))
                self.driver.quit()
        except Exception as e:
            logging.error(' close : %s \t\t__from executor.py close()', str(e))

    def restart_app(self):
        self.close()
        self.start()

    #==========================================================================================================================
    # FIRE EVENT
    #==========================================================================================================================
    def click_event_by_edge(self, edge):
        self.switch_iframe_and_get_source( edge.get_iframe_list() )
        self.fill_selects( edge.get_selects() )
        self.fill_inputs_text( edge.get_inputs() )
        self.fill_checkboxes( edge.get_checkboxes() )
        self.fill_radios( edge.get_radios() )
        self.fire_event( edge.get_clickable() )

    def get_element_by_tag(self, element):
        if element.get_id() and not element.get_id().startswith(DomAnalyzer.serial_prefix):
            return self.driver.find_element_by_id( element.get_id() )
        elif element.get_xpath():
            return self.driver.find_element_by_xpath( element.get_xpath() )
        else:
            return None

    def fire_event(self, clickable):
        logging.info(' fire_event: id(%s) xpath(%s)', clickable.get_id(), clickable.get_xpath())
        try:
            element = self.get_element_by_tag(clickable)
            if not element:
                raise ValueError('No id nor xpath for an clickable')
            element.click()
            self.check_after_click()
        except Exception as e:
            logging.error(' Unknown Exception: %s in fire_event: id(%s) xpath(%s) \t\t__from executor.py fire_event()',str(e), clickable.get_id(), clickable.get_xpath())
                
    def fill_inputs_text(self, inputs):
        for input_field in inputs:
            try:
                element = self.get_element_by_tag(input_field)
                if not element:
                    raise ValueError('No id nor xpath for an input field')
                element.clear()
                element.send_keys(input_field.get_value())
                self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in input: id(%s) xpath(%s) \t\t__from executor.py fill_inputs_text()',str(e), input_field.get_id(), input_field.get_xpath())
                
    def fill_selects(self, selects):
        for select_field in selects:
            try:
                element =  Select( self.get_element_by_tag(select_field) )
                if not element:
                    raise ValueError('No id nor xpath for an select field')
                element.select_by_index( int(select_field.get_selected()) )
                self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in select: id(%s) xpath(%s) \t\t__from executor.py fire_event()',str(e), select_field.get_id(), select_field.get_xpath())
                
    def fill_checkboxes(self, checkboxes):
        for checkbox_field in checkboxes:
            try:
                checkbox_list = checkbox_field.get_checkbox_list()
                #clear all
                for checkbox in checkbox_list:
                    element = self.get_element_by_tag(checkbox)
                    if not element:
                        raise ValueError('No id nor xpath for an checkbox')
                    if element.is_selected():
                        element.click()
                        self.check_after_click()
                for selected_id in checkbox_field.get_selected_list():
                    selected_element = self.get_element_by_tag( checkbox_list[int(selected_id)] )
                    if not selected_element:
                        raise ValueError('No id nor xpath for an checkbox')
                    selected_element.click()
                    self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in checkbox: name(%s) \t\t__from executor.py fire_event()'\
                    %( str(e), checkbox_field.get_checkbox_name() ) )
                
    def fill_radios(self, radios):
        for radio_field in radios:
            try:
                selected_id = int(radio_field.get_selected())
                radio_list = radio_field.get_radio_list()
                element = self.get_element_by_tag( radio_list[selected_id] )
                if not element:
                    raise ValueError('No id nor xpath for an radio')
                if not element.is_selected():
                    element.click()
                self.check_after_click()
            except Exception as e:
                logging.error(' Unknown Exception: %s in radio: name(%s) \t\t__from executor.py fire_event()'\
                    % ( str(e), radio_field.get_radio_name() ) )
                
    #==========================================================================================================================
    # GO ON / BACK
    #==========================================================================================================================
    def goto_url(self):
        try:
            self.driver.get(self.startUrl)
        except Exception as e:
            logging.error(' driver get url : %s \t\t__from executor.py goto_url()', str(e))

    def back_history(self):
        print('back from',self.browserID)
        try:
            time.sleep(1)
            self.driver.back()
            self.check_after_click()
        except Exception as e:
            logging.error(' back : %s \t\t__from executor.py back_history()', str(e))
            self.driver.get(self.startUrl)

    def forward_history(self):
        try:
            time.sleep(1)
            self.driver.forward()
            self.check_after_click()
        except Exception as e:
            logging.error(' forward : %s \t\t__from executor.py forward_history()', str(e))

    #==========================================================================================================================
    # GET ELEMENT / GET INFOMATION
    #==========================================================================================================================
    def get_url(self):
        try:
            return self.driver.current_url
        except Exception as e:
            logging.error(' get url : %s \t\t__from executor.py get_url()', str(e))
            return 'error url'

    def get_source(self):
        try:
            text = self.driver.page_source
        except Exception as e:
            logging.error(' %s \t\t__from executor.py get_source()', str(e))
            text = "ERROR! cannot load file"
        return text.encode('utf-8')

    def switch_iframe_and_get_source(self, iframe_xpath_list=None):
        try:
            self.driver.switch_to_default_content()
            if iframe_xpath_list and iframe_xpath_list[0] != 'None':
                for xpath in iframe_xpath_list:        
                    iframe = self.driver.find_element_by_xpath(xpath)
                    self.driver.switch_to_frame(iframe)
        except Exception as e:
            logging.error(' switch_iframe : %s \t\t__from executor.py switch_iframe_and_get_source()', str(e))
        return self.get_source()

    def get_screenshot(self, file_path):
        self.driver.get_screenshot_as_file(file_path)

    def get_log(self,pathDir):
        #save dom of iframe in list of StateDom [iframe_path_list, dom, url/src, normalize dom]
        if not os.path.exists(pathDir):
            os.makedirs(pathDir)        
        file_path = os.path.join(pathDir,'browser_'+str(self.browserID)+'.json')
        url = self.get_url()
        log_list = {'url': url,'filepath': file_path,'log':[]}

        try:
            for entry in self.driver.get_log('browser'):
                print(entry)
                log_list['log'].append(entry)
        except Exception as e:
            print(str(e))
        with codecs.open( file_path,'w', encoding='utf-8' ) as f:
            json.dump(log_list, f, indent=3, sort_keys=True, ensure_ascii=False)
        print('===log record finished')
        return log_list

    def get_coor(self,pathDir):
        #save dom of iframe in list of StateDom [iframe_path_list, dom, url/src, normalize dom]
        print("===get coor")
        if not os.path.exists(pathDir):
            os.makedirs(pathDir)        
        file_path = os.path.join(pathDir,'browser_'+str(self.browserID)+'.json') 
        url = self.get_url()
        coor_list = {'url': url,'filepath': file_path,'elements':[]}
        element_list=self.driver.find_elements_by_xpath('//*[@id]')
        for i in element_list:
            single_element={
                'element_id'    :str(i),
                'tag_name'      :str(i.tag_name),
                #'x_path'        :i.x_path
                'type'    :"none",
                'name'     :"none",
                'coor':{
                    'x'         :i.location['x'],
                    'y'         :i.location['y'],
                },
                'size':{
                    'height'    :i.size['height'],
                    'width'     :i.size['width'],                   
                },
            }
            store_single_element = False
            #tagname = id, select, a,list
            for j in ['id']:
                if  i.get_attribute(j)!=None and i.get_attribute(j)!="":
                    single_element['type'] = j
                    single_element['name'] = i.get_attribute(j)
                    store_single_element=True
            if store_single_element == True:
                coor_list['elements'].append(single_element)
                
        with codecs.open( file_path,'w', encoding='utf-8' ) as f:
            json.dump(coor_list, f, indent=2, sort_keys=True, ensure_ascii=False)
        print('===coor record finished')
        return coor_list

    def get_dom_list(self, configuration):
        #save dom of iframe in list of StateDom [iframe_path_list, dom, url/src, normalize dom]
        dom_list = []
        new_dom = self.switch_iframe_and_get_source()

        url = self.get_url()
        soup = BeautifulSoup(new_dom, 'html5lib')
        for frame in configuration.get_frame_tags():
            for iframe_tag in soup.find_all(frame):
                iframe_xpath = DomAnalyzer._get_xpath(iframe_tag)
                iframe_src = iframe_tag['src'] if iframe_tag.has_attr('src') else None
                try: #not knowing what error in iframe_tag.clear(): no src
                    if configuration.is_dom_inside_iframe():
                        self.get_dom_of_iframe(configuration, dom_list, [iframe_xpath], iframe_src)
                    iframe_tag.clear()
                except Exception as e:
                    logging.error(' get_dom_of_iframe: %s \t\t__from crawler.py get_dom_list() ', str(e))
        dom_list.append( {
                'url' : url,
                'dom' : str(soup),
                'iframe_path' : None,
            } )
        brID=self.browserID

        return dom_list, url

    def get_dom_of_iframe(self, configuration, dom_list, iframe_xpath_list, src):
        dom = self.switch_iframe_and_get_source(iframe_xpath_list)
        soup = BeautifulSoup(dom, 'html5lib')
        for frame in configuration.get_frame_tags():
            for iframe_tag in soup.find_all(frame):
                iframe_xpath = DomAnalyzer._get_xpath(iframe_tag)
                iframe_xpath_list.append(iframe_xpath)
                iframe_src = iframe_tag['src'] if iframe_tag.has_attr('src') else None
                try:
                    self.get_dom_of_iframe(configuration, dom_list, iframe_xpath_list, iframe_src)      
                    iframe_tag.clear()
                except Exception as e:
                    logging.error(' get_dom_of_iframe: %s \t\t__from crawler.py get_dom_list() ', str(e))
        dom_list.append( {
                'url' : src,
                'dom' : str(soup),
                'iframe_path' : iframe_xpath_list,
            } )

    

    #==========================================================================================================================
    # CHECK 
    #==========================================================================================================================
    def check_after_click(self):
        time.sleep(1)
        self.check_alert()
        self.check_window()
        self.check_tab()
        self.driver.find_element_by_xpath("html/body").click()
        time.sleep(0.1)

    def check_alert(self):
        no_alert = False
        while not no_alert:
            try:
                alert = self.driver.switch_to_alert()
                logging.info(' click with alert: %s ', alert.text)
                alert.dismiss()
            except Exception:
                no_alert = True

    def check_window(self):
        if len(self.driver.window_handles) > 1:
            logging.info(' more than one window appear')
            for handle in self.driver.window_handles:
                if handle != self.main_window:
                    self.driver.switch_to_window(handle)
                    logging.info(" closing: %s", str(self.driver))
                    self.driver.close()
            self.driver.switch_to_window(self.main_window)

    def check_tab(self):
        pass

#==============================================================================================================================

class CBTExecutor(SeleniumExecutor):
    #原本 executer 的 initial 方式
    def __init__(self, browserID, url):
        #choose the type of browser
        self.browserID = browserID
        #link to the url
        self.startUrl = url
        self.main_window = None
        self.detail_element_list = []
        

    #原本的Page 既成方式
    '''
    def __init__(self,driver_num,Driver):
        self.Driver=Driver
        self.driver=Driver.driver
        self.url=self.driver.current_url
        self.title=self.driver.title
        
        self.dom_list=self.driver.page_source       
        self.type_tuple='id','class','a'        
        self.element_list=[]   

        #self.id_list=driver.find_elements_by_xpath('//*[@id]')
        #self.class_list = driver.find_elements_by_xpath('//*[@class]')
        
        
        #<id="QQ">
        #detail_element_list['e_list']="QQ"
        #detail_element_list['type_tuple']='id'
        
        self.detail_element_list = []
    '''
      

    def get_element_property(self):
        self.element_list=self.driver.find_elements_by_xpath('//*')
        for i in self.element_list:
            info={
                'element'       :i,
                'tag_name'      :i.tag_name,
                #'x_path'        :i.x_path
                'type_tuple'    :[],
                'name_list'     :[],

                'coor':{
                    'x'         :i.location['x'],
                    'y'         :i.location['y'],
                },
                'size':{
                    'height'    :i.size['height'],
                    'width'     :i.size['width'],                   
                },
            }
            store_info=False
            for j in self.type_tuple:
                if i.get_attribute(j)!=None and i.get_attribute(j)!="":
                    info['type_tuple'].append(j)
                    info['name_list'].append(i.get_attribute(j))
                    store_info=True
            if store_info == True:
                self.detail_element_list.append(info)
                    
        return self.detail_element_list                   

    def print_detail_element_list(self):
        for i in self.detail_element_list:
            print ("element:"        ,i['element'])
            #print "xpath:"          ,i['xpath']   
            for j in range(0,len(i['name_list']),1):
                print (i['type_tuple'][j],"=",i['name_list'][j])
            print ("coor:"           ,i['coor']['x']        ,i['coor']['y'])
            print ("size:"           ,i['size']['height']   ,i['size']['width'])
    
    def get_element_attribute(self):
        for i in self.detail_element_list:
            if i['coor']['true_x'].find("%")!=-1:
                print ("define by percentage :",i['type'],'=',i['name'])
            if i['coor']['true_x'].find("px")!=-1:
                print ("define by pixel      :",i['type'],'=',i['name'])

    def get_element_screenshot(self):
        print('===screenshot & elementshot')
        self.driver.get_screenshot_as_file('scr/scr.png')     
        for i in self.detail_element_list:
            im      = Image.open('scr/scr.png')
            left    = i['coor']['x']
            top     = i['coor']['y']
            right   = i['coor']['x'] + i['size']['width']
            bottom  = i['coor']['y'] + i['size']['height']
            im      = im.crop((left, top, right, bottom)) # defines crop points
            im.save('scr/'+i['name_list'][0]+'.png') # saves new cropped image
        return 0
