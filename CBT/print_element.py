import json
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


#from page import Page
def element_property(feature,list):
    counter=1;
    for i in list:
        print "number   :" , counter
        print "feature  :" , (i.get_attribute(feature))
        style = i.get_attribute('style')
        print "style    :" , (style)
        style_m=style.split(";")
        for j in style_m:
            if j.find("%")!=-1:
                print "define by percentage :",j
            if j.find("px")!=-1:
                print "define by pixel      :",j

        #print "onclick: " , (i.get_attribute('onclick'))
        #print "btn:     " , (i.get_attribute('btn'))
        counter=counter+1
    return 0

driver = webdriver.Firefox()

driver.get('http://54.186.124.111/test/ctest.html')
print driver.title



#get all class element
get_class = driver.find_elements_by_xpath('//*[@class]')
element_property('class',get_class)


#get all id element
print 'element testing'
get_id = driver.find_elements_by_xpath('//*[@id]')
element_property('id',get_id)

driver.quit()






