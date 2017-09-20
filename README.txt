LANGUAGE IDENTIFIER

This program will take in a txt file called sites.txt in the working directory and scrape all of the visible text from each site. It will then use the text scraped to identify each site's language.

SETUP

1. You are going to need python 2.7 installed on your machine. You can download it here: https://www.python.org/downloads/

2. After installing python open up cmd as admin and enter the following commands (The directory that I downloaded python to is "C:\Python27", it may be different for you. Just make sure to add "\Scripts\pip.exe" to your directory path):
 "C:\Python27\Scripts\pip.exe install beautifulsoup4"
 "C:\Python27\Scripts\pip.exe install requests"
 "C:\Python27\Scripts\pip.exe install langdetect"

RUNNING THE LANGUAGE IDENTIFIER

1. The sites that you want to scrape must be in a .txt file in the same folder as LanguageIdentifier.py and in the format:

cool.com
helloworld.com
python.com

2. run the python script and when it is finished, the resulting data will be saved in "Data\Results\sitesIdentifiedDATE-TIME.txt". 