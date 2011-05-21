# SMS Attendance
# Version : 0.4
# Author  : jishnu7@gmail.com
 
DBHOST = "localhost"
DBUSER = " "
DBPASS = " "
DB = " "

import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup
import datetime
import MySQLdb

db = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASS, db=DB)

# Function to send SMS
def send_sms(message, mobileNum) :
    # >>>>>>>>>>>
    print message, "\nSuccess\n"

# Function to fetch info from college website
def fetch(username, passwd, mobnum) :
    print username
    
    # Set Cookie and log into college website
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode({'txtLogin' : username, 'txtPass' : passwd})
    login = opener.open('http://www.mesce.ac.in/MainLoginValidation.php', login_data)

    # Page for attendance summary
    attendance_page = opener.open('http://www.mesce.ac.in/departments/student.php?option=attendanceSummary')
    attendance_var = attendance_page.read()
    attendance_var = BeautifulSoup(attendance_var)
    search = attendance_var.findAll(attrs={"align" :"center", "class" : "head1"})

    # If login was unsucessfull skip current user
    try:
        len_search = len(search)
        numHours = search[len_search-3].contents[0]
        totHours = search[len_search-2].contents[0]
        percent = search[len_search-1].contents[0].next
        detail_sem = search[len_search-4].contents[0]['value']
    except:
        f = open('attendance-log.txt','a+')
        f.write(username+" "+mobnum+"\n")
        f.close()
        msg = "SMS Attendance :- "+username + ", Invalid username. Your current registraion is deleted. Please re-register at http://attendance.thecodecracker.com"
        send_sms(msg, mobnum)
        query = "DELETE FROM users WHERE username = '"+username+"' LIMIT 1"
        error = db.cursor()
        error.execute(query)
        return

    # set date values for detail info
    d1 = "1"
    m1 = datetime.date.today().month
    y1 = datetime.date.today().year
    # If 1st day of the month, then we need data from 1st day of prev month
    if datetime.date.today().day == 1:
        m1 = m1-1
        if m1 == 0:
            m1 = "12"
            y1 =  y1 -1
    d2 = datetime.date.today().day
    m2 = datetime.date.today().month
    y2 = datetime.date.today().year

    # Submit data and retrieve detailed information in the date range we set.
    details_data = urllib.urlencode({'subSemester' : detail_sem, 'selDay1' : d1, 'selMonth1' : m1, 'selYear1' : y1, 'selDay2' : d2, 'selMonth2' : m2, 'selYear2' : y2})
    details_page = opener.open('http://www.mesce.ac.in/departments/student.php?option=attendanceDetail',details_data)
    details_var = details_page.read()
    details_var = BeautifulSoup(details_var)

    # Default SMS Message. without detailed information
    msg = "SMS Attendance :- Name : "+ username.split(".")[0].capitalize() + ". No of Hours Attended : " + numHours+" Total Hours Engaged : " + totHours+" Attendance : " + percent + "%"

    # We need detailed info only if we able to successfullt get the data.
    try: 
        search_details = details_var.findAll(attrs={"class" : "tfont"})
        temp_detail = list()
        len_detail =len(search_details)
        for x in range(len_detail-17,len_detail-2):
            try:
                temp_detail.append(str(search_details[x].contents[0].contents[0]))
            except:
                try:
                    temp_detail.append(str(search_details[x].contents[0]))
                except:
                    temp_detail.append("-")
        detail = list()
        detail.append(temp_detail[8].split("-")[0]+"/"+temp_detail[8].split("-")[1])
        if temp_detail[0] == temp_detail[8]:
            for x in range(1,7):
                if temp_detail[x] == "-":
                    detail.append(temp_detail[x+8])
                else:
                    detail.append(temp_detail[x])
        else:
            for x in range(9,15):
                detail.append(temp_detail[x])

        if detail[6] != '\n\t\n\tDeveloped by Focuz Infotech Kochi, in association with Campus Network Cell, MESCE. &#169; MES College of Engineering Kuttippuram':
            # Append the detailed info to the messafe and send sms
            msg = msg + " Last Day "+detail[0] + ": "+detail[1]+" "+detail[2]+" "+detail[3]+" "+detail[4]+" "+detail[5]+" "+detail[6]
        send_sms(msg, mobnum)

    except:
        send_sms(msg, mobnum)
        f = open('attendance-detail-failed.txt','a+')
        f.write(username+"\n")
        f.close()

cursor = db.cursor()
cursor.execute("SELECT username, passwd, sem, mob FROM users")
rows = int(cursor.rowcount)

for x in range(0,rows):
    row = cursor.fetchone()
    fetch(row[0], row[1], row[3])