from bs4 import BeautifulSoup
import json
from collections import defaultdict


def get_courses(html:str)-> dict:
    """

    :param html:
    :return: {
              "1": [
                {
                  "kurskod": "TATA65",
                  "kursnamn": "Diskret matematik",
                  "hp": "6*",
                  "termin": "Termin 1 HT 2025",
                  "period": "0",
                  "link": "/kurs/TATA65/ht-2025"
                },
                ]
                }
    """

    soup = BeautifulSoup(html, "html.parser")

    # Dictionary för att gruppera kurser per år
    yearly_courses = defaultdict(list)

    # Gå igenom varje termin (accordion)
    for semester_section in soup.select("section.accordion.semester"):
        term_header = semester_section.select_one("header h3")
        if not term_header:
            continue
        term_text = term_header.text.strip()  # t.ex. "Termin 1 HT 2025"

        # Gå igenom perioderna i varje termin
        tbody_tags = semester_section.select("tbody.period")
        for tbody in tbody_tags:
            period_row = tbody.find("tr")
            if not period_row:
                continue
            period_text = period_row.get_text(strip=True).replace("Period", "").strip()

            # Gå igenom varje kursrad
            for row in tbody.select("tr.main-row"):
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue


                # Hämta länk till kursen om den finns
                link_tag = cols[1].find("a")
                course_link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None

                course = {
                    "kurskod": cols[0].text.strip(),
                    "kursnamn": cols[1].text.strip(),
                    "hp": cols[2].text.strip(),
                    "termin": term_text,
                    "period": period_text,
                    "link": course_link
                }

                # Beräkna år från termin
                try:
                    term_num = int(term_text.split()[1])  # Termin 1 HT 2025 → 1
                except:
                    term_num = 0

                year = (term_num + 1) // 2  # Termin 1–2 → År 1, 3–4 → År 2, etc.
                skip_this = False

                for courses in yearly_courses[year]:
                    if courses["kurskod"] == cols[0].text.strip():
                        skip_this = True

                if skip_this:
                    continue

                yearly_courses[year].append(course)

    # Konvertera till vanlig dict för JSON-export
    yearly_courses_dict = dict(yearly_courses)

    # Skriv ut som JSON
    #print(json.dumps(yearly_courses_dict, indent=2, ensure_ascii=False))

    return yearly_courses_dict

if __name__ == "__main__":
    # Ladda HTML-filen
    with open("liuPoängplan.html", encoding="utf-8") as f:
        print(get_courses(f.read()))