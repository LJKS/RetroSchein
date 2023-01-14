
import tkinter as tk
from tkinter import ttk
import requests
import bs4
import ikw_crawler
import random

ALLSTICKY = 'NESW' # All directions
MODULE2NAME = {'NI': 'Neuroinformatics',
                   'AI':'Artificial Intelligence',
                   'CL':'Computational Linguistics',
                   'NS':'Neuroscience',
                   'CNP': 'Cognitive Neuropsychology',
                   'MCS':'Methods of CogSci',
                   'INF':'Computer Science',
                   'MAT':'Maths',
                   'PHIL':'Philosophy',
                   'BW':'Elective Courses (inc. Foundations of CogSci and Thesis)'}

NAME2MODULE = {'Neuroinformatics': 'NI',
               'Artificial Intelligence': 'AI',
               'Computational Linguistics': 'CL',
               'Neuroscience': 'NS',
               'Cognitive Neuropsychology': 'CNP',
               'Methods of CogSci': 'MCS',
               'Computer Science': 'INF',
               'Maths': 'MAT',
               'Philosophy': 'PHIL',
               'Elective Courses (inc. Foundations of CogSci and Thesis)': 'BW'}


class ProtoCourse():
    def __init__(self, name, points, grade, identifier, modules, term, year):
        self.name = name
        self.points = points
        self.grade = grade
        self.old_grade = grade.get()
        self.identifier = identifier
        self.modules = modules
        self.term = term
        self.year = year
        self.selected_module = None

    def change_selected_module(self, module):
        self.selected_module = module


class Course():
    def __init__(self, master, row_nr, protocourse: ProtoCourse, max_course_desc_len=50):
        self.master = master
        self.name = protocourse.name

        def insert_newlines(string, every=64):
            return '\n'.join(string[i:i + every] for i in range(0, len(string), every))
        self.name = insert_newlines(self.name, max_course_desc_len)
        self.points = protocourse.points
        self.grade = protocourse.grade
        self.protocourse = protocourse
        self.name_display = ttk.Label(self.master, text=self.name)
        self.name_display.grid(column=0, row=row_nr, sticky='W')
        self.points_display = ttk.Label(self.master, text=f'{self.points:2}')
        self.points_display.grid(column=1, row=row_nr, sticky='E')
        #print(self.protocourse)
        grade_val_command = self.master.register(self.validate_grade_input)
        self.grade_display = ttk.Entry(self.master, textvariable=self.protocourse.grade, width=4, validate='focusout', validatecommand=grade_val_command)
        self.grade_display.grid(column=2, row=row_nr, sticky='E')
        #three masters up: CourseList, Submodule, BScModule
        self.selected_marker = False if self.protocourse.selected_module == None else self.master.master.master.name == MODULE2NAME[self.protocourse.selected_module]
        self.selected_marker = int(self.selected_marker)
        #print(self.protocourse.name)
        #print(self.master.master.descriptor_str)
        #print(self.master.master.master.name)
        self.selected_value = tk.StringVar(master=self.master, value=self.selected_marker, name=self.protocourse.name + 'selected_bool' + self.master.master.descriptor_str + self.master.master.master.name)
        self.selected_marker = ttk.Checkbutton(self.master, variable=self.selected_value, command=self.select)
        self.selected_marker.grid(column=3, row=row_nr)

    def select(self):
        self.protocourse.selected_module = [NAME2MODULE[self.master.master.master.name], self.master.master.descriptor_str]
        self.master.master.master.master.change_course_selection(self.protocourse)
        self.master.master.calculate_points_and_grade()

    def deselect(self):
        self.selected_value.set(0)
        self.master.master.calculate_points_and_grade()


    def validate_grade_input(self):
        grade_str = self.protocourse.grade.get()
        print('testing gradestring ' +grade_str)
        def not_accepted():
            self.protocourse.grade.set(self.protocourse.old_grade)
            return False
        def accepted():
            self.protocourse.old_grade = grade_str
            return True
        if not len(grade_str) == 3:
            return not_accepted()
        if not grade_str[1] == '.':
            return not_accepted()
        if not grade_str[0] in ['1', '2', '3', '4']:
            return not_accepted()
        if not grade_str[2] in ['0', '3', '7']:
            return not_accepted()
        if grade_str in ['4.3', '4.7']:
            return not_accepted()
        return accepted()




class CompulsoryCourses(ttk.Frame):
    def __init__(self, master, points, c_grid, r_grid, course_string_hor_len=50, padding=3):
        super().__init__(master, relief='groove', borderwidth=1)
        self.points = points
        self.padding = padding
        self.grid(column=c_grid, row=r_grid, padx=self.padding, pady=self.padding, sticky=ALLSTICKY)
        self.course_string_hor_len = course_string_hor_len
        self.descriptor_str = 'c'
        self.courselist = ttk.Frame(self)
        self.courselist.grid(column=0, row=0)

        self.courselist_name_desc = ttk.Label(self.courselist, text='Compulsory Courses:' + ' '*(self.course_string_hor_len-len('Compulsory Courses:')))
        self.points_desc = ttk.Label(self.courselist, text='  ECTS:  ')
        self.grade_desc = ttk.Label(self.courselist, text='  Grade:  ')
        self.selected_desc = ttk.Label(self.courselist, text='  Apply:  ')

        self.courselist_name_desc.grid(column=0, row=0)
        self.points_desc.grid(column=1, row=0)
        self.grade_desc.grid(column=2, row=0)
        self.selected_desc.grid(column=3, row=0)

        self.grading = ttk.Labelframe(self, text='Points and Grading')
        self.grading.grid(column=0, row=1)

        self.grading_points_max = ttk.Label(self.grading, text=f' / Points: {self.points}')
        self.grading_points_max.grid(column=1, row=0)
        self.grading_points_applied_var = tk.StringVar(self, value='0', name='grading_points_applied_var_' + self.master.name + self.descriptor_str)
        self.grading_points_applied = ttk.Label(self.grading, textvariable=self.grading_points_applied_var)
        self.grading_points_applied.grid(column=0, row=0)

        self.grading_achieved_grade_desc = ttk.Label(self.grading, text='       Approx. Grade: ')
        self.grading_achieved_grade_desc.grid(column=2, row=0)
        self.grading_achieved_grade_var = tk.StringVar(self, value='-', name='grading_achieved_grade_var' + self.master.name + self.descriptor_str)
        self.grading_achieved_grade_vis = ttk.Label(self.grading, textvariable=self.grading_achieved_grade_var)
        self.grading_achieved_grade_vis.grid(column=3, row=0)

        self.courses = []

    def add_course(self, protocourse):
        course = Course(master=self.courselist, row_nr=len(self.courses) +1, protocourse=protocourse, max_course_desc_len=self.course_string_hor_len)
        self.courses.append([protocourse, course])

    def calculate_points_and_grade(self):
        #points
        total_points = 0
        for course in self.courses:
            proto_c, vis_c = course
            if vis_c.selected_value.get() == '1':
                total_points += int(proto_c.points)
        print(total_points)
        self.grading_points_applied_var.set(str(total_points))

        #grade
        weighted_grade_sum = 0.
        total_weight = 0
        for course in self.courses:
            proto_c, vis_c = course
            if vis_c.selected_value.get() == '1':
                if proto_c.grade.get() != '-':
                    if int(proto_c.points)>0:
                        weighted_grade_sum += int(proto_c.points)*float(proto_c.grade.get())
                        total_weight+= int(proto_c.points)
        if total_weight == 0:
            self.grading_achieved_grade_var.set('-')
        else:
            self.grading_achieved_grade_var.set(f'{weighted_grade_sum/total_weight:.2f}')


class OptionalCourses(ttk.Frame):
    def __init__(self, master, points, c_grid, r_grid, course_string_hor_len=50, padding=3):
        super().__init__(master, relief='groove', borderwidth=1)
        self.points = points
        self.padding = padding
        self.grid(column=c_grid, row=r_grid, padx=self.padding, pady=self.padding, sticky=ALLSTICKY)
        self.course_string_hor_len = course_string_hor_len
        self.descriptor_str = 'o'

        self.courselist = ttk.Frame(self)
        self.courselist.grid(column=0, row=0)

        self.courselist_name_desc = ttk.Label(self.courselist, text='Compulsory Courses:' + ' '*(self.course_string_hor_len-len('Compulsory Courses:')))
        self.points_desc = ttk.Label(self.courselist, text='  ECTS:  ')
        self.grade_desc = ttk.Label(self.courselist, text='  Grade:  ')
        self.selected_desc = ttk.Label(self.courselist, text='  Apply:  ')

        self.courselist_name_desc.grid(column=0, row=0)
        self.points_desc.grid(column=1, row=0)
        self.grade_desc.grid(column=2, row=0)
        self.selected_desc.grid(column=3, row=0)

        self.grading = ttk.Labelframe(self, text='Points and Grading')
        self.grading.grid(column=0, row=1)

        self.grading_points_max = ttk.Label(self.grading, text=f' / Points: {self.points}')
        self.grading_points_max.grid(column=1, row=0)

        self.grading_points_applied_var = tk.StringVar(self, value='0', name='grading_points_applied_var_' + self.master.name + self.descriptor_str)
        self.grading_points_applied = ttk.Label(self.grading, textvariable=self.grading_points_applied_var)
        self.grading_points_applied.grid(column=0, row=0)

        self.grading_achieved_grade_desc = ttk.Label(self.grading, text='       Approx. Grade: ')
        self.grading_achieved_grade_desc.grid(column=2, row=0)
        self.grading_achieved_grade_var = tk.StringVar(self, value='-', name='grading_achieved_grade_var' + self.master.name + self.descriptor_str)
        self.grading_achieved_grade_vis = ttk.Label(self.grading, textvariable=self.grading_achieved_grade_var)
        self.grading_achieved_grade_vis.grid(column=3, row=0)


        self.courses = []

    def add_course(self, protocourse):
        course = Course(master=self.courselist, row_nr=len(self.courses) +1, protocourse=protocourse, max_course_desc_len=self.course_string_hor_len)
        self.courses.append([protocourse, course])

    def calculate_points_and_grade(self):
        #points
        total_points = 0
        for course in self.courses:
            proto_c, vis_c = course
            if vis_c.selected_value.get() == '1':
                total_points += int(proto_c.points)
        print(total_points)
        self.grading_points_applied_var.set(str(total_points))

        #grade
        weighted_grade_sum = 0.
        total_weight = 0
        for course in self.courses:
            proto_c, vis_c = course
            if vis_c.selected_value.get() == '1':
                if proto_c.grade.get() != '-':
                    if int(proto_c.points)>0:
                        weighted_grade_sum += int(proto_c.points)*float(proto_c.grade.get())
                        total_weight+= int(proto_c.points)
        if total_weight == 0:
            self.grading_achieved_grade_var.set('-')
        else:
            self.grading_achieved_grade_var.set(f'{weighted_grade_sum/total_weight:.2f}')


class BScModule(ttk.Frame):
    def __init__(self, master, name, compulsory_points, optional_points, c_grid, r_grid, r_span=1, c_span=1, padding=3):
        super().__init__(master, relief='groove', borderwidth=1)
        self.master = master
        self.name = name
        self.compulsory_points = compulsory_points
        self.optional_points = optional_points
        self.padding = padding

        self.grid(column=c_grid, row=r_grid, columnspan=c_span, rowspan=r_span, padx=self.padding, pady=self.padding, sticky=ALLSTICKY)
        self.title = ttk.Label(self, text=self.name, font=('Helvetica', 16))
        self.compulsory_courses = CompulsoryCourses(self, compulsory_points, 0,1)
        self.optional_courses = OptionalCourses(self, optional_points, 0,2)
        self.title.grid(column=0, row=0, sticky=ALLSTICKY)
        self.grid_columnconfigure(0, weight=1)

    def change_course_selection(self, protocourse, submodule):
        assert submodule in ['o', 'c']
        target_courses = self.compulsory_courses if submodule == 'c' else self.optional_courses
        for check_course in target_courses.courses:
            check_protocourse, check_vis_course = check_course
            if protocourse.name == check_protocourse.name:
                check_course[1].deselect()

class Course_Adding_System(tk.Frame):
    def __init__(self, master, courses):
        super().__init__(master, relief='groove', borderwidth=1)

        self.select_course_default_string = ''
        self.courses = courses
        self.course_strings = [self.proto2display_string(course) for course in self.courses]+[self.select_course_default_string]

        self.course_selector_variable = tk.StringVar(self, value=self.course_strings[-1], name='CourseSelectorString')
        self.search_command = self.register(self.update_searchstring)
        self.course_selector = ttk.Combobox(self, postcommand=self.search_command, textvariable=self.course_selector_variable, values=self.course_strings, width=80)
        self.course_selector.grid(column=2, row=0)

        reset_command = self.register(self.reset_search_string)
        self.reset_button = ttk.Button(self, text='Reset', command=reset_command)
        self.reset_button.grid(column=1, row=0)

        self.label = ttk.Label(self, text='Add Course here:')
        self.label.grid(column=0, row=0)

        self.add_course_command = self.register(self.add_course_button_command)
        self.default_add_button_text = 'Add Course'
        self.add_button_text = tk.StringVar(self, value=self.default_add_button_text)
        self.add_button = ttk.Button(self, textvariable=self.add_button_text, command=self.add_course_command)
        self.add_button.grid(column=3, row=0)



    def update_searchstring(self):
        if self.course_selector_variable.get == '':
            self.course_selector['values'] = self.course_strings
        self.course_selector['values'] = [course_string for course_string in self.course_strings if self.course_selector_variable.get() in course_string]
        self.add_button_text.set(self.default_add_button_text)

    def reset_search_string(self):
        self.course_selector_variable.set(self.select_course_default_string)
        self.update_searchstring()

    def add_course_button_command(self):
        course_string = self.course_selector_variable.get()
        if course_string == self.select_course_default_string:
            self.add_button_text.set('Please first select course \n' + self.default_add_button_text)
        selected_course = self.display_string2proto(course_string)
        if selected_course == None:
            self.add_button_text.set('This seems not to be \n a valid course \n' + self.default_add_button_text)
            self.course_selector_variable.set(self.select_course_default_string)
        else:
            self.master.add_course(selected_course)
            self.course_selector_variable.set(self.select_course_default_string)
            self.add_button_text.set(self.default_add_button_text)

    def proto2display_string(self, proto):
        return f'{proto.name} || {proto.year} || {proto.term}'

    def display_string2proto(self, string):
        if not len(string.split(' || '))==3:
            return None
        else:
            splits = string.split(' || ')
            course_name = splits[0]
            course_year = splits[1]
            course_term = splits[2]

            for course in self.courses:
                if course_name == course.name and course_year == course.year and course_term == course.term:
                    return course
        return None

class ModuleCheckBox(tk.Frame):
    def __init__(self, master, module_name):
        super().__init__(master, relief='groove', borderwidth=1)
        self.master=master
        self.module_name = module_name
        self.label = ttk.Label(self, text=module_name)
        self.compulsory_var = tk.IntVar(self, value=0)
        self.compulsory_box = ttk.Checkbutton(self, variable=self.compulsory_var, text='compulsory')
        self.optional_var = tk.IntVar(self, value=0)
        self.optional_box = ttk.Checkbutton(self, variable=self.optional_var, text='optional')
        self.label.grid(column=0, row=0)
        self.compulsory_box.grid(column=0, row=1)
        self.optional_box.grid(column=0, row=2)

    def get_modules(self):
        modules = []
        if self.compulsory_var.get()==1:
            modules.append([self.module_name, 'c'])
        if self.optional_var.get()==1:
            modules.append([self.module_name, 'o'])
        return modules

    def reset(self):
        self.compulsory_var.set(0)
        self.optional_var.set(0)



class CustomCourse(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.uppergrid = ttk.Frame(self)
        self.uppergrid.grid(column=0, row=0)

        self.label = ttk.Label(self, text='Add Customized Course:')

        self.default_course_title = 'Add Course Title here'
        self.course_title_var = tk.StringVar(self.uppergrid, value=self.default_course_title)
        self.course_title_box = ttk.Entry(self.uppergrid, textvariable=self.course_title_var, width=50)

        self.default_course_points = '0'
        self.course_points_var = tk.StringVar(self.uppergrid, value=self.default_course_points)
        self.course_points_box = ttk.Entry(self.uppergrid, textvariable=self.course_points_var, width=3)

        self.course_years = [str(i) for i in range(2010, 2027)]
        self.default_course_year = '2020'
        self.course_year_var = tk.StringVar(self.uppergrid, value=self.default_course_year)
        self.course_year_selector = ttk.Combobox(self.uppergrid, textvariable=self.course_year_var, width=5)

        self.course_terms = ['SS', 'WS']
        self.default_course_term = 'WS'
        self.course_term_var = tk.StringVar(self.uppergrid, value=self.default_course_term)
        self.course_term_selector = ttk.Combobox(self.uppergrid, textvariable=self.course_term_var, width=3)

        self.default_add_course_button_text = 'Add Course'
        self.add_course_button_var = tk.StringVar(self.uppergrid, value=self.default_add_course_button_text)
        add_course_command = self.register(self.add_custom_course)
        self.add_course_button = ttk.Button(self.uppergrid, command=add_course_command, textvariable=self.add_course_button_var)

        self.label.grid(column=0, row=0)
        self.course_title_box.grid(column=1, row=0)
        self.course_points_box.grid(column=2, row=0)
        self.course_year_selector.grid(column=3, row=0)
        self.course_term_selector.grid(column=4, row=0)
        self.add_course_button.grid(column=5, row=0)


        self.lower_grid = ttk.Frame(self)
        self.lower_grid.grid(column=0, row=1)
        self.module_checkers = [ModuleCheckBox(self.lower_grid, module_name) for module_name in sorted(list(MODULE2NAME.keys()))]
        for i, module_check in enumerate(self.module_checkers):
            module_check.grid(column=i, row=0)


    def add_custom_course(self):
        has_problem = False
        course_title = self.course_title_var.get()
        course_points = self.course_points_var.get()
        has_problem = has_problem or not course_points.isdigit()
        course_year = self.course_year_var.get()
        has_problem = has_problem or len(course_year)!=4
        course_term = self.course_term_var.get()
        modules = []
        for apply_module in self.module_checkers:
            applied_modules = apply_module.get_modules()
            modules = applied_modules + modules
        has_problem = has_problem or len(modules)==0

        if has_problem:
            self.add_course_button_var.set('Could not add Course \n' + self.default_add_course_button_text)
        else:
            protocourse = ProtoCourse(name=course_title, points=course_points, grade=tk.StringVar(value='-', name=course_title + '_coursegradevar'),
                                      identifier='missing/custom', modules=modules, term=course_term, year=course_year)
            self.master.add_course(protocourse)
            self.add_course_button_var.set(self.default_add_course_button_text)
            self.reset()

    def reset(self):
        self.course_title_var.set(self.default_course_title)
        self.course_points_var.set(self.default_course_points)
        self.course_year_var.set(self.default_course_year)
        self.course_term_var.set(self.default_course_term)
        for module_checker in self.module_checkers:
            module_checker.reset()

class Scheinbot(tk.Frame):
    def __init__(self, master, crawl_courses=True):
        super().__init__(master)
        self.grid(column=0, row=0, sticky=ALLSTICKY)
        self.master.grid_columnconfigure(0, weight=1)
        self.NI = BScModule(self, 'Neuroinformatics', compulsory_points=12,optional_points=12, c_grid=0, r_grid=0)
        self.AI = BScModule(self, 'Artificial Intelligence', compulsory_points=12,optional_points=12, c_grid=1, r_grid=0)
        self.CL = BScModule(self, 'Computational Linguistics', compulsory_points=12,optional_points=12, c_grid=2, r_grid=0)
        self.NS = BScModule(self, 'Neuroscience', compulsory_points=12,optional_points=12, c_grid=0, r_grid=1)
        self.CNP = BScModule(self, 'Cognitive Neuropsychology', compulsory_points=12,optional_points=12, c_grid=1, r_grid=1)
        self.MCS = BScModule(self, 'Methods of CogSci', compulsory_points=12,optional_points=12, c_grid=2, r_grid=1)
        self.INF = BScModule(self, 'Computer Science', compulsory_points=12,optional_points=12, c_grid=0, r_grid=2)
        self.MAT = BScModule(self, 'Maths', compulsory_points=12,optional_points=12, c_grid=1, r_grid=2)
        self.PHIL = BScModule(self, 'Philosophy', compulsory_points=12,optional_points=12, c_grid=2, r_grid=2)
        self.BW = BScModule(self, 'Elective Courses (inc. Foundations of CogSci and Thesis)', compulsory_points=18, optional_points=24, c_grid=3, r_grid=0, r_span=3)
        self.str2mod = {'NI':self.NI, 'AI':self.AI, 'CL':self.CL, 'NS':self.NS, 'CNP': self.CNP, 'MCS':self.MCS, 'INF':self.INF, 'MAT':self.MAT, 'PHIL':self.PHIL, 'BW':self.BW}





        if crawl_courses:
            courses = self.crawl_courses()
        else: courses = []
        self.course_adding_system = Course_Adding_System(self, courses)
        self.course_adding_system.grid(column=1, row=3, columnspan=3)

        self.custom_course_adding_system = CustomCourse(self)
        #self.custom_course_adding_system.grid(column=0, row=3, columnspan=3)



        self.course_switch_button_texts = ['Switch to adding custom courses', 'Switch to adding crawled courses']
        self.display_switch_button_targets = [self.custom_course_adding_system, self.course_adding_system]
        self.current_course_switch_display_idx = 0

        self.course_switch_var = tk.StringVar(self, value=self.course_switch_button_texts[self.current_course_switch_display_idx])
        course_switch_button_command = self.register(self.switch_course_adding_system)
        self.course_add_switch_button = ttk.Button(self, textvariable=self.course_switch_var, command=course_switch_button_command)
        self.course_add_switch_button.grid(column=0, row=3, sticky='N')

        self.quitbutton = ttk.Button(self, text='Quit!', command=master.destroy)
        self.quitbutton.grid(column=4, row=4)

    def switch_course_adding_system(self):
        self.display_switch_button_targets[int(not(bool(self.current_course_switch_display_idx)))].grid_forget()
        self.course_switch_var.set(self.course_switch_button_texts[self.current_course_switch_display_idx])
        self.display_switch_button_targets[self.current_course_switch_display_idx].grid(column=1, row=3, columnspan=3)
        self.current_course_switch_display_idx = int(not(bool(self.current_course_switch_display_idx)))
        print(self.current_course_switch_display_idx)


    def add_course(self, protocourse):
        for mod in protocourse.modules:
            if not mod[0] in self.str2mod.keys():
                print(mod[0], protocourse.modules)
                raise RuntimeError
            target_mod = self.str2mod[mod[0]]
            sub_module = mod[1] # 'c' or 'o' for compulsory / optional
            assert sub_module in ['o', 'c'], f'submodule should be o or c, but is: {sub_module}'
            select_sub_mod = lambda mod, oc: mod.compulsory_courses if oc == 'c' else mod.optional_courses
            target_mod = select_sub_mod(target_mod, sub_module)
            target_mod.add_course(protocourse)

    def change_course_selection(self, protocourse):
        for module in protocourse.modules:
            mod, submod = module
            print(module, protocourse.selected_module)
            if not module==protocourse.selected_module:
                self.str2mod[mod].change_course_selection(protocourse, submod)


    def crawl_courses(self, url='https://w3o.ikw.uni-osnabrueck.de/scheinmaker/courses/list/all/'):
        course_data = requests.get(url).text
        soup = bs4.BeautifulSoup(course_data, 'html.parser')
        parser = ikw_crawler.MyHTMLParser()
        parser.feed(str(soup))

        def crawldict2protocourse(crawldict):
            name = crawldict['title']
            points = crawldict['ECTS']
            grade = '-'
            identifier = crawldict['id']
            modules = []
            module_list = crawldict['modules']
            term = crawldict['term']
            year = crawldict['year']
            for module in module_list:

                # ignore old regulation
                if 'KOGW' in module:
                    continue

                # find submodule ()
                if any(check in module for check in ['BW', 'BWP']):
                    submodule = 'o'
                elif 'BP' in module:
                    submodule = 'c'
                else:
                    if any(check in module for check in ['MW', 'MWP', 'MP']):
                        #this is a masters course, ignore for now
                        continue
                    else:
                        raise Exception(f'Course seems to be neither in optional nor compulsory courses, has module: {module}')

                # find module
                # module is the tokens between the dashes
                mod_string = module.split('-')[2]

                ### Special cases
                # if elective, choose respective elective designator on idx 1 and remove space from elective course
                if 'elective course' in mod_string:
                    mod_string = mod_string = module.split('-')[1].replace(' ', '')

                #Treat IWS - Instruction for working scientifically as a BW course, which it practically is
                if 'IWS' == mod_string:
                    mod_string = 'BW'

                #Treat Foundations as compulsive course from elective courses
                if 'IP' == mod_string:
                    mod_string = 'BW'
                    submodule = 'c'

                assert mod_string in ['NI', 'AI', 'CL', 'NS', 'CNP', 'MCS', 'INF', 'MAT', 'PHIL', 'BW'], f'Not in regular modules: {mod_string} from {module}'

                modules.append([mod_string, submodule])

            #If the course is not directly usable for any of the modules available, can still be used as elective
            if len(modules) == 0:
                modules = [['BW', 'o']]

            new_course = ProtoCourse(name=name, points=points, grade=tk.StringVar(value=grade, name=name + '_coursegradevar'), identifier=identifier, modules=modules, term=term, year=year)
            return new_course

        available_courses = []
        for crawldict in parser.courses:
            available_courses.append(crawldict2protocourse(crawldict))

        return available_courses

if __name__ == '__main__':
    root = tk.Tk()
    gui = Scheinbot(root)
    root.mainloop()