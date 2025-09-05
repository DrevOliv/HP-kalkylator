import json
from bs4 import BeautifulSoup
import requests

def get_points_for_course(course_code:str)-> [dict]:
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

    response = requests.get(f"https://studieinfo.liu.se/kurs/{course_code}")

    soup = BeautifulSoup(response.text, "html.parser")

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


def get_master_profiles() -> dict:
    # Läs in HTML-filen
    request = requests.get("https://studieinfo.liu.se/program/6CDDD#curriculum")

    soup = BeautifulSoup(request.text, "html.parser")

    data = {"master_inriktningar": {}}

    # Hämta masterinriktningar från select-menyn
    specializations = soup.select("#specializations-filter option")
    for opt in specializations:
        value = opt.get("value")
        text = opt.text.strip()
        if value and text != "Alla":
            data["master_inriktningar"][text] = []

    # Hämta alla terminer
    terms = soup.select("section.accordion.semester")
    for term in terms:
        term_name = term.find("h3").get_text(strip=True)  # t.ex. "Termin 7 HT 2028"
        termin_nummer = None
        for word in term_name.split():
            if word.isdigit():
                termin_nummer = int(word)
                break

        # Gå igenom alla "specialization"-block
        specs = term.select("div.specialization")
        for spec in specs:
            inriktning_kod = spec.get("data-specialization", "").strip()
            if not inriktning_kod:
                continue  # hoppa över allmänna kurser

            # Leta reda på inriktningsnamnet via select-listan
            inriktning_namn = None
            for opt in specializations:
                if opt.get("value") == inriktning_kod:
                    inriktning_namn = opt.text.strip()
                    break

            if not inriktning_namn:
                continue

            rows = spec.select("tr.main-row")
            for row in rows:
                cols = row.find_all("td")
                if not cols:
                    continue
                kurskod = cols[0].text.strip()
                kursnamn = cols[1].text.strip()
                hp = cols[2].text.strip()
                nivå = cols[3].text.strip()
                block = cols[4].text.strip()
                typ = cols[5].text.strip()  # O/V/F

                points = get_points_for_course(kurskod)

                kursinfo = {
                    "kurskod": kurskod,
                    "kursnamn": kursnamn,
                    "termin": termin_nummer,
                    "hp": hp,
                    "nivå": nivå,
                    "block": block,
                    "typ": typ,
                    "examinering": points,
                }

                data["master_inriktningar"][inriktning_namn].append(kursinfo)

    return data


data = get_master_profiles()


# Spara som JSON
with open("master_inriktningar.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("JSON-fil skapad: master_inriktningar.json")
