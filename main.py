from jinja2 import Environment, FileSystemLoader
from generator import fetch_courses
import requests
from urllib.parse import urlparse

# set these to generate the final html file for the docs
EDUCATION_NAME = "Civilingenjör i Datateknik"
EDUCATION_CODE = "6CDDD"

if EDUCATION_CODE == "" or EDUCATION_NAME == "":
    print("Vars not set read main.py file")
    exit(1)

# set url to the url to avoid the input prompt
url = None
if not url:
    url = input("Paste full url to LiU education ex (civilingenjör i datateknik):\n")

# Validate if input is url
result = urlparse(url)
if not all([result.scheme, result.netloc]):
    print("input is not a valid url")
    exit(1)

response = requests.get(url)

# generating the data fro a education
course_json = fetch_courses(response.content)

# Load templates from current directory
env = Environment(loader=FileSystemLoader('./templates'))

# Load the template
template = env.get_template('index.html')

# Render the template with variables
output = template.render(
    yearly_courses=course_json,
    EDUCATION_NAME=EDUCATION_NAME
)

with open(f"docs/{EDUCATION_CODE}.html", "w") as f:
    f.write(output)
