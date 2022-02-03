'''
Creates .ics files for CSE tutor timetables
poorly developed by Anosua Roy (anosua.roy@unsw.edu.au/anosuaa.roy@gmail.com)
with great assistance from Thomas Kunc
sorry in advanced
2020 may
'''

import datetime
import uuid

ZID = 2
TIME_LOC = 1
# Total teaching weeks in one UNSW term
# Must update frequently
TOTAL_WEEKS = 10
# Change SESSION_TIME for the number of hours in one session
# Default = 3 (1511 session time)
SESSION_TIME = 3
# MON_WEEK1 must be given in "YYYY/MM/DD" format
# Change the value for the corresponding date for the monday of week 1 of desired term
MON_WEEK1 = "2022/02/14"
# MID_TERM_LENGTH is the number of week up to and includiing the mid-term break
MID_TERM_LENGTH = 6

##-----------------------------------HELPER-FUNCTIONS-------------------------------------------##

def find_end_date(first_teaching_day=MON_WEEK1, total_weeks=TOTAL_WEEKS):
    '''
    Finds the last teaching date of a particular period of time

    Params:
        first_teaching_date (str), optional: date of first teaching day of particular period
            default=MON_WEEK1
        total_weeks (int), optional: number of weeks in particular session
            default=TOTAL_WEEKS

    Returns:
        (str): last teaching date YYYYMMDD
    '''
    formatted_mon_w1 = datetime.datetime.strptime(first_teaching_day, "%Y/%m/%d")
    return (formatted_mon_w1 + datetime.timedelta(weeks=total_weeks, days=-1)).strftime("%Y%m%d")

def find_end_time(start_time, session_time=SESSION_TIME):
    '''
    Finds the end time of a class given the start time and SESSION_TIME

    Params:
        start_time (str): HHMMSS (24 hour time)
        session_time (int), optional: number of hours in one tut/lab session
            deafult=SESSION_TIME
    Returns:
        (str) HHMMSS (24 hour time)
    '''
    formatted_st = datetime.datetime.strptime(start_time, "%H%M%S")
    return (formatted_st + datetime.timedelta(hours=session_time)).strftime("%H%M%S")

def find_start_time(class_id):
    '''
    Finds the start time of a class given the class_id

    Params:
        class_id (str): the class to find a start time for

    Returns:
        (str): start time HHMMSS (24 hour time)
            e.g. '090000', '110000'
    '''
    return class_id[3:5] + '0000'

def mon_post_mid_term(first_teaching_day=MON_WEEK1, mid_term_length=MID_TERM_LENGTH):
    '''
    Find the date of the first monday after the mid-term break (usually week 7)

    Params:
        first_teaching_date (str), optional: date of first teaching day of particular period
            default=MON_WEEK1
        mid_term_length (int), optional: number of week up to and includiing the mid-term break
            default=MID_TERM_LENGTH

    Returns:
        (str): first teaching day after mid-term break YYYY/MM/DD
    '''

    formatted_date = datetime.datetime.strptime(first_teaching_day, "%Y/%m/%d")

    start_date = formatted_date + datetime.timedelta(weeks=mid_term_length)

    return start_date.strftime("%Y/%m/%d")

def find_start_date(class_id, first_teaching_day=MON_WEEK1):
    '''
    Finds the first date of class given the class_id

    Params:
        class_id (str): the class to find a start date for
        first_teaching_date (str), optional: date of first day of teaching at UNSW
            default=MON_WEEK1

    Returns:
        (str): last teaching date YYYYMMDD
    '''
    day = class_id[0] + class_id[1] + class_id[2]
    days_to_num = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5}

    if day not in days_to_num:
        raise ValueError(f"Second column must be given in dddHH-loc format e.g. mon09-kora\
                            failing day: {day}")

    formatted_mon_w1 = datetime.datetime.strptime(first_teaching_day, "%Y/%m/%d")

    start_date = formatted_mon_w1 + datetime.timedelta(days=days_to_num[day])

    return start_date.strftime("%Y%m%d")

##-----------------------------------WRITE-TO-.ICS-FILE------------------------------------------##

def end_ics_file(ics_file_name):
    '''
    Write final lines to given ics_file

    Params:
        ics_file_name (str): the generated name for the ics file
    '''
    open(ics_file_name, 'a').write("END:VCALENDAR\n")

def add_recurring_event(ics_file_name, class_id, course_code):
    '''
    Write a recurring event to given ics_file for a given class_id
    Event reoccurs every at the same time every UNSW week for 1 <= week <= 10
        exlcuding the mid-term break
    Note: this does not account for class changes e.g. public holidays

    Params:
        ics_file_name (str): the generated name for the ics file
        class_id (str): the class to find a start date for
        course_code (str): the user inputted course code of particular subject
    '''
    start_time = find_start_time(class_id)
    end_time = find_end_time(start_time)

    curr_date = datetime.datetime.now().strftime("%Y%m%d")
    curr_time = datetime.datetime.now().strftime("%H%M%S")

    for term_break in range(0, 2):

        if term_break:
            start_date = find_start_date(class_id, mon_post_mid_term())
            end_date = find_end_date(first_teaching_day=mon_post_mid_term(),\
                                    total_weeks=TOTAL_WEEKS - MID_TERM_LENGTH)
        else:
            start_date = find_start_date(class_id)
            end_date = find_end_date(total_weeks=MID_TERM_LENGTH - 1)

        event = f"""BEGIN:VEVENT
                DTSTART;TZID=Australia/Sydney:{start_date}T{start_time}
                DTSTAMP;TZID=Australia/Sydney:{curr_date}T{curr_time}
                DTEND;TZID=Australia/Sydney:{start_date}T{end_time}
                RRULE:FREQ=WEEKLY;UNTIL={end_date}T{end_time}
                UID: {uuid.uuid1(node=None, clock_seq=None)}_{ics_file_name}
                SUMMARY: {course_code.upper()} Tut-Lab
                END:VEVENT
                """.replace('                ', '')

        with open(ics_file_name, 'a') as ics_file:
            ics_file.write(event)

def start_ics_file(ics_file_name):
    '''
    Writes default start to ics file

    Params:
        ics_file_name (str): the generated name for the ics file
    '''
    basic_start_format = """BEGIN:VCALENDAR
                            VERSION:2.0
                            PRODID:-//anosua.roy@unsw.edu.au//Tutor Timetable//
                            """.replace('                            ', '')

    open(ics_file_name, 'w+').write(basic_start_format)

    with open(ics_file_name, 'a') as ics_file:
        with open('sydney_timezone_format.txt', 'r') as time_file:
            ics_file.write(time_file.read())
            ics_file.write("\n")

##-----------------------------------MAIN-FUNCTIONS------------------------------------------##

def main():
    '''
    Runs the ics generation program if called from the terminal
    '''
    start = ("""\n\nThis is a quick script to generate ics files for 22T1 tutor timetables
            Please note this does not account for public holidays and variations from regular weekly classes
            You may enter multiple course and mutliple classes for each course
            Class codes must be in the form "mon13"
            When you have finished entering class codes enter 'DONE' when prompted
            When you have finished entering course enter 'DONE' when prompted

            Email anosua.roy@unsw.edu.au about any bugs
            \n\n""").replace("            ", "")


    print(start)

    course_code = None
    class_code = None

    tutor = input("Enter zid (e.g. 'z5264396'): \n").upper()

    ics_file_name = f'{tutor}-20T2-CSE-TIMETABLE.ics'

    start_ics_file(ics_file_name)

    while course_code != 'DONE':
        course_code = input("\nEnter a course code (e.g. 'COMP1511') (type 'done' if finished): \n").upper()
        while class_code != 'done':
            class_code = input("Enter a class code (e.g. 'thu11-sitar') (type 'done' if finished): \n").lower()
            if class_code != 'done':
                add_recurring_event(ics_file_name, class_code, course_code)

    end_ics_file(ics_file_name)

    print(".ics file succesfully made in the working directory")

if __name__ == '__main__':
    main()
