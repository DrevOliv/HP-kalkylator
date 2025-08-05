from bs4 import BeautifulSoup

def get_points_for_course(html:str)-> [dict]:
    """

    :param html:
    :return: [
        {
        'Kod': 'UPG1',
        'Benämning': 'Inlämningsuppgifter',
        'Omfattning': '2'
        },
        {
        'Kod': 'TEN1',
        'Benämning': 'Skriftlig tentamen',
        'Omfattning': '4'
        }
        ]
    """

    soup = BeautifulSoup(html, "html.parser")

    # Find all tables and locate the one with Kod, Benämning, Omfattning
    examinations = []
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if "Kod" in headers and "Benämning" in headers and "Omfattning" in headers:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 3:
                    kod = cells[0].get_text(strip=True)
                    benamning = cells[1].get_text(strip=True)
                    omfattning = cells[2].get_text(strip=True).strip(" hp")
                    examinations.append({
                        "Kod": kod,
                        "Benämning": benamning,
                        "Omfattning": omfattning
                    })
            break  # Stop after finding the correct table
    #print(examinations)

    return examinations


if __name__ == "__main__":
    # Load the HTML file
    with open("liuKursExamination.html", encoding="utf-8") as f:
        print(get_points_for_course(f.read()))