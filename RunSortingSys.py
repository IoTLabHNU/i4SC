#!/usr/bin/pyinstaller3
from SortingSystem import sortingSys

try:
    SortingSys = sortingSys()    
    SortingSys.runFunc()
except Exception as l:
    print("User pressed c...")
