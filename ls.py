""" Autor: Tomasz Zdziech
    Backup Checker Project
"""

from sys import path
from tkinter import * # GUI
import FileList as fl #moja class
from tkinter import ttk #GUI
import glob
import tomli #obsluga plikow .toml
import os
import shutil
from datetime import datetime, date
import time
import sv_ttk #sun valey tkinter theme
import subprocess #podproces do polaczenia VPN

""" 
Format raportów:
Veeam B&R
Data	Wykonujący 	Status	Oryginalny rozmiar maszyny [TB]	
Data ostatniego pełnego backupu 	Rozmiar backupu [GB]	
Data ostatniego wykonanego backupu	Wolne miejsce w repozytorium [GB]	Uwagi

SQL
Data	Wykonujący kontrolę	Status	Rozmiar pliku BAK	Data ostatniego backupu 	
Wolne miejsce w repozytorium 	Uwagi


"""


if __name__ == '__main__':

#my global d cons.
    sqlExtension = ".bak"
    veeamExtension = ".vrb" # reverse incremental
    veeamFullExtension = ".vbk" #pelny
    veeamIncExtension = ".vib" # incremental
    openVpnPath = "C:\\Program Files\\OpenVPN\\bin\\openvpn.exe" #sciezka do pliku openvpn.exe
    

    main_list = fl.FileList("") #jesli folder sieciowy to podwoje backslashe \\\\Desktop-sj7tn1k\\wii\\
    

    mainWindow = Tk()
    vpnCheckButtonValue = IntVar() # VPN check button value
    sendEmailButtonValue = IntVar()
    writeLogButtonValue = IntVar()

    sv_ttk.set_theme("dark")  # Set light theme

    """
        kroki: (ju po wczytaniu pliku konfiguracyjnego)
        - odczytuje katalogi
        iF SQL
            w kazdym katalogu:
            ostatni plik na jego podstawie wyplówa tekst do wklejenia
            jesli plki starszy niz dwa dni WARNING!!!

            !!!!! co jesli sa w jednym folderze???????? czy brak dla Express???

        ELIF VEEAM
            w kazdym katalogu:
            1. wyszukuje ostatni backup
            2. wyszukuje ostatni pelny backup
            zaleznie od tego ktory jest najmlodszy generujemy linie do wklejenia
            jesli plki starszy niz dwa dni WARNING!!!
        
        """
    ## analiza logu polaczenia VPN zwraca True jesi wykrje odpowiedni tekst
    def analyze_vpn_log(file):
        desiredString = "Initialization Sequence Completed"
        unnecessaryString = "AUTH: Received control message: AUTH_FAILED"
        no_config_file_string = "Error opening configuration file:"
        no_credentials_file = "WARNING: cannot stat file"
        unknownError = "Unknown Error"
        for line in file:
            #print(line)            
            if desiredString in line:
                print("Znaleziono potwierdzenie polaczenia:", line)
                return True
            elif unnecessaryString in line:
                print("znaleziono: blad audentykacji:", line)
                return False
            elif no_config_file_string in line:
                print("Nie znaleziono pliku konfiguracyjnego VPN:", line)
                return False
            elif no_credentials_file in line:
                print("Nie znaleziono pliku z danymi logowania VPN:", line)
                return False
            elif unknownError in line:
                print("")
            


        return False

    def turnVpn():
        if vpnCheckButtonValue.get(): print("VPN enabled, status: ", vpnCheckButtonValue.get())
        else: print("VPN disabled, status: ", vpnCheckButtonValue.get())
    
    def sendEmail():
        if sendEmailButtonValue.get(): print("Sending email enabled, status: ", sendEmailButtonValue.get())
        else: print("Sending email disabled, status: ", sendEmailButtonValue.get())

    def writeLog():
        if writeLogButtonValue.get(): print("Writing log enabled, status: ", writeLogButtonValue.get())
        else: print("Writing log, status: ", writeLogButtonValue.get())


    def print_to_maintext(mstring: str, nl=False):
        mainText.insert(END, mstring)
        if nl: mainText.insert(END, "\n")


    def check_backup_age(date):
        zmienna = datetime.fromtimestamp(float(date)) #zamienie numpy_str na float a potem na datetime zeby bylo mozna porownac daty
        timer = datetime.now() - zmienna
        if timer.days > 7:
            return f"UWAGA!!!!!! Ostatni backup sprzed ponad : {str(timer.days)} dni."
        elif timer.days > 2:
            return f"Ostatni backup sprzed ponad: {str(timer.days)} dni"
        else:
            return ""


    def get_free_space_string(path: str):
        total, used, free = shutil.disk_usage(path)
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if total < 1024.0:
                break
            free /= 1024.0
            total /= 1024.0
            unit = x
        return free, total, x 
        #moze by tak zwroci jeszcze procent albo ostrzegac gdy miejsce jest mniejsze niz backup???


    #zwraca liste foderow w folderze nadrzednym
    def get_directories(path: str) -> list[str]:
        direList = []
        p=os.listdir(path)
        for i in p:
            if os.path.isdir(path+i):                
                direList.append(path+i+"\\")
        return direList

    #przeszukanie folderu podrzednego
    def sub_folder_execute_sql(path: str) -> None:

        fileList = fl.FileList(path)
        error_message = ""
        
        
        # Data	
        day = date.today()
        print_to_maintext(f"%s	" % day.strftime("%d.%m.%Y"))
        #Wykonujący kontrolę	
        print_to_maintext("Tomasz Zdziech	")
        #Status	
        print_to_maintext("ok	")
        #Rozmiar pliku BAK (nazwa)	oraz Data ostatniego backupu
        file_info = fileList.find_newest(sqlExtension)            
        if file_info :
            file_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file_info['date'])))
            print_to_maintext(f"{file_info['size']} (\'{file_info['file']}\')	{file_day}	")

            error_message += fileList.count_number(sqlExtension)
            error_message += check_backup_age(file_info["date"])    
        else: error_message = f"brak plików w folderze {path}."
                
                
        #Wolne miejsce w repozytorium 
        free, total, unit = get_free_space_string(path)
        print_to_maintext(f"{free:3.2f} {unit} / {total:3.2f} {unit} 	")
        if free < total/20:
            error_message += "Na dysku zostało mniej niż 5% miejsca"
                    
            
        #Uwagi
        print_to_maintext(f"{error_message}", True)

        """
            Potencjalnie mozna tu sprawdzac:
            - czy nie ma miejsca malo (porownujac do rozmiaru pliku backupu)
            - czy backup nei jest starszy niz ILEŚ dni
            - czy wogole znaleziono PLIKI!!!

        """
    def sub_folder_execute_veeam(path: str) -> None:        
        fileList = fl.FileList(path)
        error_message = ""
              	
        day = date.today()
        print_to_maintext("%s 	" % day.strftime("%d.%m.%Y"))
            
        # Wykonujący 	
        print_to_maintext("Tomasz Zdziech	")
            
        # Status	
        print_to_maintext("ok	")
            
        # Oryginalny rozmiar maszyny [TB]
        print_to_maintext("??? GB	")
            
        # Data ostatniego pełnego backupu 	+ Rozmiar backupu [GB]
        file_info = fileList.find_newest(veeamFullExtension)
        if file_info: 
            file_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file_info['date'])))
            print_to_maintext(f"{file_day}	{file_info['size']} 	")            
            	
        # Data ostatniego wykonanego backupu	
        file2_info = fileList.find_newest(veeamExtension)
        if file2_info: file2_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file2_info['date'])))
        else: 
            file2_info = fileList.find_newest(veeamIncExtension)
            if file2_info: file2_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file2_info['date'])))

        if not file_info and not file2_info: #gdy nie ma zadnego z rozszezen
            print_to_maintext("BRAK PLIKOW BACKUPU VEEAM W FOLDERZE", True )
            error_message += "BRAK PLIKOW BACKUPU VEEAM, "
        elif file_info and file2_info: #gdy sa pliki z oboma rozszezeniami
            #porownywanie
            if file_info["date"] > file2_info["date"]:
                print_to_maintext( f"{file_day} ( \'{file_info['file']}\'[{file_info['size']}] )	")
                error_message += check_backup_age(file_info["date"])
            elif file_info["date"] < file2_info["date"]:
                print_to_maintext( f"{file2_day} (\'{file2_info['file']}\'[{file2_info['size']}])	")
                error_message += check_backup_age(file2_info["date"])
            else:
                pass
        elif file_info: # gdy jest z rozszezeniem plenym
            print_to_maintext( f"{file_day} ( \'{file_info['file']}\'[{file_info['size']}])	")
            error_message += "Brak plików przyrostowych, "
            error_message += check_backup_age(file_info["date"])
        elif file2_info: #gdy jest z rozszezeniem przyrostowym
            print_to_maintext( f"{file2_day} (\'{file2_info['file']}\'[{file2_info['size']}])	")
            error_message += "Brak plików z backupem pełnym, "
            error_message += check_backup_age(file2_info["date"])
            
        # Wolne miejsce w repozytorium [GB]	
        free, total, unit = get_free_space_string(path)
        print_to_maintext(f"{free:3.2f} % {unit} / {total:3.2f} {unit} 	")
        if free < total/20:
            error_message += "Na dysku zostało mniej niż 5% miejsca"

         # Uwagi
        print_to_maintext(error_message, True)
        
   

    #odpalamy sie w folderze podanym w TOML
    def main_folder_execute(toml):      
        
        if toml['sql'] == "yes":
            print_to_maintext("****************************************************", True)
            print_to_maintext(f"Szukamy backupow SQL {toml['spath']}", True)
            print_to_maintext(f"Klient {toml['company']}", True)
            print_to_maintext("Data	Wykonujący kontrolę	Status	Rozmiar pliku BAK	Data ostatniego backupu 	Wolne miejsce w repozytorium 	Uwagi", True)
            direList = get_directories(toml["spath"])
            for i in direList:
                sub_folder_execute_sql(i)

        if toml['veeam'] == "yes":
            print_to_maintext("****************************************************", True)
            print_to_maintext("Szukamy backupow VEEAM " + toml['vpath'], True)
            print_to_maintext(f"Klient {toml['company']}", True)
            print_to_maintext("Data	Wykonujący 	Status	Oryginalny rozmiar maszyny [TB]	Data ostatniego pełnego backupu 	Rozmiar backupu [GB]	Data ostatniego wykonanego backupu	Wolne miejsce w repozytorium [GB]	Uwagi", True)
            direList = get_directories(toml["vpath"])
            for i in direList:
                print_to_maintext("Folder VEEAM: " + i, True)
                sub_folder_execute_veeam(i)
            if 'vpath2' in toml:
                print_to_maintext("****************************************************", True)
                print_to_maintext("Szukamy backupow VEEAM " + toml['vpath2'], True)
                direList = get_directories(toml["vpath2"])
                for i in direList:
                    print_to_maintext("Folder VEEAM: " + i, True)
                    sub_folder_execute_veeam(i)


        #print_to_maintext(dirList)



    def start_button():
        tomlFileName = fileListComboBOx.get() #pobiera z widgetu wybrana wartosc

        mainText.delete("1.0", "end") #oczyszczenie okna
        
        #wgranie pliku .toml
        tomlFileOpen = open(tomlFileName, mode="rb")
        toml = tomli.load(tomlFileOpen)
        tomlFileOpen.close()

        
        #odpalamy VPN
        if vpnCheckButtonValue.get() and 'short_name' in toml:
            #na czas laczenia VPN wylaczyc przycisk START
            startButton["state"] = "disabled" 
            
            #polaczenie VPN            
            vpnCompanyName = toml["short_name"] 
            vpnCompanyFile = f"vpn\{vpnCompanyName}.ovpn"
            vpnCompanyCred = f"vpn\{vpnCompanyName}.txt"
            command = [openVpnPath, "--config", vpnCompanyFile, "--auth-user-pass", vpnCompanyCred]
            with open('vpnlog\output.txt', 'w') as file: proc = subprocess.Popen(command, stdout=file)

            
            #sprawdzamy czy sie zakonczyl pomyslnie                        
            print("przed")
            vpn_state = False
            vpn_connection_trys = 0
            while not vpn_state:
                #print("petla")
                time.sleep(5)
                
                file = open('vpnlog\output.txt', 'r') #log z polaczenia VPN
                # if log == ok: vpnState = True
                if analyze_vpn_log(file): 
                    print("POLACZONO!!!!")
                    vpn_state = True
                else: vpn_connection_trys += 1            

                if vpn_connection_trys > 3:
                    print("nie udalo sie odczytac z loga VPN stanu polaczenia po 3 probach (3 x 10s), spadam")    
                    vpn_state = FALSE         
                    break
                        
            print("po")
        else: print("W pliku toml brak danych do polaczenie VPN lub nie wybrano polaczenia VPN w GUI!")
            
        
        # jesli bylo wybrane polaczenie VPN a nie udalo sie polaczyc to powinno zostac ominiete
        if vpnCheckButtonValue.get() and vpn_state:
            main_folder_execute(toml)
        elif not vpnCheckButtonValue.get(): #nie wybrano przycisku
            main_folder_execute(toml)
        else:
            print("Wyszukiwanie przerwane z powodu problemu z polaczeniem VPN / lub inny warunek bledny")

        #zamykamy VPN
        if vpnCheckButtonValue.get() and 'short_name' in toml:        
            #wlaczyc przycisk START
            startButton["state"] = "active" 
            #ubic polaczenie VPN
            proc.terminate()
            print("Wylaczam")        
               
        #saving log file (if checked)       
        if writeLogButtonValue.get():            
            day = datetime.today()
            logfilepath = f"log\{toml['company']} %s.txt" %day.strftime(" %d.%m.%Y %H.%M.%S")
            logfile = open(logfilepath, mode="w")
            logfile.write(mainText.get("1.0", "end"))
            logfile.close()
            print("Zapisano log: ", logfilepath)
        else:
            print("Log nie zapisany z wyboru")

        #sending email (if checked)
        if sendEmailButtonValue.get():
            print("Wyslano email")
        else:
            print("Email nei wyslany z wyboru")

###############################################################################
############End of Functions definitions#######################################

    mainWindow.state('zoomed')
        
    mainWindow.title("Backup Checker - by Tomasz") 
    mainWindow.config(background="GREY") 
    icon = PhotoImage(file='icon.png')
    mainWindow.iconphoto(True, icon) 

    #elementy okna definicje
    fileListComboBOx = ttk.Combobox(mainWindow, values = glob.glob("config\*.toml"))    
    fileListComboBOx.set("Choose")
    startButton = ttk.Button(mainWindow, text="Start", command = start_button)
    mainText = Text(mainWindow, height = 300, width = 300, borderwidth=10)
    vpnCheckButton = ttk.Checkbutton(mainWindow, text="Connect to VPN?", variable = vpnCheckButtonValue, onvalue = 1, offvalue = 0, command = turnVpn)
    sendEmailButton = ttk.Checkbutton(mainWindow, text="Send result with Email?", variable = sendEmailButtonValue, onvalue = 1, offvalue = 0, command = sendEmail)
    writeLogButton = ttk.Checkbutton(mainWindow, text="Write result to log file?", variable = writeLogButtonValue, onvalue = 1, offvalue = 0, command = writeLog)

    #elemty okna inicjacja
    fileListComboBOx.place(relx=0 , rely=0, relwidth=0.5, anchor="nw")
    startButton.place(relx=0.5 , rely=0, relwidth=0.15, anchor="nw")
    vpnCheckButton.place(relx=0 , rely=0.04, relwidth=0.15, anchor="nw")
    sendEmailButton.place(relx=0 , rely=0.08, relwidth=0.15, anchor="nw")
    writeLogButton.place(relx=0 , rely=0.12, relwidth=0.15, anchor="nw")
    mainText.place(relx=0.15 , rely=0.04, relwidth=0.8, anchor="nw")
    
    

    mainWindow.mainloop()
  
  
