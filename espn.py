from lxml import etree
import requests
from flask import Flask, jsonify

app = Flask(__name__)
app.debug = True

ESPN = "http://www.espn.co.uk/football/sport/match/index.html?event=3;type=results"
HEADING_XPATH = "td/a/text()"

def __get_heading_from_row(r):
    return r.xpath(HEADING_XPATH)[0]

def __is_heading(element):
    return element.get("class") == "heading"

''' Extract a score from a string, format=home-away eg. 1-0 '''
def __parse_score(score_string):
    score = score_string.strip()
    scores = score.split('-')
    return {
        "home_score" : scores[0],
        "away_score" : scores[1]
    }

@app.route("/")
def index():
    r = requests.get(ESPN)
    # do some error handling from requests
    html = r.text

    x = etree.HTML(html)
    rows = x.xpath("//*[@id=\"content\"]/div[2]/table/tbody/tr")

    dates = []
    matches = []
    day = {}
    for r in rows:
        if __is_heading(r):
            # we have finished processing last day
            if len(matches) > 0:
                day['matches'] = matches
                dates.append(day)

            # start again with new day
            day = {"date": __get_heading_from_row(r)}
            matches = []
        else:
            cols = r.xpath("td")

            match = {
                "match_time" : cols[1].xpath("text()")[0].strip(),
                "home_team" : cols[2].xpath("a/text()")[0],
                "score" : __parse_score(cols[3].xpath("text()")[0]),
                "away_team" : cols[4].xpath("a/text()")[0],
                "report" : cols[len(cols)-1].xpath("a/@href")[-1]
            }
            matches.append(match)

    return jsonify(
        {
            "competition" : "English Premier League",
            "match_days": dates
        }
    )

if __name__ == "__main__":
    app.run()
