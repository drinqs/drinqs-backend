import requests
import bs4


def scrapeNamesWith(letter):
    response = requests.get('https://www.thecocktaildb.com/browse.php?b=%s'%letter)
    soup = bs4.BeautifulSoup(response.content,'html.parser')
    soup.select('.row')
    alleAs = soup.find_all("a")
    strliste = []
    for ele in alleAs[6:-34]:
        neuerstring = str(ele).split("<br/>")
        strliste.append(neuerstring[1][:-4])
    del strliste[0:141:2]
    del strliste[72::2]
    return strliste

def scrapeNames():
    alphabet = 'abcdefghijklmnopqrstvwyz12345679'
    nameList = []
    for letter in alphabet:
        namesLetters = scrapeNamesWith(letter)
        for drink in namesLetters:
            nameList.append(drink)
    i = 0
    for name in nameList:
        if name == 'Americano</img>':
            liste = name.split('<')
            nameList[i] = liste[0]
        elif name == 'Butter Baby</a>':
            nameList[i] = name[:-4]
        i+=1
    return nameList



