from sys import path
from tkinter.tix import DirList
from pip import main
from tkinter import *
import FileList as fl
from tkinter import ttk
import glob
import tomli
import os
import shutil
from datetime import datetime, date
import time

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

    sqlExtension = ".bak"
    veeamExtension = ".vrb" # reverse incremental
    veeamFullExtension = ".vbk" #pelny
    veeamIncExtension = ".vib" # incremental

    main_list = fl.FileList("") #jesli folder sieciowy to podwoje backslashe \\\\Desktop-sj7tn1k\\wii\\
    #print(main_list.list)
    #main_list.do_ls()
    #main_list.find_biggest(".py")
    #main_list.find_newest(".py")

    mainWindow = Tk()

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
    def check_backup_age(date):
        #sprawdzamy czy backup nie jest starszy niz XXXXXX dni
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
        return "%3.2f" % free + x + " / " + "%3.2f" % total + x 
        #moze by tak zwroci jeszcze procent albo ostrzegac gdy miejsce jest mniejsze niz backup???


    #zwraca liste foderow w folderze nadrzednym
    def get_directories(path: str) -> list[str]:
        dirList = []
        p=os.listdir(path)
        for i in p:
            if os.path.isdir(path+i):                
                dirList.append(path+i+"\\")
        return dirList

    #przeszukanie folderu podrzednego
    def sub_folder_execute(path: str, btype: str) -> None:
        #print("-------",path,"-------------------")
        fileList = fl.FileList(path)
        error_message = ""
        #fileList.do_ls()
        if btype == "SQL":
            # Data	
            day = date.today()
            print(day.strftime("%d.%m.%Y"), end = ";")
            #Wykonujący kontrolę	
            print("Tomasz Zdziech", end = ";")
            #Status	
            print("ok", end = ";")
            #Rozmiar pliku BAK (nazwa)	oraz Data ostatniego backupu
            file_info = fileList.find_newest(sqlExtension)            
            if file_info :
                file_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file_info['date'])))
                print(file_info['size'],"(", file_info['file'],");", file_day, end = ";")

                error_message += check_backup_age(file_info["date"])    
                
                
            #Wolne miejsce w repozytorium 
            print(get_free_space_string(path),  end = ";")
            
            #Uwagi
            print(error_message)

            """
            Potencjalnie mozna tu sprawdzac:
            - czy nie ma miejsca malo (porownujac do rozmiaru pliku backupu)
            - czy backup nei jest starszy niz ILEŚ dni
            - czy wogole znaleziono PLIKI!!!

            """

        elif btype == "VEEAM":
            # Data	
            day = date.today()
            print(day.strftime("%d.%m.%Y"), end = ";")
            
            # Wykonujący 	
            print("Tomasz Zdziech", end = ";")
            
            # Status	
            print("ok", end = ";")
            
            # Oryginalny rozmiar maszyny [TB]
            print("??? GB", end = ";")
            
            # Data ostatniego pełnego backupu 	+ Rozmiar backupu [GB]
            file_info = fileList.find_newest(veeamFullExtension)
            if file_info: 
                file_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file_info['date'])))
                print(file_day, ";", file_info['size'],  end = ";")
                #print(file_day, file_info['size'],"(", file_info['file'],")	",  end = ";")
            	
            # Data ostatniego wykonanego backupu	
            file2_info = fileList.find_newest(veeamExtension)
            if file2_info: file2_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file2_info['date'])))
            else: 
                file2_info = fileList.find_newest(veeamIncExtension)
                if file2_info: file2_day = time.strftime("%d.%m.%Y %H:%M", time.localtime(float(file2_info['date'])))

            if not file_info and not file2_info: #gdy nie ma zadnego z rozszezen
                print("BRAK PLIKOW BACKUPU VEEAM W FOLDERZE",  end = ";" )
                error_message += "BRAK PLIKOW BACKUPU VEEAM, "
            elif file_info and file2_info: #gdy sa pliki z oboma rozszezeniami
                #porownywanie
                if file_info["date"] > file2_info["date"]:
                    print( file_day, "(", file_info['file'], "[", file_info['size'], "]", ")",  end = ";")
                    error_message += check_backup_age(file_info["date"])
                elif file_info["date"] < file2_info["date"]:
                    print( file2_day, "(", file2_info['file'], "[", file2_info['size'], "]", ")",  end = ";")
                    error_message += check_backup_age(file2_info["date"])
                else:
                    pass
            elif file_info: # gdy jest z rozszezeniem plenym
                print( file_day, "(", file_info['file'], "[", file_info['size'], "]", ")",  end = ";")
                error_message += "Brak plików przyrostowych, "
                error_message += check_backup_age(file_info["date"])
            elif file2_info: #gdy jest z rozszezeniem przyrostowym
                print( file2_day, "(", file2_info['file'], "[", file2_info['size'], "]", ")",  end = ";")
                error_message += "Brak plików z backupem pełnym, "
                error_message += check_backup_age(file2_info["date"])
            
            # Wolne miejsce w repozytorium [GB]	
            print(get_free_space_string(path), end = ";")

            # Uwagi
            print(error_message)
        
   

    #odpalamy sie w folderze podanym w TOML
    def main_folder_execute(toml):      
        
        if toml['sql'] == "yes":
            print("****************************************************")
            print("Szukamy backupow SQL ", toml['spath'])
            print("Klient", toml['company'])
            print("Data	Wykonujący kontrolę	Status	Rozmiar pliku BAK	Data ostatniego backupu 	Wolne miejsce w repozytorium 	Uwagi")
            dirList = get_directories(toml["spath"])
            for i in dirList:
                sub_folder_execute(i, "SQL")

        if toml['veeam'] == "yes":
            print("****************************************************")
            print("Szukamy backupow VEEAM ", toml['vpath'])
            dirList = get_directories(toml["vpath"])
            for i in dirList:
                print("Folder VEEAM: ", i)
                sub_folder_execute(i, "VEEAM")
            if toml['vpath2']:
                print("****************************************************")
                print("Szukamy backupow VEEAM ", toml['vpath2'])
                dirList = get_directories(toml["vpath2"])
                for i in dirList:
                    print("Folder VEEAM: ", i)
                    sub_folder_execute(i, "VEEAM")


        #print(dirList)



    def start_button():
        temp_file = fileListComboBOx.get() #pobiera z widgetu wybrana wartosc
        
        #wgranie pliku .toml
        fp = open(temp_file, mode="rb")
        toml = tomli.load(fp)

        main_folder_execute(toml)
        
        
        #print(toml)
        mainText.delete("1.0", "end")
        mainText.insert(END, toml ) #wypluwa do pola tekstowego
        mainText.insert(END, '\n')
        mainText.insert(END, toml['company']+'\n')
        mainText.insert(END, toml['vpath']+'\n')
        mainText.insert(END, toml['spath']+'\n')


    #inicjacja glownego okna
    mainWindow.geometry("420x420")
    mainWindow.title("Backup Checker - by Tomasz") 
    mainWindow.config(background="GREY") 
    icon = PhotoImage(file='icon.png')
    mainWindow.iconphoto(True, icon) 

    #elementy okna definicje
    fileListComboBOx = ttk.Combobox(mainWindow, values = glob.glob("config\*.*"))    
    fileListComboBOx.set("Wybierz")
    startButton = Button(mainWindow, text="Start", command = start_button)
    mainText = Text(mainWindow, height = 300, width = 300)

    #elemty okna inicjacja
    fileListComboBOx.pack()
    startButton.pack()
    mainText.pack()

   



    #text_field.insert(END, main_list.find_biggest(".py") )
    #text_field.insert(END, main_list.find_newest(".py") )

   

    mainWindow.mainloop()
  
  
