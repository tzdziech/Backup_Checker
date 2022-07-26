from os import path
from datetime import datetime
import glob
import numpy as np

    #konwersja rozmiaru na jak najwieksze jednostki
def convert_bytes(size):
    """ Convert bytes to KB, or MB or GB"""
    size = float(size)
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.2f %s" % (size, x)
        size /= 1024.0

#wyodrebnienie rozszezenia z nazwy pliku
def get_extension(file):
    file_details = path.splitext(file)
    return file_details[1]

def path_to_filename(path: str):
    #print("path_to_filename", path[path.rindex("\\")+1:] )
    return path[path.rindex("\\")+1:]


class FileList:
    """Lista plikow w katalogu wraz rozszezeniem, rozmiarem i czasem modyfikacji"""

    def __init__(self, directory):
        #pobranie danych do stworzenia list
        size = [] #lista z rozmiarami
        natural_size = []
        file_extension = [] #lista z rozszezeniami
        file_modification_time = []
        files = glob.glob(f"{directory}*.*")
        for file in files:    
            file_extension.append(get_extension(file)) 
            size.append(convert_bytes(path.getsize(file)))#pobiera rozmiar i conwertuje na najwieksze jednostki
            natural_size.append(path.getsize(file))
            file_modification_time.append(path.getmtime(file))

        #stworzenie tablicy z list
        #zadana list plikow:  0 - nazwa, 1- rozmiar zmienony, 2 - rozmiar naturalny, 3 - rozszezenie(z .), 4 - czas naturalny) 
        self.list = np.array([files, size, natural_size, file_extension, file_modification_time])
        if len(files) == 0:
            print("Brak plikow w katalogu lub katalog nie prawidłowy - zainicjowano pustą listę")

    def do_ls(self):
        for x in range(len(self.list[0])):
            print("File name:", self.list[0,x],"\t size:", self.list[1,x],"(", self.list[2,x], ") \textension:", self.list[3,x], "\t last modified:", self.list[4,x], "(", datetime.fromtimestamp(float(self.list[4,x])), ")")
        print("Znaleziono:", len(self.list[0]), "pliki")

    #zwraca numer pozycji najwiekszego pliku z listy o zadanym rozszezeniu
    def find_biggest(self, extension):
        if len(self.list[0]) == 0:
            #   print("Brak plikow w katalogu - nie mozna znalezc najwiekszego")
            return False

        last_biggest = self.list[2,0]
        number_biggest = False        
        for x in range(len(self.list[0])):
            if self.list[2,x] > last_biggest and self.list[3,x] == extension:
                last_biggest = self.list[2,x]
                number_biggest = x

        #   print("Najwiekszy plik to:", self.list[0,number_biggest], self.list[1,number_biggest])
        #   return "Najwiekszy plik to:", self.list[0,number_biggest], self.list[1,number_biggest]
        if number_biggest: return path_to_filename(self.list[0,number_biggest])
        else: return False

    #zwraca numer pozycji najnowszego pliku z listy o zadanym rozszezeniu
    def find_newest(self, extension):
        if len(self.list[0]) == 0:
            #   print("Brak plikow w katalogu - nie mozna znalezc najnowszego")
            return False

        last_newest = self.list[4,0]
        number_newest = False        
        for x in range(len(self.list[0])):
            if self.list[4,x] > last_newest and self.list[3,x] == extension:
                last_newest = self.list[4,x]
                number_newest = x

        #   print("Najnowszy plik to:", self.list[0,number_newest], self.list[1,number_newest])
        #   return "Najnowszy plik to:", self.list[0,number_newest], self.list[1,number_newest]
        if number_newest: return {'size': self.list[1,number_newest],'file': path_to_filename(self.list[0,number_newest]),'date': self.list[4,number_newest]}
        else: return False
        #   return self.list[0,number_newest]
        

    

if __name__ == '__main__':
    list = FileList("C:\\Users\\Agron\\Documents\\NAUKA\\PYTHON\\programy\\Backup_Checker\\")
    #print(list.list)
    list.do_ls()
    list.find_biggest(".py")
    list.find_newest(".py")

    #help(FileList)