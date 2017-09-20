from bs4 import BeautifulSoup
from bs4.element import Comment
from multiprocessing.dummy import Pool
from langdetect import detect
import time
import requests
import io

"""
Description: Takes in a .txt file with a list of sites that are new line
delimited and do not have the "http://" prefix. It searches each site for visible text
and writes to scrapeData.txt -> "URL/tDATA" for each URL. If the URL does not work,
the URL is written to blacklistSites.txt.
"""

class LIWebScraper:
    def __init__(self, siteTextFile):
        self.sites = None
        self.outfile = None
        self.blacklistFile = None
        self.startTime = None
        self.logFile = None
        self.numBlackList = 0
        self.initSiteList(siteTextFile)
        self.setupSitesForRequests()

    def initSiteList(self, siteTextFile):
        infile = open(siteTextFile, "r")
        self.sites = infile.readlines()
        infile.close()

    def setupSitesForRequests(self):
        self.sites = ["http://" + site.replace("\n", "") for site in self.sites]

    def startMultiThreaded(self):
        try:
            self.construct()
            self.scrapeAllSitesMultiThreaded()
        finally:
            self.destruct()

    def construct(self):
        self.startTime = time.time()
        self.printStart()
        self.openFiles()

    def printStart(self):
        print("-" * 20 + " Scraper Started " + "-" * 20 + "\n")
        print("{:>20} | {:>10}".format("ProcessMessage", "Site"))
        print("-" * 60)

    def openFiles(self):
        self.outfile = open("Data\\scrapeData.txt", "w+")
        self.blacklistFile = open("Data\\blacklistSites.txt","w+")

    def scrapeAllSitesMultiThreaded(self):
        threads = Pool(20)
        threads.map(self.scrape,self.sites)
        threads.terminate()
        threads.join()

    def scrape(self, site):
        try:
            data = self.cleanTextForDataFile(self.textFromHTML(site))
            self.checkData(data)
            self.saveScrapeDataToFile(site, data)
        except AttributeError:
            self.handleError(site,"No Data")
        except requests.exceptions.ReadTimeout:
            self.handleError(site,"Timeout")
        except requests.exceptions.ConnectionError:
            self.handleError(site,"Failed Connection")
        except requests.exceptions.InvalidURL:
            self.handleError(site,"Bad URL")
        except:
            self.handleError(site,"Unexpected Error")

    def cleanTextForDataFile(self, text):
        return " ".join(text.split())

    def textFromHTML(self, site):
        soup = self.buildSoup(site)
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tagVisible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    def buildSoup(self, site):
        getResponse = self.getRequestSite(site)
        return BeautifulSoup(getResponse.content, 'html.parser')

    def getRequestSite(self, site):
        return requests.get(site, timeout=5)

    def tagVisible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def checkData(self,data):
        errorWordCount = 0
        if "Forbidden" in data:
            errorWordCount = errorWordCount + 1
        if "403" in data:
            errorWordCount = errorWordCount + 1
        if "404" in data:
            errorWordCount = errorWordCount + 1
        if errorWordCount > 1:
            raise requests.exceptions.InvalidURL

    def saveScrapeDataToFile(self, site, data):
        if data == "":
            raise AttributeError
        writeString = site + "\t" + data + "\n"
        print("{:>20} | {}".format("[Success]", site))
        self.outfile.write(writeString.encode('utf-8'))

    def handleError(self,site,message):
        self.printBadProcess(site,message)
        self.saveBlacklistSiteToFile(site)

    def printBadProcess(self,site,message):
        print("{:>20} | {}".format("[" + message + "]", site))

    def saveBlacklistSiteToFile(self, site):
        self.numBlackList = self.numBlackList + 1
        writeString = site + "\n"
        self.blacklistFile.write(writeString.encode('utf-8'))

    def destruct(self):
        self.closeFiles()
        self.printStop()

    def closeFiles(self):
        self.outfile.close()
        self.blacklistFile.close()

    def printStop(self):
        print("\n" + "-" * 20 + " Scraper Stopped " + "-" * 20 + "\n")
        self.printStats()

    def printStats(self):
        self.printStat("STAT","VALUE")
        print("")
        self.printStat("No. of Sites",len(self.sites))
        self.printStat("No. of Blacklisted Sites", self.numBlackList)
        self.printStat("Runtime",str(self.calculateRunTime())[:7]+ " seconds")
        self.printStat("Scrape(s)/Second",str(len(self.sites)/self.calculateRunTime())[:5] + " seconds")

    def printStat(self,statName,value):
        print("{:>25}: {}".format(statName,value))

    def calculateRunTime(self):
        return time.time() - self.startTime


"""
Description: Takes the results from the visible text scraper and identifies each site using the text
"""

class Identifier:
    def __init__(self):
        self.scrapeData = []
        self.languageDictionary = {}
        self.outfile = None
        self.initScrapeData()
        self.initLanguageDictionary()

    def initScrapeData(self):
        infile = io.open("Data\\scrapeData.txt","r",encoding="utf-8")
        self.setupData(infile.readlines())
        infile.close()

    def setupData(self, dataList):
        for data in dataList:
            splitData = data.split("\t")
            self.scrapeData.append((splitData[0],splitData[1]))

    def initLanguageDictionary(self):
        infile = io.open("Data\\languageDictionary.txt","r",encoding="utf-8")
        self.setupDictionary(infile.readlines())
        infile.close()

    def setupDictionary(self,languageList):
        for language in languageList:
            splitLanguage = language.split()
            self.languageDictionary[splitLanguage[0]] = splitLanguage[1]

    def start(self):
        try:
            self.printStart()
            self.openOutfile()
            self.identifyAll()
        finally:
            self.closeOutfile()
            self.printStop()

    def printStart(self):
        print("-" * 20 + " Identifier Started " + "-" * 20 + "\n")

    def openOutfile(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.outfile = io.open("Data\\Results\\sitesIdentified" + timestr + ".txt","w+",encoding="utf-8")

    def identifyAll(self):
        for dataTuple in self.scrapeData:
            self.identify(dataTuple)

    def identify(self,dataTuple):
        language = self.languageDictionary[detect(dataTuple[1])]
        print("{:>60}: {}".format(dataTuple[0],language))
        self.writeToOutfile(dataTuple[0][7:]+"\t"+language+"\n")

    def writeToOutfile(self, stringToWrite):
        self.outfile.write(stringToWrite)

    def closeOutfile(self):
        self.outfile.close()

    def printStop(self):
        print("\n" + "-" * 20 + " Identifier Stopped " + "-" * 20 + "\n")

if __name__ == "__main__":
    scraper = LIWebScraper("sites.txt")
    scraper.startMultiThreaded()
    id = Identifier()
    id.start()
