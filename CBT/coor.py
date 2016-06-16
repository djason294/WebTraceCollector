import os,time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image

def screenshot(obj):
    driver.save_screenshot('scr/scr.png')
    for j in range(0,len(obj),1):
        e.append(driver.find_element_by_id(obj[j]))
        im = Image.open('scr/scr.png')
        left = e[j].location['x']
        top = e[j].location['y']
        right = e[j].location['x'] + e[j].size['width']
        bottom = e[j].location['y'] + e[j].size['height']
        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save('scr/scr'+obj[j]+'.png') # saves new cropped image

def print_ele(obj):
    for j in range(0,len(obj),1):
        e.append(driver.find_element_by_id(obj[j]))
        print obj[j],' location:',e[j].location['x'],',',e[j].location['y']
        print obj[j],' size:',e[j].size['width'],',',e[j].size['height']

def screen_chk(obj):
    b_size=driver.get_window_size()
    chk=0
    print 'screen check,in screen or out screen:'
    for j in range(0,len(obj),1):
        e.append(driver.find_element_by_id(obj[j]))
        if e[j].location['x']+e[j].size['width']>b_size['width']:
            print '!!!',obj[j],'\'s width is out of screen by',e[j].location['x']+e[j].size['width']-b_size['width']
            chk=1
        if e[j].location['y']+e[j].size['height']>b_size['height']:
            print '!!!',obj[j],'\'s height is out of screen by',e[j].location['y']+e[j].size['height']-b_size['height']
            chk=1
    if chk==0:
        print 'nothing out of screen, screen check end.'

def cover_chk(obj):
    chk=0
    print 'cover check,elements cover each other or not:'
    for j in range(0,len(obj),1):
        e.append(driver.find_element_by_id(obj[j]))
        for k in range(j,len(obj),1):
            if j != k : #prevent from crawling same object / elements
                x_cover=0;
                y_cover=0;
                
                if (e[j].location['x']<=e[k].location['x']) and (e[j].location['x']+e[j].size['width']>e[k].location['x']):
                    x_cover=1 
                elif (e[j].location['x']<e[k].location['x']+e[k].size['width']) and (e[j].location['x']+e[j].size['width']>=e[k].location['x']+e[k].size['width']):
                    x_cover=1
                elif (e[j].location['x']>=e[k].location['x']) and (e[j].location['x']+e[j].size['width']<=e[k].location['x']+e[k].size['width']):
                    x_cover=1
                elif (e[j].location['x']<=e[k].location['x']) and (e[j].location['x']+e[j].size['width']>=e[k].location['x']+e[k].size['width']):
                    x_cover=1     
                if (e[j].location['y']<=e[k].location['y']) and (e[j].location['y']+e[j].size['height']>e[k].location['y']):
                    y_cover=1 
                elif (e[j].location['y']<e[k].location['y']+e[k].size['height']) and (e[j].location['y']+e[j].size['height']>=e[k].location['y']+e[k].size['height']):
                    y_cover=1
                elif (e[j].location['y']>=e[k].location['y']) and (e[j].location['y']+e[j].size['height']<=e[k].location['y']+e[k].size['height']):
                    y_cover=1
                elif (e[j].location['y']<=e[k].location['y']) and (e[j].location['y']+e[j].size['height']>=e[k].location['y']+e[k].size['height']):
                    y_cover=1    
               
                if (x_cover==1) and (y_cover==1):
                    print '!!! obj: ',obj[j],' and obj: ',obj[k],' cover each other.please check!!!'
                    chk=1
                if chk==0:
                    print 'obj: ',obj[j],' and obj: ',obj[k],' nothing cover each other.'
    if chk==0:
       print 'nothing cover each other, cover check end.'

# enable browser logging
d = DesiredCapabilities.FIREFOX
d['loggingPrefs'] = {'browser': 'ALL'}
driver = webdriver.Firefox(capabilities=d)
#driver = webdriver.Chrome(desired_capabilities=d)
#driver = webdriver.Ie()
driver.get('http://www.m.pchome.com.tw/')
#driver.get('http://stackoverflow.com/questions/4681072/selenium-how-to-turn-on-firebug-with-console-script-and-net?lq=1')
print driver.title


print 'get browser size',driver.get_window_size()
print 'get browser position',driver.get_window_position()


obj=[]
e=[]
location=[]
size=[]

#crawling part
obj.append('header_banner')
obj.append('header_linkBar')

print_ele(obj)
screen_chk(obj)
cover_chk(obj)
print 'mission end'

#print
#print len(driver.get_log('browser'))
#{u'timestamp': 1407591650751, u'message': u"Expected ':' but found '}'.  Declaration dropped.", u'level': u'WARNING'}

time.sleep(2) # Let the user actually see something!
print 'narrow window testing'
driver.set_window_size(50,50)


screenshot(obj)
print_ele(obj)
screen_chk(obj)
cover_chk(obj)
time.sleep(2)

driver.quit()

