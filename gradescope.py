"""
Creates a directory with files of all student submissions, checks for potential plagiarism, checks code for 
illegal imports, uploads submissions to Gradescope.

Usage: 
1. export the submissions from gradescope
2. unzip the directory and place it in this script's directory
3. export the grades from gradescope and place the grades file in this script's directory
5. Update the varibles in script
6. Run this script

WARNING: 
1. Ensure there are no other directories or csv files in the program's directory
   other than the submissions directory and grades file.
2. Ensure that the program is ran in its directory.

UPDATE THESE FIVE VARIABLES BELOW:
"""

# Name of the homework (ex. "HW4")
HW_NAME = 'HW1'
# List with all the files names of the hw
HW_FILE_NAMES = ["cel2fahr.py", "circle.py", "converter.py", "divide.py", "fahr2cel.py", "heart.py", "hello.py", "hybrid.py", "mad.py", "paint.py"]
# Email used for Gradescope
GRADESCOPE_EMAIL = 'nmchang@ucdavis.edu'
# Course and assignment IDs as integers
COURSE_ID = 475090
ASSIGNMENT_ID = 2562604
# You can get course and assignment IDs from the URL, e.g.
# https://www.gradescope.com/courses/1234/assignments/5678
# course_id = 1234, assignment_id = 5678

import os 
from shutil import copyfile
from collections import defaultdict
from dataclasses import dataclass, field
import re
import requests
import getpass

CSV_SEARCH_STR = "import "
MAIN_SEARCH_STR = "__name__"
CLUSTER_THRESH = 2
BASE_URL = 'https://www.gradescope.com'

class APIClient:
    def __init__(self):
        self.session = requests.Session()

    def post(self, *args, **kwargs):
        return self.session.post(*args, **kwargs)

    def log_in(self, email, password):
        url = "{base}/api/v1/user_session".format(base=BASE_URL)

        form_data = {
            "email": email,
            "password": password
        }
        r = self.post(url, data=form_data)

        self.token = r.json()['token']

    def upload_pdf_submission(self, course_id, assignment_id, student_email, filename):
        url = "{base}/api/v1/courses/{0}/assignments/{1}/submissions".format(
            course_id, assignment_id, base=BASE_URL
        )

        form_data = {
            "owner_email": student_email
        }
        files = {'pdf_attachment': open(filename, 'rb')}

        request_headers = {'access-token': self.token}
        r = self.post(url, data=form_data, headers=request_headers, files=files)
        return r

    def replace_pdf_submission(self, course_id, assignment_id, student_email, filename):
        url = "{base}/api/v1/courses/{0}/assignments/{1}/submissions/replace_pdf".format(
            course_id, assignment_id, base=BASE_URL
        )

        form_data = {
            "owner_email": student_email
        }
        files = {'pdf_attachment': open(filename, 'rb')}

        request_headers = {'access-token': self.token}
        r = self.post(url, data=form_data, headers=request_headers, files=files)
        return r

    def upload_programming_submission(self, course_id, assignment_id, student_email, filenames):
        url = "{base}/api/v1/courses/{0}/assignments/{1}/submissions".format(
            course_id, assignment_id, base=BASE_URL
        )

        form_data = {
            "owner_email": student_email
        }
        files = [('files[]', (filename, open(filename, 'rb'))) for filename in filenames]

        request_headers = {'access-token': self.token}
        r = self.post(url, data=form_data, headers=request_headers, files=files)
        # print(f"{r=} {r.content} {r.text}")
        return r

@dataclass
class CodeSubmission:
    code: str
    file_name: str
    student: str
    has_main: bool = False
    imports: list = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.student},{self.file_name},{' '.join(self.imports)},{self.has_main}\n"

@dataclass
class SameCode:
    code: str
    file_name: str
    students: list = field(default_factory=list)
    copies: int = field(default_factory=int)

#Logs into Gradescope and submits student submissions
def api_client(data_dict: dict) -> None:
    client = APIClient()
    #email = input("Please provide the email address on your Gradescope account: ")
    #email = 'aroy@ucdavis.edu'
    password = getpass.getpass('Enter your password: ')
    client.log_in(GRADESCOPE_EMAIL, password)
    # Use the APIClient to upload submissions after logging in, e.g:
    # client.upload_pdf_submission(66777, 309912, '841154914@qq.com', 'LTE_OUR_2.pdf')

    for pathname in os.listdir("./result"):
        if pathname == '.DS_Store':
            continue
        pathname1 = pathname.split('.')
        name = pathname1[0]
        client.upload_programming_submission(COURSE_ID, ASSIGNMENT_ID, data_dict.get(name), ['./result/'+name+'.py'])

def print_illegal_code_message():
    msg = """\ 
    ######################################################################
    1. Export the submissions from gradescope
    2. Unzip and directory and rename it to `submissions`
    3. Export the grades from gradescope
    3. Delete all the columns except first name, last name, submission_id
    4. Save the file as 'HW3_ID.csv'
    5. Run this script
    ######################################################################
    """
    print(msg)

def create_submission_name_map(metadata_file: str) -> dict:
    """
    Creates a map of submission_id and student name from submission metadata file
    """

    with open(metadata_file) as infile:
        line = infile.readline()
        data_dict = {}

        for line in infile:
            line = line.strip()
            data_list = line.split(',')
            status = data_list[7]
            if status.lower() == "missing":
                continue
            ID = data_list[8]
            first_name = data_list[0]
            last_name = data_list[1]
            name = first_name + " " + last_name
            data_dict[ID] = name

    return data_dict

def search_file(file_str: str) -> tuple[bool]:
    imports = []
    has_main = False
    match = re.search("import (\w+)", file_str)

    if match:
        imports = list(match.groups())
    
    if MAIN_SEARCH_STR in file_str:
        has_main = True
    return (imports, has_main)

def create_submission_objects(data_dict: dict) -> list[CodeSubmission]:
    """
    Parses through all the code files and looks for the search string
    """

    submissions : list[CodeSubmission] = []
    #data_dict = create_submission_name_map(hw_name+".csv")
    submissions_directory = "./submissions"
    for pathname in os.listdir(submissions_directory):
        if pathname == '.DS_Store' or pathname == 'submission_metadata.yml':
            continue
        dirname = os.path.basename(pathname)

        _, fileID = dirname.split('_')
        student_name = str(data_dict.get(fileID))
        for submission_file in os.listdir(os.path.join(submissions_directory, pathname)):
            if submission_file == '__MACOSX':
                continue
            file_name = os.path.basename(submission_file)
            file_path = os.path.join(submissions_directory,pathname,submission_file)

            try:
                with open(file_path, encoding="utf8", errors='ignore') as file:
                    file_str = file.read().strip()

                    submission_obj : CodeSubmission = CodeSubmission(code=file_str, file_name=file_name, student=student_name)
                    submission_obj.imports, submission_obj.has_main = search_file(file_str)

                    submissions.append(submission_obj)

            except IsADirectoryError:
                continue
    return submissions

def filter_guilty_submissions(subs: list[CodeSubmission]) -> list[str]:
    guilty_list = []
    for sub in subs:
        if sub.imports or sub.has_main:
            guilty_list.append(str(sub))

    return guilty_list

#Search for illegal imports and functions in submissions
def illegal_code(data_dict: dict) -> None:
    #print_illegal_code_message()
    submissions_obj_list = create_submission_objects(data_dict)
    lines = filter_guilty_submissions(submissions_obj_list)

    with open(f"{HW_NAME}imports.csv", "w") as outfile:
        outfile.write("student_name,file_name,imports,__name__=='__main__'\n")
        outfile.writelines(lines)

def print_plag_message():
    msg = """\ 
    ######################################################################
    1. Export the submissions from gradescope
    2. Unzip and directory and rename it to `submissions`
    3. Export the grades from gradescope
    4. Save the file as 'HW3_ID.csv' or the equivalent
    5. Run this script
    ######################################################################
    """
    print(msg)
    
def _tstrip_lines(lines: str, char = "#"):
    """
    - Gets rid of all the initial lines (lines from the top) that starts with # 
    - Once code line starts, it does not strip any more lines
    """
    idx = 0
    lines_list = lines.strip().split("\n")
    for line in lines_list:
        
        if line.strip().startswith(char) or line.strip() == "":
            idx += 1
        else:
            break
    lines_list = lines_list[idx:]
    return " ".join(lines_list)

def create_same_code_clusters(data_dict: dict) -> list[SameCode]:
    """
    Parses through all the code files and creates a SameCode dataclass for every unique code (after stripping)
    All the SameCode dataclass is returned in a list
    """
    cluster_dict : dict[str, SameCode] = {}
    submissions_directory = "./submissions"
    for pathname in os.listdir(submissions_directory):
        if pathname == '.DS_Store' or pathname == 'submission_metadata.yml':
            continue
        dirname = os.path.basename(pathname)

        _, fileID = dirname.split('_')
        student_name = str(data_dict.get(fileID))
        for submission_file in os.listdir(os.path.join(submissions_directory, pathname)):
            if not submission_file.endswith(".py"):
                continue
            file_name = os.path.basename(submission_file)
            file_path = os.path.join(submissions_directory,pathname,submission_file)

            try:
                with open(file_path, encoding="utf8", errors='ignore') as file:
                    file_str = file.read().strip()
                    file_str = _tstrip_lines(file_str) # comment this line if top strip not required
                    if file_str not in cluster_dict:
                        same_code_obj = SameCode(code=file_str, file_name=file_name)
                        cluster_dict[file_str] = same_code_obj

                    else:
                        same_code_obj = cluster_dict[file_str]

                    same_code_obj.copies += 1
                    same_code_obj.students.append(student_name)

            except IsADirectoryError:
                continue
    return list(cluster_dict.values())


def filter_same_code_cluster_and_format_lines(same_code_cluster: list[SameCode]) -> list[str]:
    """
    filter the same_code_obj objects based off the clustering threshold and format lines
    """

    
    lines = []
    for same_code_obj in same_code_cluster:
        if same_code_obj.copies >= CLUSTER_THRESH:
            line = f"{same_code_obj.file_name},{' & '.join(same_code_obj.students)}\n"
            lines.append(line)

    return lines

#Cluster same submissions
def plag(data_dict: dict) -> None:
    #print_plag_message()
    same_code_cluster : list[SameCode] = create_same_code_clusters(data_dict)
    lines : list = filter_same_code_cluster_and_format_lines(same_code_cluster)
    outfile = f"{HW_NAME}plag.csv"
    with open(outfile, "w") as fobj:
        fobj.write("problem_name,student_names\n")
        fobj.writelines(lines)

#Concatinate student submissions from the `submissions` directory 
#and copy it to the `result` directory where each file is named after the student
def hwStyle(data_dict: dict) -> None:
    if not os.path.exists("./result"):
        os.makedirs("result")
        #print("Created a new directory: result")
    for pathname in os.listdir("./submissions"):
        if pathname == '.DS_Store':
            continue
        dirname = os.path.basename(pathname)

        fileID = dirname.split('_')
        fileID = fileID[1]
        dst = str(data_dict.get(fileID))

        output_file_str = ""
        for file in HW_FILE_NAMES:
            if os.path.isfile(os.path.join("./submissions",dirname,file)):
                with open(os.path.join("./submissions",dirname,file)) as fobj:
                    fobj_str = fobj.read()
                    output_file_str += f"\n{fobj_str}"

        with open(os.path.join("./result", dst + ".py"), "w") as fobj:
            fobj.write(output_file_str)

#Grabs dict for all later programs
def get_data_dict() -> dict:
    with open(f'{HW_NAME}.csv') as infile: # update this for every file
        line = infile.readline()
        data_dict = {}
        for line in infile:
            line = line.strip()
            data_list = line.split(',')
            first_name = data_list[0]
            last_name = data_list[1]
            name = first_name + " " + last_name
            status = data_list[7]
            if status.lower() == "missing":
                continue
            ID = data_list[8]
            data_dict[ID] = name
            std_email = data_list[3]
            data_dict[name] = std_email
    return data_dict

#Renames the csv file and directory
def rename_files():
    files_list = os.listdir("./")
    for file in files_list:
        if file.endswith(".csv"):
            os.rename(file, f'{HW_NAME}.csv')
        if os.path.isdir(os.path.join('./', file)):
            os.rename(file, 'submissions')

def main():
    rename_files()
    data_dict = get_data_dict()
    print("Reformatting submissions directory...") 
    hwStyle(data_dict)
    print("Checking for Plagiarism...")
    plag(data_dict)
    print("Checking for Illegal Imports...")
    illegal_code(data_dict)
    print("Running API Client to submit files...")
    api_client(data_dict)
    print("Complete!")

# Driver Code 
if __name__ == '__main__':  
    main()