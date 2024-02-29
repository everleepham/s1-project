import mysql.connector
from datetime import datetime
import os


courses = ['AI_DATA_PREP', 'AI_DATA_SCIENCE_IN_PROD', 'CS_DATA_PRIV', 'CS_SOFTWARE_SECURITY', 'DT_RDBMS', 'MK_COM_FOR_LEADER', 'PG_PYTHON', 'PM_AGILE', 'SE_ADV_DB', 'SE_ADV_JAVA', 'SE_ADV_JS']

original = ".\sites\course_grade.html"

def connect(
    db_host: str, db_port: int, db_user: str, db_password: str, db_name: str
) -> mysql.connector.connection.MySQLConnection:
    """
    Connects to the MySQL database
    :return: a connection object
    """
    conn = mysql.connector.connect(
        host=db_host, port=db_port, user=db_user, password=db_password, database=db_name
    )
    return conn


host = "localhost"
port = 3245
user = "admin"
password = "admin"
database_name = "project"

for course in courses:
    new_file = f"./sites/course_grade_html/{course}.html"

    connection = connect(host, port, user, password, database_name)
    cursor = connection.cursor()

    cursor.execute(
        "select s.student_epita_email, c.contact_first_name, c.contact_last_name, s.student_population_period_ref, " 
        "s.student_population_code_ref,g.grade_course_code_ref, sum(g.grade_score * e.exam_weight) / sum(e.exam_weight) as grade, c2.course_name  "
        "from contacts c "
        "join students s on c.contact_email = s.student_contact_ref "
        "join grades g on s.student_epita_email = g.grade_student_epita_email_ref "
        "join exams e on g.grade_course_code_ref = e.exam_course_code "
        "join courses c2 on e.exam_course_code = c2.course_code "
        f"where e.exam_course_code  like '{course}' "
        "group by e.exam_course_code, s.student_epita_email, c2.course_name  "
    )

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    new_file = f"./sites/course_grade_html/{course}.html"

    with open(original, 'r') as f:
        html = f.read()

    with open('./sites/gcourse_row_frag.html', 'r') as file:
        gcourse_row_fragment = file.read()

    gcourse_rows_fall = ''
    gcourse_rows_spring = ''

    for i, tup in enumerate(data):
        grade_str = str(tup[6])
        grade = grade_str.rstrip('0').rstrip('.') if '.' in grade_str else grade_str
        html = html.replace('%course%', tup[7])
        temp = gcourse_row_fragment.replace('%course%', tup[5])
        temp = temp.replace('%major%', tup[4])
        temp = temp.replace('%email%', tup[0])
        temp = temp.replace('%student_fname%', tup[1])
        temp = temp.replace('%student_lname%', tup[2])
        temp = temp.replace('%grade%', grade)
        if tup[3] == 'FALL':
            gcourse_rows_fall += temp
        else:
            gcourse_rows_spring += temp

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%d/%m/%Y')

    html = html.replace('%datetime%', formatted_datetime)
    html = html.replace('%gcourse_rows_fall%', gcourse_rows_fall)
    html = html.replace('%gcourse_rows_spring%', gcourse_rows_spring)

    with open(new_file, "w") as f:
        f.write(html)

    print(f"Created {new_file}")