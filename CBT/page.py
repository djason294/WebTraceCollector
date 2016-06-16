import os,time
from selenium import webdriver
from bs4 import BeautifulSoup
from PIL import Image

class Driver:
    def __init__(self,driver_num):
        self.browser_tuple=('Firefox','Chrome','Ie')
        self.driver_name=self.browser_tuple[driver_num]
        self.driver_num=driver_num

        if self.driver_num==0:
            self.driver=webdriver.Firefox()
        elif self.driver_num==1:
            self.driver=webdriver.Chrome()
        elif self.driver_num==2:
            self.driver=webdriver.Ie()

        self.driver.set_window_position(0,0)
        self.driver.set_window_size(300,240)
        self.driver_size=self.driver.get_window_size()    


    def print_driver_name(self):
        print self.driver_name

    def open_page(self,url):
        self.driver.get(url)

    def set_window_size(self,x,y):
        self.driver.set_window_size(x,y)
        self.driver_size=self.driver.get_window_size()
        return 0;

    def get_window_size(self):
        return self.driver_size

    def print_driver_size(self):
        print 'width:',self.driver_size['width'],',height:',self.driver_size['height']
        return 0

    def change_driver_size(self,width,height):
        self.driver_size=self.driver.set_window_size(width,height)


    def get_screenshot(self,file_name=None):
        if file_name is None:
            file_name = self.driver_name
        self.driver.save_screenshot('scr/'+file_name+'.png')

    def quit_driver(self):
        self.driver.quit()


class Page:
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
        
        '''
        <id="QQ">
        detail_element_list['e_list']="QQ"
        detail_element_list['type_tuple']='id'
        '''
        self.detail_element_list = []
        
    def get_url(self):
        return self.url

    def get_title(self):
        return self.title
    
    def get_dom_list(self):
        return self.dom_list

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
            print "element:"        ,i['element']
            #print "xpath:"          ,i['xpath']   
            for j in range(0,len(i['name_list']),1):
                print i['type_tuple'][j],"=",i['name_list'][j]
            print "coor:"           ,i['coor']['x']        ,i['coor']['y']
            print "size:"           ,i['size']['height']   ,i['size']['width']
    
    def get_element_attribute(self):
        for i in self.detail_element_list:
            if i['coor']['true_x'].find("%")!=-1:
                print "define by percentage :",i['type'],'=',i['name']
            if i['coor']['true_x'].find("px")!=-1:
                print "define by pixel      :",i['type'],'=',i['name']

    def get_element_screenshot(self):
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

    def compare_coor(self, Page):
        for i in self.detail_element_list:
            ele_to_compare = Page.find_element_by_xpath(i['xpath'])
            if i['coor']['x'] != ele_to_compare['coor']['x']:
                print "x coor not equal"


        return 0

    '''
    # get dom by source
    def get_dom_list(self):
        soup = BeautifulSoup(self.dom, 'html5lib')
        dom_list.append( StateDom(None, str(soup), url) )
        return dom_list, url
    '''
