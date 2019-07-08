from flask import Flask, render_template, request
import sqlite3
#import numpy

app = Flask(__name__)

db_name = "draftQbs.db"
db = sqlite3.connect(db_name, check_same_thread = False)
cur = db.cursor()

@app.route("/", methods = ["GET", "POST"])
def root():
    return render_template("root.html")

@app.route("/statBase", methods = ["GET", "POST"])
def statBase():
    #cur.execute(".mode html")
    cur.execute("SELECT Year, Round, Pick, First, Last, Team, College, Conference, FranchiseQB, Completions, Attempts, CompPct, Yards, YardsPerAtt, TD, INT, TDtoINTRatio, AYperA, NFLRating, TDPct, INTPct FROM QB WHERE Year > 1999;")
    results = cur.fetchall()
    print results
    return render_template("home.html", data=results);

@app.route("/filter", methods = ["GET", "POST"])
def filter():
    year = request.form["year"]
    round = request.form["round"]
    college = request.form["college"]
    conference = request.form["conference"]

    #print year
    #print round
    #print college
    #print conference

    stringYear = ""
    andRound = ""
    stringRound = ""
    andCollege = ""
    stringCollege = ""
    andConf = ""
    stringConf = ""
    
    if conference != "":
        andConf = " AND "
        stringConf = " QB.Conference = %s" % ("'" + conference + "'")

    if college != "":
        andCollege = " AND "
        stringCollege = " QB.College = %s" % ("'" + college + "'")
    elif year == "" and round == "":
        andConf = ""

    if round != "":
        andRound = " AND "
        stringRound = " QB.Round = %s" % (str(round))
        print "y" + round + "y"
    elif year == "":
        andCollege = ""

    if year != "":
        stringYear = " QB.Year = %s" % (str(year))
        print "y" + year + "y"
    else:
        andRound = ""


    command = "SELECT * from QB WHERE"
    addYear = "%s" % (stringYear)
    addRound = "%s%s" % (andRound, stringRound)
    addCollege = "%s%s" % (andCollege, stringCollege)
    addConf = "%s%s" % (andConf, stringConf)
    command += addYear + addRound + addCollege + addConf

    #print command
    cur.execute(command)

    #cur.execute("SELECT * from QB WHERE QB.Conference = " + "'" + conference + "'" + " AND QB.Round = " + round + " AND QB.Year = " + year + " AND QB.College = " + "'" + college + "'" + ";")
    results = cur.fetchall()

    return render_template("home.html", data=results);

@app.route("/scoreBase", methods = ["GET", "POST"])
def scoreBase():
    cur.execute("SELECT Year, Round, Pick, First, Last, Team, College, Conference, FranchiseQB, CompPctScore, YardsPerAttScore, TDtoINTScore, AYPerAScore, NFLRatingScore, TDPctScore, INTPctScore, GeoMean, GeoFirstThree FROM QB WHERE Year > 1999;")
    results = cur.fetchall()
    
    print results[0]

    cur.execute("SELECT * FROM AVGS;")
    avgs = cur.fetchall()

    return render_template("scoreBase.html", data=results, averages=avgs);

@app.route("/score", methods = ["GET", "POST"])
def score():
    first = request.form["first"]
    last = request.form["last"]
    stat = request.form["stat"]

    cur.execute("SELECT * from QB WHERE QB.First = " + "'" + first + "'" + " AND QB.Last = " + "'" + last + "';")
    data = cur.fetchall()

    x = 0
    if stat == "Comp%":
        x = 10
    elif stat == "Y/A":
        x = 12
    elif stat =="TD:INT":
        x = 15

    #print stat 
    ownStat = data[0][x]
    #print "ownStat"
    #print ownStat

    currYear = data[0][0]
    cur.execute("SELECT * from QB WHERE QB.Year = " + str(currYear) + " OR QB.Year = " + str(currYear + 1) + " OR QB.Year = " + str(currYear - 1) + ";")
    era = cur.fetchall()

    eraValues = []
    for row in era:
        eraValues.append(row[x])
    #print eraValues

    eraSum = 0
    for item in eraValues:
        eraSum += item
    eraAvg = float(eraSum) / len(eraValues)
    #print eraAvg

    eraSquareDist = []
    for item in eraValues:
        squareDist = (item - eraAvg)**2
        eraSquareDist.append(squareDist)
    #print eraSquareDist
    
    eraSumSD = 0
    for item in eraSquareDist:
        eraSumSD += item
    eraMeanSD = float(eraSumSD) / (len(eraSquareDist)-1)
    #print eraMeanSD

    eraSdev = eraMeanSD**(0.5)
    #print eraSdev

    numSdevs = (ownStat - eraAvg) / eraSdev
    #print numSdevs

    prodScore = (numSdevs * 15) + 100
    #print "PRODUCTION SCORE"
    #print prodScore
    #print "!!!!!!!"

    return render_template("home.html", firstName = first, lastName = last, statistic = stat, prodScore = prodScore, data = era)

    
@app.route("/scorecard", methods = ["GET", "POST"])
def scorecard():
    first = request.form["first"]
    last = request.form["last"]

    cur.execute("SELECT * from QB WHERE QB.First = " + "'" + first + "'" + " AND QB.Last = " + "'" + last + "';")
    data = cur.fetchall()
    
    newFirst = data[0][3]
    newLast = data[0][4]
    compPct = data[0][10]
    yardsPerAtt = data[0][12]
    tdToInt = data[0][15]
    adjYardsPerAtt = data[0][16]
    nflRating = data[0][17]
    tdPct = data[0][18]
    intPct = data[0][19]

    franchiseQB = data[0][20]
    if franchiseQB == "Early":
        franchiseQB = "Too early to tell"

    compPctScore = data[0][21]
    yardsPerAttScore = data[0][22]
    tdToIntScore = data[0][23]
    adjYPAScore = data[0][24]
    nflRatingScore = data[0][25]
    tdPctScore = data[0][26]
    intPctScore = data[0][27]

    allSeven = data[0][28]
    firstThree = data[0][29]

    #print data

    cur.execute("SELECT * FROM AVGS;")
    avgs = cur.fetchall()

    #print avgs

    return render_template("scorecard.html", First = newFirst, Last = newLast, CompPct = compPct, YardsPerAtt = yardsPerAtt, TDtoINT = tdToInt, AYPerA = adjYardsPerAtt, NFLRating = nflRating, TDPct = tdPct, INTPct = intPct, CompPctScore = compPctScore, YardsPerAttScore = yardsPerAttScore, TDtoINTScore = tdToIntScore, AYPerAScore = adjYPAScore, NFLRatingScore = nflRatingScore, TDPctScore = tdPctScore, INTPctScore = intPctScore, AllSeven = allSeven, FirstThree = firstThree, averages = avgs, FranchiseQB = franchiseQB)

if __name__ == "__main__":
    app.debug = True
    app.run()
