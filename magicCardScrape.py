#Mark Czuy Fall 2016
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import urllib2
import re
import csv
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from mpl_toolkits.basemap import Basemap
from collections import Counter
from geopy.exc import GeocoderTimedOut
import datetime

SLList = []
DLList = []
RDDict = {}
cities = []
players = []
deck = []
date = []
durls = []
topplayers = []
pnames = Counter()
placedate = {}
dnames = Counter()
cname = []
type = []
mana  = []
rarity  = []
artist = []
edition = []
release = []
CNpTaM = []
soidata = []
alphadata = []

def getSetLinks(url):
     page = urllib2.urlopen(url + "/sitemap.html")
     soup = BeautifulSoup(page, "lxml")
     #print soup.prettify()
     allLinks = soup.find_all("a")
     for link in allLinks:
          if str(link.get("href")).endswith("/en.html"):
               SLList.append(link.get("href"))
     print("List of Links Complete")

def getReleaseDates():
     with open('releasedates.csv', 'rb') as f:
          for row in csv.DictReader(f, delimiter='\t'):
               RDDict[str(row["Set"]).rstrip()] = str(row['Released']).rstrip()
               
def createCardCSV(prefix):
     with open('cards.csv', 'w') as outfile:
          headers = ['Card name','Type','Mana','Rarity','Artist','Edition','Release']
          writer = csv.writer(outfile, delimiter="\t", quotechar='"', quoting=csv.QUOTE_ALL)
          writer.writerow(headers)
          
          getReleaseDates()
          
          for suffix in SLList:
               url = prefix + suffix
               
               page = urllib2.urlopen(url)
               lines = page.readlines()
               for i in xrange(len(lines)):
                    if lines[i].find("[ 1-") > 0:
                         m = i
                         break
                    else: m = -1
               #Needed to deal with the special 1 card sets which do not have the number of cards in the HTML
               if m!= -1:
                    searchObj = re.findall(r"\d+", lines[m])
               else: searchObj = [1,1]
          
               for i in xrange(len(lines)):
                    if lines[i].find("Card name") > 0:
                         n = i
                         break
          
               for i in xrange(int(searchObj[1])):
                    lnum = n+11*(i+1)
                    name = re.sub('\n','',(re.sub('    ','',(re.sub('<[^<]+?>','',str(lines[lnum]))))))
                    type = re.sub('—','-',(re.sub('\n','',(re.sub('    ','',(re.sub('<[^<]+?>', '', str(lines[lnum+1]))))))))
                    mana = re.sub('\n','',(re.sub('    ','',(re.sub('<[^<]+?>', '', str(lines[lnum+2]))))))
                    rarity = re.sub('\n','',(re.sub('    ','',(re.sub('<[^<]+?>', '', str(lines[lnum+3]))))))
                    artist = re.sub('\n','',(re.sub('    ','',(re.sub('<[^<]+?>', '', str(lines[lnum+4]))))))
                    edition = re.sub('\n','',(re.sub('     ','',(re.sub('<[^<]+?>', '', str(lines[lnum+5]))))))
                    release = ""
                    if edition in RDDict:
                         release = RDDict[edition]
                    writer.writerow((name,type,mana,rarity,artist,edition,release)) 

def getDeckLinks(url):
     with open('decks.csv', 'w') as outfile:
          headers = ['Deck','Finish','Player','Event','Format','Date','Location','URL']
          writer = csv.writer(outfile, delimiter="\t", quotechar='"', quoting=csv.QUOTE_ALL)
          writer.writerow(headers)
          url = url
          tcount = 0
          for i in xrange(169):
               req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
               con = urllib2.urlopen( req )
               soup = BeautifulSoup(con, "lxml")
               count = 0
               deckinfo= []
               tcount += 1
               durl = []
               dnum = 0
               for link in soup.find_all("a"):
                    if str(link.get("href")).startswith("http://sales.starcitygames.com//deckdatabase/displaydeck.php?DeckID="):
                         durl.append(link.get("href"))
               for row in soup.find_all('td',attrs={'class' :["deckdbbody" , "deckdbbody2"]}):
                    count +=1
                    t = row.text.encode('utf-8').strip()
                    deckinfo.append(t)
                    if count == 7:
                         deckinfo[6] = re.sub('[^\w]', ' ', deckinfo[6]).strip()
                         deckinfo.append(durl[dnum])
                         writer.writerow(deckinfo)
                         dnum += 1
                         count = 0
                         deckinfo= []
               print tcount
               url = "http://sales.starcitygames.com//deckdatabase/deckshow.php?&t[C1]=3&start_date=02/21/2004&end_date=05/15/2016&start=1&finish=8&order_1=date%20desc&order_2=finish&start_num=25&start_num=" + str(tcount*25) + "&limit=25"
     
def pictures():
     
     year =  []
     month = []
     day =   []
     for d in date:
          ds = d.split('-')
          year.append(int(ds[0]))
          month.append(int(ds[1]))
          day.append(int(ds[2]))
          
     
     plt.hist(year)
     plt.title("Number of Legacy Events by Year")
     plt.xlim([2005,2016])
     plt.xlabel("Year")
     plt.ylabel("Number of Events")
     plt.show()
     
     plt.hist(month)
     plt.xlim([0,13])
     plt.title("Histogram for Legacy Events by Month")
     plt.xlabel("Month")
     plt.ylabel("Number of Events")
     plt.show()

     
     
     map = Basemap(resolution='l',projection='merc')
     map.drawcoastlines()
     map.drawcountries()
     
     eventLocals = Counter()
     for city in cities:
          if (city == "") or (city == 'Magic Online'):
               a = 1
               #print("not a city")
          else:
               eventLocals[city] += 1
     print len(eventLocals)
     
     for cname,count in eventLocals.items():
          geolocator = Nominatim()
          #http://stackoverflow.com/questions/27914648/geopy-catch-timeout-error
          try:
               location = geolocator.geocode(cname, timeout=10)
               if location:
                    clong = location.longitude
                    clat = location.latitude
                    x,y = map(clong,clat)
                    map.plot(x,y, 'ro', markersize=count, label = cname)

          except GeocoderTimedOut as e:
               print("Error: geocode failed on input %s with message %s"%(location, e.message))
          
     plt.title("Map of All Cities That Have Held Legacy Tournaments")
     plt.show()
     
     
     for name in deck:
          dnames[name] += 1
     for k,v in dnames.items():
          if v < 10:
               del dnames[k]
     
     plt.bar(range(len(dnames)), dnames.values(), align='center')
     plt.xticks(range(len(dnames)), dnames.keys())
     locs, labels = plt.xticks()
     plt.setp(labels, rotation=90)

     plt.title("Number of Top 8 Finishes by Archetype")
     plt.xlabel("Deck Name")
     plt.show()
     
     
     plt.bar(range(len(pnames)), pnames.values(), align= 'center')
     plt.xticks(range(len(pnames)), pnames.keys())
     locs, labels = plt.xticks()
     plt.setp(labels, rotation=90)

     plt.title("Players with 5 or More Top 8 Finishes")
     plt.xlabel("Players Name")
     plt.show()
     
     
     
     markers = ["x","o","+","*","p","D"]
     colors =["blue","black","red","yellow","green","orange"]
     c=0
     for player in topplayers:
          pwins = 0
          pplotx = []
          pploty = []
          for day in reversed(date):
               if day in placedate[player]:
                    pwins  += 1
                    x = datetime.datetime.strptime(day,'%Y-%m-%d').date()
                    pplotx.append(x)
                    pploty.append(pwins)
          plt.plot(pplotx, pploty, label=player, color=colors[c], markersize=6, marker=markers[c])
          c += 1
          pwins = 0
     plt.legend(loc=2,ncol=3,fontsize=8)
     plt.xlabel('Year')
     plt.ylabel('Number of Wins to Date')
     plt.title("Top 6 Winning Players - Wins By Date")
     plt.show()
          
def getDataLists():
     with open('decks.csv', 'rb') as f:
          reader = csv.DictReader(f, delimiter='\t')
          for row in reader:
               if row['Format'] == 'Legacy':
                    if row['Finish'] == '1st':
                         cities.append(row['Location'])
                    if row['Date'] in date:
                         a=1
                    else:
                         date.append(row['Date'])
                    
                    players.append(row['Player'])
                    deck.append(row['Deck'])
                    durls.append(row['URL'])
                    
                    if row['Player'] in placedate.keys():
                         placedate[row['Player']].append(row['Date'])
                    else:
                         placedate.setdefault(row['Player'], [])
                         placedate[row['Player']].append(row['Date'])
     for name in players:
          pnames[name] += 1
     for k,v in pnames.items():
          
          if v < 5:
               del pnames[k]
          if v >= 15:
               topplayers.append(k)
     
def getCardlistsData():
     with open('cards.csv', 'rb') as f:
          for row in csv.DictReader(f, delimiter='\t'):
               cname.append(row['Card name'])
               type.append(row['Type'])
               mana.append(row['Mana'])
               rarity.append(row['Rarity'])
               artist.append(row['Artist'])
               edition.append(row['Edition'])
               release.append(row['Release'])
               CNpTaM.append((row['Card name'],row['Type'],row['Mana']))
               if row['Edition'] == "Limited Edition Alpha":
                    alphadata.append((row['Card name'], row['Type'], row['Rarity'], row['Mana']))
               if row['Edition'] == "Shadows over Innistrad":
                    soidata.append((row['Card name'], row['Type'], row['Rarity'], row['Mana']))

def cardWork():
     cardCount = Counter()
     typeCount = Counter()
     colorCounts = Counter()
     for card, ctype, manacost in CNpTaM:
          cardCount[card] += 1
          if " - " not in ctype:
               if "/" not in ctype:
                    typeCount[ctype] += 1
          else:
               sctype = ctype.split(" - ")
               typeCount[sctype[0]] += 1
     cardmana = []
     for card, ctype, manacost in CNpTaM:
          if card not in cardmana:
               cardmana.append(card)
               if "U" in manacost:
                    colorCounts["Blue"] += 1
               if "R" in manacost:
                    colorCounts["Red"] += 1
               if "G" in manacost:
                    colorCounts["Green"] += 1
               if "B" in manacost:
                    colorCounts["Black"] += 1
               if "W" in manacost:
                    colorCounts["White"] += 1
               if manacost == "":
                    colorCounts["Colorless"] +=1
               if manacost.isdigit():
                    colorCounts["Colorless"] +=1
     labels = colorCounts.keys()
     sizes = colorCounts.values()
     color = colorCounts.keys()
     for c in xrange(len(color)):
          if color[c] == "Colorless":
               color[c] = "Brown"
          if color[c] == "Black":
               color[c] = "Dimgrey"
     plt.pie(sizes,labels=labels, colors=color,
     autopct='%.0f%%', startangle=90)
     plt.title("Percentage of Total Cards Printed in Each Color")
     plt.show()
    
def setCompWork():
     cardmana = []
     colorCounts = Counter()
     catype = Counter()
     for card, atype, rarity, mana in alphadata:
          if "Enchant" in atype:
               catype["Enchantment"] += 1
          if "Summon" in atype:
               catype["Creature"] += 1
          if "Artifact" in atype:
               catype["Artifact"] += 1
          if "In" in atype:
               catype["Instant"] += 1
          if "Sorcery" in atype:
               catype["Sorcery"] += 1
          if card not in cardmana:
               cardmana.append(card)
               if "U" in mana:
                    colorCounts["Blue"] += 1
               if "R" in mana:
                    colorCounts["Red"] += 1
               if "G" in mana:
                    colorCounts["Green"] += 1
               if "B" in mana:
                    colorCounts["Black"] += 1
               if "W" in mana:
                    colorCounts["White"] += 1
               if mana == "":
                    colorCounts["Colorless"] +=1
               if mana.isdigit():
                    colorCounts["Colorless"] +=1

     #needs to be different from soi params due to older naming conventions
     soicardmana = []
     soicolorCounts = Counter()
     soirarity = []
     soitype = Counter()
     for card, type, rarity, mana in soidata:
          if "Enchantment" in type:
               soitype["Enchantment"] += 1
          if "Creature" in type:
               soitype["Creature"] += 1
          if "Artifact" in type:
               soitype["Artifact"] += 1
          if "Instant" in type:
               soitype["Instant"] += 1
          if "Sorcery" in type:
               soitype["Sorcery"] += 1
          if card not in cardmana:
               cardmana.append(card)
               if "U" in mana:
                    soicolorCounts["Blue"] += 1
               if "R" in mana:
                    soicolorCounts["Red"] += 1
               if "G" in mana:
                    soicolorCounts["Green"] += 1
               if "B" in mana:
                    soicolorCounts["Black"] += 1
               if "W" in mana:
                    soicolorCounts["White"] += 1
               if mana == "":
                    soicolorCounts["Colorless"] +=1
               if mana.isdigit():
                    soicolorCounts["Colorless"] +=1
          
     #http://matplotlib.org/examples/pylab_examples/subplots_demo.html
     f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
     f.suptitle("Comparision of Oldest Vs Newest Card Sets")
     ax1.set_title("Based on Card Type")
     ax1.scatter(range(len(catype)), catype.values(), label = "Alpha")
     ax1.set_xticks(range(len(catype)), catype.keys())
     
     ax1.scatter(range(len(soitype)), soitype.values(), color = "red", label = "SOI")
     ax1.set_xticks(range(len(soitype)), soitype.keys())
     ax1.legend(loc=2)
     labels = catype.keys()
     ax1.set_xlabel(labels)
     plt.setp(labels)
     
     ax2.set_title("Based on Card Color")
     ax2.scatter(range(len(colorCounts)), colorCounts.values(), label = "Alpha")
     ax2.set_xticks(range(len(colorCounts)), colorCounts.keys())
     
     ax2.scatter(range(len(soicolorCounts)), soicolorCounts.values(), color = "red", label = "SOI")
     ax2.set_xticks(range(len(soicolorCounts)), soicolorCounts.keys())
     ax2.legend(loc=2)
     labels = colorCounts.keys()
     ax2.set_xlabel(labels)
     plt.setp(labels)
     
     plt.show()
     
     
def main():
     cardsURL = "http://magiccards.info"
     getSetLinks(cardsURL)
     createCardCSV(cardsURL)
     decksURL = "http://sales.starcitygames.com//deckdatabase/deckshow.php?&t[C1]=3&start_date=02/21/2004&end_date=05/15/2016&start=1&finish=8&order_1=date%20desc&order_2=finish&start_num=25&start_num=0&limit=25"
     getDeckLinks(decksURL)
     getDataLists()
     pictures()
     getCardlistsData()
     cardWork()
     setCompWork()
main()