import pymysql.cursors, time,re, requests, random, os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep

database = ""
pwd = ""
fbuser = ""
fbpwd = ""
f = open("credentials.txt","r")
if f.mode == 'r':
   database = f.readline()
   pwd = f.readline()
   fbuser = f.readline()
   fbpwd = f.readline()

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user=database.rstrip(" \n"),
                             password=pwd.rstrip(" \n"),
                             db=database.rstrip(" \n"),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
mycursor = connection.cursor()
try:

   with connection.cursor() as cursor:
      # get data here
      #populate clubs of each department
      clubs = {}
      url = "http://www.cosam.calpoly.edu/content/student_orgs"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for item in  soup.find('h2', attrs={'id':'Statistics_Department'}).find_next_siblings('h3'):
         name = re.sub(r'\(.*\)','',item.a.string.strip(" \n\t"))
         name = re.sub(r'Cal Poly','',name)
         clubs[name.strip(" \n\t")] = {}
         clubs[name.strip(" \n\t")]['homepage'] = item.a['href']
         clubs[name.strip(" \n\t")]['dep'] = 'STAT'
      url = "https://engineering.calpoly.edu/student-clubs-organizations"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for item in soup.find_all('div', class_='accordion'):
         if item.find('div').h2.string == 'Computer Science & Software Engineering':
            for tr in item.find('table').tbody.find_all('tr'):
                tds = tr.find_all('td')
                name = re.sub(r'\(.*\)','',tds[0].string.strip(" \n\t"))
                name = re.sub(r'Cal Poly','',name)
                clubs[name.strip(" \n\t")] = {}
                clubs[name.strip(" \n\t")]['homepage']= tds[1].a['href']
                clubs[name.strip(" \n\t")]['dep'] = 'CSSE'
      clubs['Roborodentia Club'] = {'dep':'CSSE','homepage':'http://roborodentia.calpoly.edu/'}
      url = "https://www.asi.calpoly.edu/club_directories/listing_bs"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('li', class_="row club_list"):
         name = i.span.a.get_text().strip(" \n\t")
         name = re.sub(r', Cal Poly','',name)
         if name in clubs:
            fee = 'No'
            if len(i.find('span',class_='contribute').find_all('a')) > 0:
               fee = 'Yes'
            span = i.div.find_all('span')
            sqlpeople = "insert into clubXpeople (person, phoneNum, email, position, club) values (%s, %s, %s, %s, %s)"
            pres = (span[1].get_text().strip(" \n\t"), span[3].get_text().strip(" \n\t"), span[5].get_text().strip(" \n\t"), 'President', name)
            ad = (span[7].get_text().strip(" \n\t"), span[9].get_text().strip(" \n\t"), span[11].get_text().strip(" \n\t"), 'Advisor', name)
            mycursor.execute(sqlpeople, pres)
            mycursor.execute(sqlpeople,ad)
            connection.commit()
            college = span[15].get_text().strip(" \n\t")
            college = re.sub(r', College of','',college)
            box = int(span[13].get_text().strip(" \n\t"))
            ctype = span[17].get_text().strip(" \n\t")
            des = span[19].get_text().strip(" \n\t")
            email= span[21].get_text().strip(" \n\t")
            club = (name, clubs[name]['dep'], box, college, ctype, des, email, clubs[name]['homepage'], fee)
            sqlclub = "insert into club (name, department, box, college, type, description, email, homepage, fee) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            mycursor.execute(sqlclub, club)
            connection.commit()

      #fb accounts -- added manually because these could not be found on homepages etc.
      sqlsocial = "insert into clubXsocialmedia (club, type, page, open) values (%s, %s, %s, %s)"
      social = {}
      social['Association for Computing Machinery'] ={'Facebook':'https://www.facebook.com/groups/cpacm/', 'Instagram':'calpoly.acm','FBopen':'yes'}
      social['Data Science Club']={'Facebook':'https://www.facebook.com/groups/892660674182504/', 'FBopen':'yes'}
      social['Game Development Club']= {'Facebook':'https://www.facebook.com/CPGameDev/', 'FBopen':'no'}
      social['Linux Users Group']={'Facebook':'https://www.facebook.com/groups/calpolylug/', 'FBopen':'yes'}
      social['SLO Hacks'] = {'Facebook':'https://www.facebook.com/slohacks/', 'Instagram':'slo_hacks','FBopen':'no'}
      social['STAT Club'] = {'Facebook':'https://www.facebook.com/groups/calpolystatclub/', 'FBopen':'yes'}
      social['White Hat']= {'Facebook':'https://www.facebook.com/groups/whitehatcalpoly/', 'FBopen':'yes'}
      social['Women Involved in Software and Hardware']={'Instagram':'wishcalpoly','Facebook':'https://www.facebook.com/groups/WISHcalpoly/', 'FBopen':'yes'}

      url = "https://www.facebook.com/"
      options = Options()
      options.headless = True
      driver = webdriver.Firefox(options=options)
      driver.get(url)
      sleep(1) 
  
      username_box = driver.find_element_by_id('email') 
      username_box.send_keys(fbuser) 
      sleep(1) 
      password_box = driver.find_element_by_id('pass') 
      password_box.send_keys(fbpwd) 
      login_box = driver.find_element_by_id('loginbutton') 
      login_box.click()

      for c in social.keys():
         if 'Facebook' in social[c]:
            tuplesocial = (c, 'Facebook', social[c]['Facebook'], social[c]['FBopen'])
            mycursor.execute(sqlsocial, tuplesocial)
            if social[c]['FBopen'] == 'yes':
               driver.get(social[c]['Facebook'] + "about/")
               sleep(1)
               soup = BeautifulSoup(driver.page_source, "html.parser")  
               activity = soup.find(text="Activity").parent.parent.next_sibling
               posts = soup.find(text=re.compile("New posts? today"))
               postsToday =posts.parent.previous_sibling.get_text().replace(',','')
               postsMonth=posts.parent.next_sibling.get_text().replace(' in the last 30 days', '').replace(',','')
               mem = activity.find(text="Members")
               memTot=mem.parent.previous_sibling.get_text().replace(',','')
               memMonth=mem.parent.next_sibling.get_text().replace(' in the last 30 days', '').replace(',','')
               mycursor.execute("insert into clubFBxActivity (club, postsToday, postsMonth, members, joinedInMonth) values (%s, %s, %s, %s, %s)", (c, postsToday, postsMonth, memTot, memMonth))

         if 'Instagram' in social[c]:
            tuplesocial = (c, 'Instagram', social[c]['Instagram'],None)
            mycursor.execute(sqlsocial, tuplesocial)
            urlIG = 'https://www.instagram.com/' + social[c]['Instagram']
            myRequest = requests.get(urlIG)
            soup = BeautifulSoup(myRequest.text,"html.parser")
            info=soup.find_all('meta', content = re.compile('.*Followers,.*'))[0]['content']
            m= re.compile('(\d*) Followers, (\d*) Following, (\d*) Posts.*')
            g = m.match(info)
            sqlIG = "insert into clubIGxInfo (name, followers, following, posts) values (%s, %s, %s, %s)"
            mycursor.execute(sqlIG, (c, g.group(1), g.group(2), g.group(3)))
      connection.commit()
      driver.quit() 

      # lets get info for officers --> every club hp is different, so got scrape each differently
      #ACM - only hs fb

      #Data Science - only has fb

      #Game Dev - events, officers, and projects
      url = "http://www.cpgd.org/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      meet = soup.find(text=re.compile(".*meetings.*")).parent.parent.find_all('b')
      time =meet[0].get_text().strip(" \n\t.")
      loc=meet[1].get_text().strip(" \n\t.")
      mycursor.execute("insert into clubXevent (event, date, location, club) values (%s, %s, %s, %s)", ('meeting', time, loc, 'Game Development Club'))
      events = soup.find_all('h3', class_='post-title')
      dates =  soup.find_all('h2', class_='date-header')
      x = -1
      for i in events:
          x = x + 1
          mycursor.execute("insert into clubXevent (event, date, location, club) values (%s, %s, %s, %s)", (i.a.get_text(), dates[x].span.get_text(), None, 'Game Development Club'))
      for i in soup.find(text=re.compile("Officers.*")).parent.next_sibling.next_sibling.find_all('li'):
          s = i.get_text().strip().split("(")
          person = s[0].strip()
          pos = s[1][0:s[1].find(")")]
          mycursor.execute("insert into clubXpeople (person, position, club) values (%s, %s, %s)", (person, pos, 'Game Development Club'))
      url = "https://github.com/CalPolyGameDevelopmentClub/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('a', itemprop="name codeRepository"):
          proj = i.get_text().strip()
          mycursor.execute("insert into clubXproject (club, project) values (%s, %s)" , ('Game Development Club', proj))
      connection.commit()

      # Linux User group -meetings and projects, resources
      url = "http://cplug.org/projects.html"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('header', class_='major'):
          mycursor.execute("insert into clubXproject (club, project) values (%s, %s)" , ('Linux User Group', i.h1.get_text().strip()))
          for x in i.next_sibling.next_sibling.get_text().replace("Skills Developed:", '').strip().split(","):
              mycursor.execute("insert into clubXresource (club, resource) values (%s, %s)", ('Linux User Group', x))

      # hard coded events for now since there is no tables etc to pull this info
      mycursor.execute("insert into clubXevent (event, date, club) values (%s, %s, %s)", ('meeting', 'Every other Saturday', '20-124'))
      mycursor.execute("insert into clubXevent (event, date, club) values (%s, %s, %s)", ('Facebook Tech Talk', 'October 11th', 'lobby of building 20A'))
      connection.commit()

      # Roborodentia -  officers
      url = "http://roborodentia.calpoly.edu/staff/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      n = 1
      name = ''
      pos = ''
      email = ''
      for i in soup.find_all('td'):
         if n % 3 == 1:
            name = i.a.get_text().strip()
         if n%3 == 2:
            pos = i.get_text().strip()
         if n%3 == 0:
            email = i.a.get_text().strip().replace('(place an \'at\' sign here)', '@')
            mycursor.execute("insert into clubXpeople (person, position, email,club) values (%s,%s, %s, %s)", (name, pos, email,'Roborodentia'))
         n= n+1
      #SLO-hacks - sponsors, projects (tracks), past events
      url = "https://www.slohacks.com/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('a', class_= re.compile('src-components----SponsorLogos-module.*')):
          mycursor.execute("insert into clubXsponsor (club, sponsor) values (%s, %s)", ('SLO Hacks', i.img['alt']))
      for i in soup.find_all('div', class_='src-components----Tracks-module---trackContainer---1ce7n'):
          proj = ""
          for x in i.find_all('h2'): 
              proj = proj + x.get_text()
          mycursor.execute("insert into clubXproject (club, project) values (%s, %s)" ,('SLO Hacks', proj))
      url = "https://www.slohacks.com/club/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('h3'):
          date = i.get_text()
          for x in i.next_sibling.find_all('h4'):
              event = x.get_text()
              mycursor.execute("insert into clubXevent (event, date, club) values (%s, %s, %s)", (event, date, 'SLO Hacks'))

      # STAT Club - officer info 
      url = "https://statistics.calpoly.edu/content/statclub"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find('h2', id= 'STATClub_Officers').next_sibling.next_sibling.find_all('li'):
          strs = i.get_text().split(":")
          mycursor.execute("insert into clubXpeople (person, position, club) values (%s, %s, %s)", (strs[1].strip(), strs[0].strip(), 'STAT club'))

      connection.commit()
 
      # White hat - officers, projects, resources
      url = "https://thewhitehat.club/officers"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      mycursor.execute("insert into clubXevent (club, event, location) values (%s, %s, %s)", ('White Hat','meeting',soup.find(text=re.compile('.*lab.*')).parent.next_sibling.next_sibling.get_text()))
      for i in soup.find_all('div', class_='officer-item'):
          mycursor.execute("insert into clubXpeople (person, position, club) values (%s, %s, %s)", (i.div.h4.get_text(), i.div.h3.strong.get_text(), 'White Hat'))
      url = "https://thewhitehat.club/resources"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('div', class_='resources-group'):
          for x in i.find_all('a'):
              mycursor.execute("insert into clubXresource (club, resource) values (%s, %s)", ('White Hat', x.get_text()))
      url = "https://github.com/WhiteHatCP/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('a', itemprop="name codeRepository"):
          proj = i.get_text().strip()
          mycursor.execute("insert into clubXproject (club, project) values (%s, %s)" , ('White Hat', proj))
      connection.commit()

      #WISH
      url = "https://web.calpoly.edu/~wish/pages/officers.html"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      for i in soup.find_all('h3'):
         strs = i.get_text().split("\n")
         tuplep=(strs[0].strip(), strs[2].strip(), 'Women Involved in Software and Hardware')
         mycursor.execute("insert into clubXpeople (person, position, club) values (%s, %s, %s)", tuplep)
      connection.commit()

      # STAT tutoring - unfortunately only pdfs and pics to get info from
      mycursor.execute("insert into tutoringXurl (department, infoType, url) values (%s, %s, %s)", ("STAT", "day, time, location", "https://statistics.calpoly.edu/content/tutoring"))
      mycursor.execute("insert into tutoringXurl (department, infoType, url) values (%s, %s, %s)", ("STAT", "private tutoring", "https://content-calpoly-edu.s3.amazonaws.com/statistics/1/documents/Tutoring/Winter%202019%20-%20Private%20Tutors.pdf"))
      
      # data assist
      url = "http://guides.lib.calpoly.edu/c.php?g=261982&p=5144949"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      n = 1
      name = ''
      subj = ''
      for i in soup.find_all('td', class_='ck_border'):
         if n % 2 == 1:
            text = i.get_text().split('-')
            name = text[1].strip()
            subj = text[0].strip()
         if n % 2 == 0:
            time = i.get_text().strip().replace('\n', ' ')
            mycursor.execute("insert into dataXtutoring (subject, person, datetime, location) values (%s, %s, %s, %s)", (subj, name, time, 'Kennedy Library Rm 111'))
         n += 1
      connection.commit()

      # csse tutoring
      mycursor.execute("insert into tutoringXurl (department, infoType, url) values (%s, %s, %s)", ("CSSE", "schedule", "http://tutoring.csc.calpoly.edu/schedule/"))
      url = "http://tutoring.csc.calpoly.edu/schedule/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      text = soup.find(text="Tutoring Center Hours").parent.next_sibling.next_sibling.get_text().strip().replace('\n', ' ')
      m= re.compile('The tutoring center is held in (.*), and is offered\s*(.*) starting the second full week of the quarter.\s*Tutoring is held from (.*). Tutoring .*')
      g = m.match(text)
      building = g[1].strip()
      days = g[2].strip()
      time = g[3].strip()
      mycursor.execute("insert into csseTutoringXinfo (typeOfInfo, info) values (%s, %s)", ("location", building))
      mycursor.execute("insert into csseTutoringXinfo (typeOfInfo, info) values (%s, %s)", ("tutoring days", days))
      mycursor.execute("insert into csseTutoringXinfo (typeOfInfo, info) values (%s, %s)", ("tutoring time", time))

      url = "http://tutoring.csc.calpoly.edu/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      text = soup.find(text="Want to be a Tutor?").parent.next_sibling.next_sibling.get_text().strip()
      text=re.sub(r'\s+', ' ', text).strip()
      m= re.compile('If you\'ve passed (.*) and want to be a tutor, email (.*) at (.*). Tell.*')
      g = m.match(text)
      course=g[1]
      name =g[2]
      email=g[3]
      mycursor.execute("insert into csseTutoringXinfo (typeOfInfo, info) values (%s, %s)", ("tutor requirement", course))
      mycursor.execute("insert into csseXtutors (name, email, position) values (%s, %s, %s)", (name, email, 'advisor'))

      text = soup.find(text='CS Tutoring Services').parent.next_sibling.next_sibling.get_text()
      text = re.sub(r'\s+', ' ', text).strip()
      m = re.compile('.* CSC/CPE (.*). We .* including (.*). If .*')
      g = m.match(text)
      courses = g[1].replace('and', '').split(',') + g[2].replace('and', '').split(',')
      for i in courses:
          mycursor.execute("insert into tutoringXcourse (department, course) values (%s, %s)", ('CSSE', i.strip()))

      url = "http://tutoring.csc.calpoly.edu/tutors/"
      myRequest = requests.get(url)
      soup = BeautifulSoup(myRequest.text,"html.parser")
      text = soup.find(text=re.compile('Head Tutor: .*'))
      m = re.compile('Head Tutor: (.*)')
      g = m.match(text)
      name=g[1].strip()
      email= text.parent.next_sibling.next_sibling.get_text().split(',')[1].strip()
      mycursor.execute("insert into csseXtutors (name, email, position) values (%s, %s, %s)", (name, email, 'head tutor'))

      for i in soup.find_all('h2'):
          mycursor.execute("insert into csseXtutors (name) values (%s)", (i.get_text().strip()))

finally:
    connection.close()
