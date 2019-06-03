import mechanicalsoup
from bs4 import BeautifulSoup
import csv
import re

def scoreCheck(score, outof, countOfRatings):
    if(countOfRatings == 0):
        return "Not yet rated/Unknown rating"
    else:
        print(outof)
        return (score/outof) * 10


username = input("Please enter your username:") # example "13mdg5@queensu.ca". Remove the <> signs for all cases
password = input("Please enter your password:") #example "vd56fjsr"
profile = input("Please paste what comes after http://mindsumo.com when you are on your profile page:") #example "/user/13mdg5"
# These values are filled by the user
url = "https://www.mindsumo.com/login"
#username = "<Put  your email here>" # example "13mdg5@queensu.ca". Remove the <> signs for all cases
#password = "<put your password here>" #example "vd56fjsr"
#profile = "<put the portion of the url which comes after mindsumo.com when you go to your profile page here" #example "/user/13mdg5"
baseurl = "https://www.mindsumo.com"


with open('mindsumoResults.csv', 'w') as resetFile:
    writer = csv.writer(resetFile, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Company Name", "Challenge Title", "Score Earned", "Ranking in Challenge", "Payment Earned", "Image URL"])
resetFile.close()
browser = mechanicalsoup.StatefulBrowser(raise_on_404=True)
browser.open(url)

form = browser.select_form('form[id="new_user"]')
form['user[email]'] = username
form['user[password]'] = password

response = browser.submit_selected()
pageCount = 1
while (pageCount < 14):
    response = browser.open(baseurl + profile + "?page={0}&sort=rating".format(pageCount))
    pageCount += 1
    soup = response.text
    soup3 = BeautifulSoup(soup, 'lxml')
    mydivs = soup3.findAll("div", {"class": "contest_snapshot_border"})
    #print(mydivs)
    for divs in mydivs:
        challengelink = divs.find("a")
        challengelink = baseurl + challengelink.attrs['href']
        response = browser.open(challengelink)
        soup = response.text
        soup3 = BeautifulSoup(soup, 'lxml')
        #print(soup3)
        winnerlist = soup3.findAll("tr", {"class": "winner_line"})
        #print(winnerlist)
        winnerCount = 0
        totalPayment = 0
        for winners in winnerlist:
            result = winners.find("a", {"class" : "table_winner_link"})
            if (result is None):
                print("No placement has been provided.")
                break
            #print(result)
            if (result.attrs['href'] == profile):
                winnerCount += 1
                print("You are in " + str(winnerCount) + " place.")
                payment = winners.find("td", {"class": "points"})
                payment = re.findall(r'\d+', payment.text)
                totalPayment = (payment[0] + "." + payment[1])
                print(totalPayment)
                #payment = payment.text.split('"')[1].strip()
                #print("Your payment for this is {0}".format(payment))
                break
            else:
                winnerCount += 1
            if(winnerCount == len(winnerlist)):
                winnerCount = "Not a winner"
                totalPayment = 0

        imgurl = divs.find("img", {"alt": "challenge_snapshot"})
        company =  divs.find("td", {"class" : "byline"})
        ratingdata = divs.findAll("td", {"class" : "tri_rating"})
        score = 0
        outof = 0
        countOfRatings = 0
        for ratings in ratingdata:
            score += float(ratings.attrs['title'].split("/")[0])
            outof += float(ratings.attrs['title'].split("/")[1])
            countOfRatings += 1
        if (outof == 0):
            print("No score provided")
        else:
            print(str(score) + "out of " + str(outof))
        titleset = divs.find("td", {"class" : "contest_snapshot_col2"})
        title = titleset.find("div", {"class" : "title"})
        print(title.text)
        print(imgurl.attrs['src'])
        print(company.text.strip())
        with open('mindsumoResults.csv', mode='a') as mindsumoResults:
            writer = csv.writer(mindsumoResults, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([company.text.strip(), title.text, scoreCheck(score, outof, countOfRatings), winnerCount,totalPayment, imgurl.attrs['src']])
            #mindsumoResults.flush()
        mindsumoResults.close()
        winnerCount = 0;


