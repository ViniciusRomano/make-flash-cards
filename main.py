import urllib.request
from bs4 import BeautifulSoup
import os, datetime
import pymongo
from pymongo import MongoClient


def setup_mongo():
    # Mongo Connect
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.study_english
    words = db.words

def order_list(rows):
    return sorted(rows, key=len)

def create_file(all_phrases):
    today = datetime.datetime.today()
    timestamp = str(today.timestamp()).split('.')[0]
    file = open(timestamp+".txt", "w")
    for x in all_phrases:
        file.write(x+'\n')
    file.close() #This close() is important
    print('Arquivo criado! - '+timestamp+'.txt')

def make_list_linguee(word):    
    url="https://www.linguee.com.br/portugues-ingles/search?source=auto&query="+ word.replace(' ','+')
    request=urllib.request.Request(url,None,HEADERS) #The assembled request
    response = urllib.request.urlopen(request)    
    soup = BeautifulSoup(response, 'html.parser')    
    mydivs = soup.findAll("div", {"class": "example"})    
    all_rows = []
    for x in mydivs:                      
        all_rows.append(x.findAll("span", {"class": "tag_s"})[0].get_text() +';' + x.findAll("span", {"class": "tag_t"})[0].get_text())
    return all_rows

def make_list_inverso(word):
    url="https://context.reverso.net/traducao/ingles-portugues/"+ word.replace(' ','+')
    request=urllib.request.Request(url,None,HEADERS) #The assembled request
    response = urllib.request.urlopen(request)
    response = response.read().decode('utf-8')
    soup = BeautifulSoup(response, 'html.parser')
    mydivs = soup.findAll("div", {"class": "example"})
    all_rows = []
    for x in mydivs:
        for counter,y in enumerate(x.findAll("span", {"class": "text"})):            
            _text = y.get_text().replace('    ','').replace('\n  ','').replace('\n','')            
            if(counter):
                text+= ';' + _text
                all_rows.append(text)            
            else:            
                text = _text
    return order_list(all_rows)[slice(0,10)]

def setup_mongo():
    # Mongo Connect
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.study_english
    return db.words

if __name__ == "__main__":
    
    # constants
    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    HEADERS={'User-Agent':USER_AGENT} 

    words = setup_mongo()
    os.system('clear')
    
    # Global Array
    selecteds_phrases = []
    
    while(True):
        print(str(len(selecteds_phrases)) + ' frases cadastradas.')
        word = ''
        
        # get word
        while(not len(word)):
            word = input('Digite uma palavra para o scraping (0 para sair,1 para inserir manualmente):\n')
        
        # verify if exists in mongodb
        check_work = words.count_documents({"word":word})

        # exit
        if(word == "0"):
            break 

        # manual input
        if(word == "1"):
            phrase = input('Digite a frase já no formato do anki:\n')
            selecteds_phrases.append(phrase)
            os.system('clear')

        # search word            
        elif(not check_work):        
            _all_rows = make_list_linguee(word)
            _all_rows += make_list_inverso(word)
            for counter,y in enumerate(_all_rows,1):
                print(str(counter) + ' - ' + y.replace(';', ' | ') + '\n')
            selecteds = input('Quais as frases escolhidas (separadas por vírgulas, -1 não inserir nada):\n')
            os.system('clear')
            _selecteds =  selecteds.split(',')
            if(_selecteds[0] != '-1'):
                for x in _selecteds:
                    selecteds_phrases.append(_all_rows[int(x)-1])
                words.insert_one({'word':word,'phrases':selecteds_phrases})
                  
        else:
            os.system('clear')
            print("Palavra já foi inserida no anki!")

    #create file        
    create_file(selecteds_phrases)






























