import json
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from page import Driver,Page

page =[]
for i in range(0,3,1):
	dr =Driver(i)
	dr.print_driver_name()
	dr.open_page('http://54.186.124.111/test/ctest.html')
	dr.print_driver_size()
	
	page.append(Page(i,dr))
	print page[i].get_title()
	print page[i].get_url()
	#get all element
	print 'element testing'
	print page[i].get_dom_list()
	page[i].get_element_property()
	page[i].print_detail_element_list()
	page[i].get_element_screenshot()
	dr.get_screenshot()
	dr.quit_driver()

for i in range(0,3,1):
	for j in range(i,3,1):
		print i,j
		page[i].compare_coor(page[j])





