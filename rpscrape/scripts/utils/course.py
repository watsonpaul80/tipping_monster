from orjson import loads


def courses(code='all'):
    data = loads(open('../courses/_courses', 'r').read())
    for cid, course in data[code].items():
        yield cid, course


def course_name(code):
    if code.isalpha():
        return code
    for cid, course in courses():
        if cid == code:
            return course.replace(' ', '-')
    return code


def course_search(term):
    for cid, course in courses():
        if term.lower() in course.lower():
            print_course(cid, course)


def print_course(code, course):
    print(f'\tCODE: {code: <4} |  {course}')


def print_courses(code='all'):
    for cid, course in courses(code):
        print_course(cid, course)


def valid_course(code):
    return code in {cid for cid, _ in courses()}
