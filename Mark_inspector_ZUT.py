from bs4 import BeautifulSoup
from getpass import getpass
from datetime import datetime
import requests
import time
from pydub import AudioSegment
from pydub.playback import play
import os


LOGIN_URL="https://edziekanat.zut.edu.pl/WU/Logowanie2.aspx"
DATA_URL="https://edziekanat.zut.edu.pl/WU/OcenyP.aspx"
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
user = "student"
clear = lambda: os.system('cls')


def check_changes(data):
    old_data = []
    with open('oceny.txt') as f:
        for line in f:
            old_data.append(line.strip().split(';'))
    f.close
    
    for i in range(len(data)):
        for j in range(2,len(data[0])-1):
            if(old_data[i][j] != data[i][j]):
                if(data[i][j] == '2'):
                    try:
                        play(AudioSegment.from_mp3("audio/2.mp3"))
                    except:
                        print('No audio file. Place your audio files under audio/5.mp3, audio/2.mp3, audio/3+.mp3 in .exe directory')

                elif(data[i][j] == '5'):
                    try:
                        play(AudioSegment.from_mp3("audio/5.mp3"))
                    except:
                        print('No audio file. Place your audio files under audio/5.mp3, audio/2.mp3, audio/3+.mp3 in .exe directory')

                else:
                    try:
                        play(AudioSegment.from_mp3("audio/3+.mp3"))
                    except:
                        print('No audio file. Place your audio files under audio/5.mp3, audio/2.mp3, audio/3+.mp3 in .exe directory')

                print(f'{data[i][0]} ocena: {data[i][j]}')
                input('Press enter to continue...')
                clear()

                return True

    return False


def saveto_file(data):
    with open('oceny.txt', "w", encoding='utf-8') as f:
        for li in data:
            for ele in li:
                f.write(ele + ';')
            f.write('\n')
        f.close()


def get_payload(session, username, password):
    resp=session.get(LOGIN_URL)
    soup=BeautifulSoup(resp.content, 'html.parser')

    # Getting data needed for POST payload
    tokens = dict()
    try:
        tokens["EVENTTARGET"] = soup.find(id="__EVENTTARGET")['value']
        tokens["EVENTARGUMENT"] = soup.find(id="__EVENTARGUMENT")['value']
        tokens["VIEWSTATE"] = soup.find(id="__VIEWSTATE")['value']
        tokens["VIEWSTATEGENERATOR"] = soup.find(id="__VIEWSTATEGENERATOR")['value']
    except:
        print(f'Could not find necessary tokens in login page.\nMaybe the site has changed?')
        exit()

    payload={
        "__EVENTTARGET":tokens["EVENTTARGET"],
        "__EVENTARGUMENT":tokens["EVENTARGUMENT"],
        "__VIEWSTATE":tokens["VIEWSTATE"],
        "__VIEWSTATEGENERATOR":tokens["VIEWSTATEGENERATOR"],
        "ctl00_ctl00_TopMenuPlaceHolder_TopMenuContentPlaceHolder_MenuTop3_menuTop3_ClientState":"",
        "ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$txtIdent":username,
        "ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$txtHaslo":password,
        "ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$butLoguj":"Zaloguj",
        "ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$rbKto":user
    }

    return payload


def grab_data(session):
    page = session.get(DATA_URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    data_temp = []
    data = []

    table = soup.find(id="ctl00_ctl00_ContentPlaceHolder_RightContentPlaceHolder_dgDane")
    if(table is None):
        print(f'Could not find data.\nCheck your credentials.')
        exit()
    else:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele for ele in cols]
            data_temp.append([ele for ele in cols if ele])

        data_temp.pop(0)

        for przedm in data_temp:
            li = list()

            przedm = przedm[:2] + przedm[5:-3]

            for i in range(len(przedm)):
                li.append(przedm[i].find(text=True).replace(u'\xa0', u'Brak_oceny')) # The "whitespace" eraser

            data.append(li)
        
        return data


if __name__ == '__main__':
    username = input('Username: ')
    password = getpass(prompt='Password: ')

    while(True):
        try:
            ss = int(input(f'Refresh rate in s: '))
            if(ss < 10 and ss > 600):
                print("Try value between 10s and 10mins")
                continue
            break
        except:
            print("Not a valid input")

    session=requests.Session()
    session.headers.update(headers)

    payload = get_payload(session, username, password)
    resp = session.post(LOGIN_URL, data=payload)

    data = grab_data(session)
    saveto_file(data)

    while(True):
        clear()
        now = datetime.now()
        print(f'Last refresh: {now.strftime("%H:%M:%S")}')
        time.sleep(ss)

        data = grab_data(session)
        if(check_changes(data)):
            saveto_file(data)

        

        
        


    




