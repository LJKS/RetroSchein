import requests
from html.parser import HTMLParser
import bs4

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.courses = []
        self.current_course = None
        self.legit_modules = ['CS-BP-AI', 'CS-BP-CL', 'CS-BP-CNP', 'CS-BP-INF', 'CS-BP-MAT', 'CS-BP-MCS', 'CS-BP-NI', 'CS-BP-NS', 'CS-BP-PHIL', 'CS-BW', 'CS-BW - Bachelor elective course', 'CS-BW-IP', 'CS-BW-IWS', 'CS-BWP-AI', 'CS-BWP-CL', 'CS-BWP-CNP', 'CS-BWP-INF', 'CS-BWP-MAT', 'CS-BWP-MCS', 'CS-BWP-NI', 'CS-BWP-NS', 'CS-BWP-PHIL', 'CS-MP-IDC', 'CS-MP-SP', 'CS-MW', 'CS-MW - Master elective course', 'CS-MWP-AI', 'CS-MWP-CL', 'CS-MWP-CNP', 'CS-MWP-NI', 'CS-MWP-NS', 'CS-MWP-PHIL', 'KOGW-PM-CL', 'KOGW-PM-INF', 'KOGW-PM-KI', 'KOGW-PM-KNP', 'KOGW-PM-LOG', 'KOGW-PM-MAT', 'KOGW-PM-NI', 'KOGW-PM-NW', 'KOGW-PM-PHIL', 'KOGW-PM-SD', 'KOGW-PWB', 'KOGW-WM-AWA', 'KOGW-WPM-CL', 'KOGW-WPM-INF', 'KOGW-WPM-KI', 'KOGW-WPM-KNP', 'KOGW-WPM-MAT', 'KOGW-WPM-NI', 'KOGW-WPM-NW', 'KOGW-WPM-PHIL']



    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            divdict = {}
            for t in attrs:
                assert type(t)== tuple
                divdict[t[0]] = t[1]
            if divdict['class'] == 'course_entry_div':
                print(attrs)
                self.current_course = {}
                self.courses.append(self.current_course)
                self.current_course['title'] = divdict['course_title']
                self.current_course['year'] = divdict['course_year']
                self.current_course['term'] = divdict['course_term']
                self.current_course['id'] = divdict['course_vpv']
                self.current_course['modules'] = []

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if 'LPs' in data:
            self.current_course['ECTS'] = data.split()[0]
        if data in self.legit_modules:
            self.current_course['modules'].append(data)


def crawl_courses(url='https://w3o.ikw.uni-osnabrueck.de/scheinmaker/courses/list/all/'):
    course_data = requests.get(url).text
    soup = bs4.BeautifulSoup(course_data, 'html.parser')
    parser = MyHTMLParser()
    parser.feed(str(soup))
    for course in parser.courses:
        print(course)
if __name__ == '__main__':
    crawl_courses()