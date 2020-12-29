#!/usr/bin/python2.7

import os
import re
import requests
from optparse import OptionParser
from multiprocessing import cpu_count
import urllib2
from bs4 import BeautifulSoup

def splite_rpm_downlink(down_link):
    """splite rpm down link to list like ['D521816', '010.ali3000', 'kernel-hotfix-D521816-010.ali3000.ecsvm-1.0-1.alios7.x86_64.rpm'
    , "http://yum.tbsite.net/taobao/7/x86_64/current/kernel-hotfix-D521816-012.ali3000/kernel-hotfix-D521816-012.ali3000-1.0-1.alios7.x86_64.rpm"]"""

    list_array=down_link.split("/")
    rpm_name=list_array[-1]
    print rpm_name
    akid=rpm_name.split("-")[2]
    kernel=rpm_name.split("-")[3]
    print akid, kernel, rpm_name, down_link

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-a", "--akid",
                      action="store",  dest="akid",
                      help="rpm akid name for searching",
                      )
    (options, args) = parser.parse_args()

    url = "http://rpm.corp.taobao.com/find.php?q="+options.akid+"&t=&d=0&os="
    req = requests.session()
    response = req.get(url, headers="", verify=False)
    html_test = response.text
    soup = BeautifulSoup(html_test)
    #print soup.prettify()
    #for item in soup.findAll('a'):
    #    print item

    for item in soup.findAll(href=re.compile("^\?t=&")):
        #get rpm link
        rpm_link="http://rpm.corp.taobao.com/find.php?"+item['href']
        response = req.get(rpm_link, headers="", verify=False)
        rpm_html = response.text
        rpm_soup = BeautifulSoup(rpm_html)
        down_link=rpm_soup.findAll(href=re.compile("^http://yum"))[1]
        print down_link['href']
        splite_rpm_downlink(down_link['href'])


