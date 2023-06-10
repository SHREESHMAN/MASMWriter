from os import chdir,listdir,mkdir
from datetime import datetime as dt
from time import sleep
from pathlib import PurePath as pp
import json

#GLOBALS AND CONSTANTS
BACKUPFILE="masmbackups.json"
PROGRAM="mpro.asm"
DIRECTORY=pp("C:/8086") #use / or \\
LL=50
L=15
#Edited Code
EDITED = False
c,data,procs,macs,code = [],[],[],[],[]

# The below code is defining a dictionary named "defaults" which contains information about various
# procedures and macros in assembly language. Each key in the dictionary represents a procedure or
# macro and contains information about its implementation, purpose, and any register modifications it
# makes. Some of the procedures/macros defined include displaying a hex value, taking user input and
# converting it to hex, displaying decimal equivalent of a value, printing a string, and displaying an
# immediate character.
defaults = {
    "DISPAL":{
        "procs":["""DISPAL PROC\n\tPUSH DX\n\tPUSH CX\n\tPUSH AX\n\t\tMOV CH,AL
    \t\tMOV CL,4\n\t\tMOV DL,CH\n\t\tROL DL,CL\n\t\tAND DL,0FH\n\t\tCMP DL,0AH\n\t\tJC PP
    \t\tADD DL,7\n\t PP:ADD DL,30H\n\t\tMOV AH,2\n\t\tINT 21H\n\n\t\tMOV DL,CH\n\t\tAND DL,0FH
    \t\tCMP DL,0AH\n\t\tJC GG\n\t\tADD DL,7\n\t GG:ADD DL,30H\n\t\tMOV AH,2\n\t\tINT 21H\n\tPOP AX
    \tPOP CX\n\tPOP DX\n\tRET\nDISPAL ENDP"""],"info":"Displays Hex Value stored in AL\n[No register modification]"
    },
    "INP":{
        "procs":["""INP PROC\n\t   PUSH BX\n\tPUSH CX\n\t   MOV AH,01H\n\t   INT 21H\t\t ;GET INPUT ASCII
    \t   CMP AL,3AH\n\t   JC G\n\t   SUB AL,7H\n\t G:SUB AL,30H\t  ;CONVERT ASCII AL TO HEX\n\t   MOV CL,04H
    \t   ROL AL,CL\n\t   MOV BL,AL\t   ;UPPER NIBBLE IN BL\n\t   MOV AH,01H\n\t   INT 21H\n\t   CMP AL,3AH
    \t   JC H\n\t   SUB AL,7H\t   ;NEW LOWER NIBBLE HEX IN AL\n\t H:SUB AL,30H
    \t   OR AL,BL\t\t;COMBINE NIBBLES TO MAKE A BYTE IN AL\n\n\t   POP CX\n\tPOP BX\n\t   RET\nINP ENDP"""],
        "info":"Takes 1 byte input from user and converts into hex\nOnly 0-F will work\n[AL modification - Result]"
    },
    "DISPDEC":{
        "procs":["""DISPDEC PROC\nPUSH AX\nPUSH BX\nPUSH CX\nPUSH DX\n\tMOV CL,0
    \tLEA SI,_YY\n\n    BCK:MOV DX,0    \n\tMOV BX,0AH    \n\tDIV BX\n\t\t\t   ;R-DX\t  Q-AX\n\tMOV CH,DL\t 
    \tADD CH,30H    \n\tMOV [SI],CH\t;[SI] <- CH <- DL <- R\n\t\n\tINC SI\n\tINC CL
    \tCMP AX,0\t   ;AX <- Q    \tJNZ BCK\n\n     PNT:\n\tDEC SI\n\tMOV DL,[SI]\n\tMOV AH,02H
    \tINT 21H\n\tDEC CL    \n\tJNZ PNT\nPOP DX\nPOP CX\nPOP BX\nPOP AX  \nRET\nDISPDEC ENDP"""],
        "data":["_YY DB DUP 5 (0)"],
        "info":"Displays Decimal Equivalent of Value in AX\n[No register modification]\n[_YY Array wil be added to data segment]"},
    "PRINT":{
        "macs":['PRINT MACRO MSG\nPUSH AX\nPUSH DX\n\tMOV AH,09H\n\tLEA DX,MSG\t;msg to be displayed\n\tINT 21H\t\nPOP DX\nPOP AX\nENDM'],
        "info":"Prints a string from data segment\nTakes Label as argument\n[No register modification]"
    },
    "CHSHOW":{
        "macs":['CHSHOW MACRO CH\nPUSH AX\nPUSH DX\n\tMOV AH,02H\n\t MOV DL,CH\t;char to be displayed\n\tINT 21H\t\nPOP DX\nPOP AX\nENDM'],
        "info":"Prints an immidiate character\nTakes character (eg:'>') as argument\n[No register modification]"
    },
    "String Display Interrupt":{
        "code":['MOV AH,02H','INT 21H'],
        "info":"Prints an immidiate character\nTakes character (eg:'>') from DL\n[No register modification]"
    }
}


# The below code is checking if a directory named "8086" exists in the "C:/" directory. If it does not
# exist, it creates the directory. Then, it changes the current working directory to "C:/8086".
# Finally, it checks if a file named "collection.json" exists in the current working directory. If it
# does, it reads the contents of the file and loads it into the defaults dictionary in the global
# namespace.
chdir(str(DIRECTORY).replace(str(DIRECTORY.name),''))
if str(DIRECTORY.name) not in listdir():
    print(f"-<"*LL+'\n\t'+f"'{str(DIRECTORY)}' not found New directory being created!")
    mkdir(str(DIRECTORY.name))
    sleep(1)
chdir(str(DIRECTORY))
if 'collection.json' in listdir():
    with open('collection.json') as f:
        globals().update({"defaults":json.load(f)})

#    This function checks for the existence of a backup file and allows the user to choose whether to
#    continue editing a previous save or start a new project.
#    :param x: The parameter x is an optional integer parameter with a default value of 0. It is used to
#    determine whether to create a new backup file or not. If x is 1, a new backup file will be created
#    even if one already exists, defaults to 0 (optional)
def checkbackup(x=0):
    global BACKUPFILE,EDITED,c
    if (BACKUPFILE not in listdir()) or (x==1):
        print(">-"*LL+'\n\t'+f"Backup file not detected, creating new!\n"+"-<"*LL+"\n")
        sleep(1)
        with open(BACKUPFILE,"w") as newbkup:
            json.dump({},newbkup)
    else:
        with open(BACKUPFILE,"r") as backup:
            b=json.load(backup)
        if b[max(b)]["EDITED"]:
            print(f"\nLatest Custom Save at {max(b)} detected!")
        else:
            print(f"\nLatest Save at {max(b)} detected!")

        choice = input("""\nWould you like to continue edititng a save or start a new project?
| 0 - Use Latest Save
| 1 - Use an older Save
| Enter - Create a new program\n""")
        while choice not in ['0','1','']:
            choice=input("Invalid!\nEnter Selection: ")    

        if choice=="0":
            if b[max(b)]["EDITED"]:               
                print(f"\nLoading Custom Save at {max(b)}")
                global EDITED
                EDITED = True
                c = b[max(b)]["c"].splitlines()
                sleep(1)
            else:
                print(f"\nLoading Save at {max(b)}")
                globals().update(b[max(b)])
                sleep(1)
        elif choice=="1":
            print()
            lis=list(b.keys())
            for i in range(len(lis)):
                print(f"{i+1}\t|{lis[i]}")
            l=linsel(2,"Save",lis,"Load")
            save = b[lis[l]]
            if save["EDITED"]:
                print(f"\nLoading Custom Save at {lis[l]}")
                EDITED = True
                c = save["c"].splitlines()
                sleep(1)
            else:
                print(f"\nLoading Save at {lis[l]}")
                globals().update(save)
                sleep(1)
        else:
            pass

def has(dmcp):return len(dmcp)>0

def getMacros(x=1):
    """
    The function returns a string containing assembly code macros if they exist.
    
    :param x: The parameter x is an optional integer parameter with a default value of 1. It is used to
    determine whether to include additional assembly code in the returned string. If x is equal to 1,
    the additional code will be included. If x is not equal to 1, the additional code will, defaults to
    1 (optional)
    :return: The function `getMacros` returns a string `s` that contains assembly code for defining
    macros. The string includes the `.MODEL SMALL` and `.STACK 100H` directives if the optional argument
    `x` is not provided or is equal to 1. If the list `macs` contains any macros, they are included in
    the string with a header that says "MACROS".
    """
    if x==1:s = ".MODEL SMALL\n.STACK 100H\n"
    else: s=''
    if has(macs):
        s += ';' + '=' * L + "MACROS" + '=' * L + '\n'
        for i in range(len(macs)):
            s += f"\n{macs[i]}\n"
    return s
def getData(x=1):
    """
    This is a Python function that returns a string containing code and variables, with an optional
    parameter to exclude the code section.
    
    :param x: An optional parameter with a default value of 1. It is used to determine whether to
    include the variables section in the output or not. If x is 0, only the variables section will be
    returned. If x is 1 or any other value, both the variables and code sections will be, defaults to 1
    (optional)
    :return: The function `getData()` is returning a string that contains assembly code. The code
    includes a section for declaring variables (if there are any), and a section for the main code. The
    main code starts with the label "START" and includes instructions for setting up the data segment
    and the data register. The code may also include additional instructions depending on the specific
    implementation.
    """
    m='\n\n;'+'='*L+"CODE"+'='*L+'\n'
    if has(data):
        s = '\n;'+'='*L+"VARIABLES"+'='*L+'\n'+".DATA"
        for i in range(len(data)):
            s += f"\n\t{data[i]}"
        if x==0:return s + '\n'
        return s + m+ "\n.CODE\nSTART:\n\tMOV AX,@DATA\n\tMOV DS,AX\n"
    else:
        return m+"\n.CODE\nSTART:\n"
def getCode(x=1):
    """
    This is a Python function that returns a string containing assembly code, with an optional parameter
    to include an exit code.
    
    :param x: The parameter x is an optional integer parameter with a default value of 1, defaults to 1
    (optional)
    :return: The function getCode is returning a string that contains assembly code. If the parameter x
    is equal to 0, it returns only the code without the "MOV AH,4CH\n\tINT 21H\n" instruction. If x is
    not equal to 0, it returns the code with the "MOV AH,4CH\n\tINT 21H\n" instruction at the end.
    """
    s = str()
    if has(code):
        for i in range(len(code)):
            s += f"\n\t{code[i]}"
    if x==0:return s
    return s + "\n\n\tMOV AH,4CH\n\tINT 21H\n"
def getProcs(x=1):
    """
    This function returns a string containing a list of procedures and the string "END START".
    
    :param x: The parameter x is an optional integer parameter with a default value of 1. It is used to
    control the output of the function. If x is set to 0, the function will only return the procedures
    section of the output without the "END START" line. If x is set to any, defaults to 1 (optional)
    :return: a string that contains information about the procedures in the program, as well as the
    string "END START". The "x" parameter is used to control whether or not the "END START" string is
    included in the returned value. If x is 0, only the information about the procedures is returned.
    """
    s = str()
    if has(procs):
        s += ('\n;' + '=' * L + "PROCEDURES" + '=' * L + '\n')
        for i in range(len(procs)):
            s += f"\n{procs[i]}\n"
    if x==0:return s
    return s + "\nEND START"

def combiner(x=0):
    """
    This function returns a dictionary or string depending on the input parameter and whether the
    function has been edited.
    
    :param x: The parameter x is used to determine the behavior of the function. If x is equal to 1, the
    function will return a dictionary containing information about the current state of the function. If
    x is not equal to 1, the function will return a string containing the combined macros, data, code,
    defaults to 0 (optional)
    :return: The function `combiner` returns different values based on the input parameter `x` and the
    value of a global variable `EDITED`. If `x` is 1 and `EDITED` is False, it returns a dictionary
    containing the values of `macs`, `data`, `code`, and `procs`. If `x` is 1 and `EDITED` is True
    """
    #NEED TO DISPLAY WHEN NOT EDITED
    if EDITED and x==1:#if edited no matter what return cstring
        return {"EDITED":True,"c":'\n'.join(c)}
    elif x==1:#not edited => ned for backup 
        return {"EDITED":False,"macs":macs,"data":data,"code":code,"procs":procs}#dict
    elif EDITED:
        return '\n'.join(c)
    else:#for print
        return(getMacros()+getData()+getCode()+getProcs())

def finalCode(x=0):
    """
    This function creates a backup file and writes the combined code to a specified program file, and
    can also return the backup data if requested.
    
    :param x: The parameter x is an optional integer parameter that determines the behavior of the
    function. If x is not provided or set to 0, the function will create a backup of the current program
    code and update the backup file with the current code. If x is set to 1, the function will write,
    defaults to 0 (optional)
    :return: The function `finalCode()` returns a dictionary containing the backup data if the `x`
    parameter is 0 or 1, and returns nothing if the `x` parameter is 2.
    """
    #0 - backup 1 - +write| 2 - return only
    if x==1:
        with open(PROGRAM,"w") as f:
            f.write(combiner())
            print(f"Check C:/8086/{PROGRAM} on your DOSBOX!")
    try:
        with open(BACKUPFILE,"r") as ff:    
            a=json.load(ff)
    except:
        checkbackup(1)
        a=dict()
    if x!=2:
        with open(BACKUPFILE,"w") as ff:
            a[str(dt.now())[:19]]=combiner(1)
            json.dump(a,ff,indent=4)
    if x==2:return a

def get(key):
    """
    The function "get" returns a collection of objects from a dictionary "defaults" that contain a given
    key.
    
    :param key: The parameter "key" is a variable that represents the key that we want to search for in
    the "defaults" dictionary. The function iterates through the values of the "defaults" dictionary and
    checks if the key exists in each value. If the key exists in a value, that value is added
    :return: The function `get` returns a list of all the objects in the `defaults` dictionary that
    contain the specified `key`.
    """
    collection=[]
    for name in defaults:
        obj = defaults[name]
        if key in obj:
            collection.append(obj)
    return collection

def collect(obj):
    """
    The function collects procedures, data, macros, and interrupts from an object and checks if they are
    already in the program, printing a warning if they are.
    
    :param obj: a dictionary object containing the following keys: "procs", "data", "macs", and "code".
    Each key corresponds to a list of strings representing procedures, data, macros, and interrupt code
    respectively
    """
    global procs,macs,data,code
    if "procs" in obj:
        for i in obj["procs"]:
            if i in procs:
                print("Warning: Procedure fully or partially already in program!")
                continue
            procs.append(i)
    if "data" in obj:
        for i in obj["data"]:
            if i in data:
                print("Warning: Data fully or partially already in program!")
                continue
            data.append(i)
    if "macs" in obj:
        for i in obj["macs"]:
            if i in macs:
                print("Warning: Macro fully or partially already in program!")
                continue
            macs.append(i)
    if "code" in obj:
        for i in obj["code"]:
            if i in code:
                print("Warning: Interrupt fully or partially already in program!")
                continue
            code.append(i)

def linsel(x,line,lis,z="edit"):
    """
    The function `linsel` allows the user to select and edit a line in a list, displaying a range of
    lines before and after the selected line.
    
    :param x: The value of x is used to determine whether the function should prompt the user for input
    or not. If x is not 0 or 1, the function will prompt the user for input. If x is 0, the function
    will prompt the user to enter a replacement line for the selected line
    :param line: The line number that the user wants to edit or view in the list
    :param lis: The list of lines that the function is operating on
    :param z: The parameter "z" is a string that specifies the action being performed in the function.
    It is used in the input prompt to provide context to the user. The default value of "z" is "edit",
    defaults to edit (optional)
    :return: different values depending on the input parameters and user input. If `x` is not equal to 0
    or 1, the function prompts the user to enter a number and returns the integer value of that number
    minus 1. If an exception occurs during the input process, the function calls itself recursively. If
    `x` is equal to 0, the function prompts the user to
    """
    if x!=0 and x!=1:
        try:
            x = input(f"Enter {line} number to {z} (0-Back): ")
            while int(x) not in range(len(lis)-1):
                print("Invalid input enter again!")
                x = input(f"Enter {line} number to {z} (0-Back): ")
            return int(x)-1#actual index
        except:linsel(x,line,lis);return

    line = int(line)-1
    if line<4:temp=0
    else: temp=line-3
    if line>len(lis)-4:temp2=len(lis)
    else: temp2=line+4

    if x == 0:
        for i in range(temp,temp2):
            if i==line:print(f"  | >",end="")
            print(f"{i+1}\t|{lis[i]}")
        replacement = input("-"*LL+"\nEnter Replacement Line: ")
        if "\t" in lis[line] or "    " in lis[line]:
            lis[line] = "    "+replacement
        else: lis[line] = replacement
        return lis
    elif x==1:
        print("Edits Applied\n"+"=="*LL)
        for i in range(temp,temp2):
            if i==line:print(f"  | >",end="")
            print(f"{i+1}\t|{lis[i]}")

#    ask function displays a menu of options and prompts the user to select an option,
#    then calls a corresponding function based on the user's input.
#    :param x: The optional parameter x has a default value of 1 and is used to determine which options
#    to display to the user. If x is 1, the full list of options is displayed. If x is 0, the program
#    creates a backup of the code and exits, defaults to 1 (optional)
#    :return: Nothing is being returned. The function is simply printing out options and taking user
#    input to execute different actions based on the input.  
def ask(x=1):
    if x==1:print("-"*LL+"Options"+LL*"-"+"""\n0 - Apply Edits/Change Specific Lines\n\t|1| !Whole Program (Final)!\t|2| Macs\t|3| Code\t|4| Procs\t|5| Data\t
1 - View\n\t|11| - Whole Program\t\t\t|12| - Macros\n\t|13| - Code\t\t\t\t|14| - Procedures\n\t|15| - Data and Variables
2 - Add Macro\n\t|21| - Default Macros\t\t\t|22| - Custom Macro (with All PUSHS/POPS)\n\t|23| - Custom Blank Macro 
3 - Add Code\n\t|31| - Default Interrupts\t\t|32| - Add a line of code\n\t|33| - Add a Block of Code
4 - Add Procedure\n\t|41| - Default Procedures\t\t|42| - Custom Procedures (with All PUSHS/POPS)\n\t|43| - Custom Blank Procedure 
5 - Add Data\n\t|51| - String\t\t\t\t|52| - Byte(s)\n\t|53| - Word\t\t\t\t|54| - Dup Array\n\t|55| - 0 Array
6 - Settings\n\t|61| - Change Filename\n\t(Coming Soon)\n\tx62x - Store new default macs/procs/int as options\n\tx63x - Load another save\t\tx64x - Merge()
7 - Save asm and Exit\n"""+"--"*40)
    choice = (input("\n|>=[ "))
    try:
        temp=int(choice)
    except:
        print("Invalid!")
        ask(0)
        return
    if temp<6 and temp>0:M0(temp)
    elif temp>=11 and temp<=16:M1(int(choice[1]))
    elif temp>=21 and temp<=24:M2(int(choice[1]))
    elif temp>=31 and temp<=34:M3(int(choice[1]))
    elif temp>=41 and temp<=44:M4(int(choice[1]))
    elif temp>=51 and temp<=56:M5(int(choice[1]))
    elif temp>=61 and temp<=64:M6(int(choice[1]))
    elif temp == 7:
        print("Creating backup",end="")
        for i in range(6):
            sleep(0.5);print(".",end="")
        finalCode(1)
        print('\n'+LL*">"+"Writing to your DOSBOX directory!"+LL*"<"+"\n"+5*"\t"+"Ending Program")
    elif temp == 0:
        print("Creating backup",end="")
        for i in range(6):
            sleep(0.5);print(".",end="")
        finalCode(0)
        print('\n'+LL*">"+"Backup Saved!"+LL*"<"+"\n"+5*"\t"+"Ending Program")
    else:
        print("Invalid! choice")
        ask(0)
        return

def M0(x):
    """
    This is a Python function that allows the user to edit different sections of code, including macros,
    procedures, and data.
    
    :param x: The input parameter to the function M0, which determines the specific action to be
    performed within the function. It could be either 1, 2, 22, 3, 33, 4, 44, 5, or 55
    :return: nothing (i.e., None).
    """
    if x==1:
        global c
        global EDITED
        print(f"{'--'*LL}\nIf you make final changes here the other features of the program may not be used again without manually overwriting these changes!\n{LL*'--'}")

        if not EDITED:c = combiner().splitlines()
        if x==1:
            for i in range(len(c)):
                print(f"{i+1}\t|{c[i]}")
        line=linsel(2,'line',c)
        if line!=-1:
            line+=1
            EDITED = True
            c=linsel(0,line,c)
            linsel(1,line,c)
            finalCode(0)
            cont(0,1)
        else:ask()
    else:       
        if x==2 or x==22:
            global macs
            m=macs.copy()
            if x==2:
                for i in range(len(m)):
                    print(f"\n\t\t\tMacro {i+1}:\n{m[i]}")
            mno = input("="*LL+"\nEnter Macro number to edit (0-Back): ")
        elif x==4 or x==44:
            global procs
            m=procs.copy()
            if x==4:
                for i in range(len(m)):
                    print(f"\n\t\t\tProcedure {i+1}:\n{m[i]}")
            mno = input("="*LL+"\nEnter Procedure number to edit (0-Back): ")
        if x==3 or x==33:
            global code
            m=code.copy()
        elif x==5 or x==55:
            global data
            m=data.copy()
        else:#should work on  2/4 aswell
            try:
                temp = int(mno)
                if temp>len(m) or temp<0:
                    assert 420==69
                if temp==0:
                    ask()
                    return
            except:
                print("Invalid!")
                if x==2 or x==22:M0(22)
                elif x==3 or x==33:M0(33)
                elif x==5 or x==55:M0(55)
                else:M0(44)
                return
            mno=int(mno)-1
            m=m[mno].splitlines()

        for i in range(len(m)):
            print(f"{i+1}\t|{m[i]}")
        line = input("="*LL+"\nEnter line number to edit (0-Back): ") 

        try:
            temp = int(line)
            if temp>len(m) or temp<0:
                assert 420==69
            if temp==0:
                ask()
                return
        except:
            print("Invalid!")
            if x==2 or x==22:M0(22)
            elif x==3 or x==33:M0(33)
            elif x==5 or x==55:M0(55)
            else:M0(44)
            return
        
        m=linsel(0,line,m)
        if x==2 or x==22:macs[mno]='\n'.join(m)
        elif x==3 or x==33:code='\n'.join(m)
        elif x==4 or x==44:procs[mno]='\n'.join(m)
        elif x==5 or x==55:data='\n'.join(m)
        linsel(1,line,m)
        finalCode(0)
        if x==2 or x==22:cont(0,2)
        elif x==3 or x==33:cont(0,3)
        elif x==4 or x==44:cont(0,4)
        elif x==5 or x==55:cont(0,5)    
    return
def M1(x):
    """
    The function M1 takes an input x and performs a specific Viewing action based on its value, then calls the
    function cont with arguments 1 and x.
    
    :param x: x is a parameter that is used to determine which action to perform in the M1 function.
    Depending on the value of x, the function will call different helper functions to retrieve and print
    information related to macros, code, procedures, and data. The cont(1,x) function is also called at
    :return: nothing (i.e., None).
    """
    if x==1:
        print(combiner())
    elif x==2:
        print(getMacros(0))
    elif x==3:
        print(getCode(0))
    elif x==4:
        print(getProcs(0))
    elif x==5:
        print(getData(0))
    cont(1,x)
    return
def M2(x):
    """
    The function M2 allows the user to view, add, and create macros in Python.
    
    :param x: The parameter x is used to determine which part of the function to execute. If x is equal
    to 1, the function will display a list of existing macros and allow the user to add a new one. If x
    is equal to 2 or 3, the function will prompt the user to
    :return: nothing (i.e., None).
    """
    if x==1:
        i=1
        coll=get("macs")
        for obj in coll:
            print(LL*"-")
            print(f"\t\t\tMacro {i}\nDescription: {obj['info']}")
            i+=1
            for j in obj['macs']:
                print(f"\n{j}\n")
        line = linsel(2,"Macro",coll,"add")
        if line!=-1:
            collect(coll[line])
            print("\nAdding Macro Complete!\n")
    elif x==2 or x==3:
        n = input("\nEnter your macro name: ")
        a = input("Enter argument name or leave blank if none: ")
        if x==2:
            lines=f"{n} MACRO {a}\nPUSH AX\nPUSH BX\nPUSH CX\nPUSH DX"
            print("\n\tEnter Your Code Line by Line\n\tThe indent and stack operations will be added automatically\n\tEnter $ as last line to exit\n")
        else:
            lines=f"{n} MACRO {a}\n"
            print("\n\tEnter Your Code Line by Line\n\tThe indent will be added automatically\n\tEnter $ as last line to exit\n")
        l = input("\t| ")
        while l!="$":
            lines+="\n\t"+l
            l = input("\t| ")
        if x==2:
            lines+="\nPOP DX\nPOP CX\nPOP BX\nPOP AX"
        lines+="\nENDM"
        print(">-"*LL+'\n\t'+f"MACRO {n} CREATED!\n"+"-<"*LL+"\n"+lines)
        macs.append(lines)

    cont(2,x)
    return
def M3(x):
    """
    The function M3 allows for the insertion of code into a global variable 'code' and the addition of
    interrupts to a collection.
    
    :param x: The parameter x is an integer that determines which action to perform in the M3 function.
    It can be 1, 2, or 3, and each value corresponds to a different action
    :return: nothing (i.e., None).
    """
    global code
    if x==1:
        i=1
        coll=get("code")
        for obj in coll:
            print(LL*"-")
            print(f"\t\t\tInterrupt {i}\nDescription: {obj['info']}")
            i+=1
            for j in obj['code']:
                print(f"\t{j}")
        line = linsel(2,"Interrupt",coll,"add")
        if line!=-1:
            collect(coll[line])
            
            print("\nAdding Interrupt Complete!\n") 
    elif x==2:
        for i in range(len(code)):
            print(f"{i+1}\t|{code[i]}")
        l=linsel(2,"line",code,"Insert Before")
        s = input(f"Enter Code to insert before line {l}: ")
        print(">-"*LL+'\n\t'+f"Code Inserted!\n"+"-<"*LL+"\n")
        code.insert(l,s)
    elif x==3:
        for i in range(len(code)):
            print(f"{i+1}\t|{code[i]}")
        l=linsel(2,"line",code,"Insert Before")
        s = input(f"Enter Code to insert before line {l}\nEnter $ as your last line to end block\n\n\t| ").strip()
        stat = 0
        while stat ==0:
            if s=="$":
                stat=1
            else:
                code.insert(l,s)
                l+=1
                s = input(f"\t| ").strip()
        print(">-"*LL+'\n\t'+f"Code Inserted!\n"+"-<"*LL+"\n")

    cont(3,x)
    return
def M4(x):
    """
    The function M4 allows the user to add or view procedures and input code line by line.
    
    :param x: The parameter x is an integer that determines which part of the code to execute. It is
    used as a control variable in an if-else statement to determine whether to add a new procedure or
    edit an existing one
    :return: nothing (i.e., None).
    """
    if x==1:
        i=1
        coll=get("procs")
        for obj in coll:
            print(LL*"-")
            print(f"\t\t\tProcedure {i}\nDescription: {obj['info']}")
            i+=1
            for j in obj['procs']:
                print(f"\n{j}\n")
        line = linsel(2,"Procedure",coll,"add")
        if line!=-1:
            collect(coll[line])
        print("\nAdding Procedure Complete!\n")         
        
    elif x==2 or x==3:
        n = input("\nEnter your procedure name: ")
        if x==2:
            lines=f"{n} PROC \nPUSH AX\nPUSH BX\nPUSH CX\nPUSH DX"
            print("\n\tEnter Your Code Line by Line\n\tThe indent and stack operations will be added automatically\n\tEnter $ as last line to exit\n")
        else:
            lines=f"{n} PROC \n"
            print("\n\tEnter Your Code Line by Line\n\tThe indent will be added automatically\n\tEnter $ as last line to exit\n")
        l = input("\t| ")
        while l!="$":
            lines+="\n\t"+l
            l = input("\t| ")
        if x==2:
            lines+="\nPOP DX\nPOP CX\nPOP BX\nPOP AX"
        lines+=f"\n{n} ENDP"
        print(">-"*LL+'\n\t'+f"PROCEDURE {n} CREATED!\n"+"-<"*LL+"\n"+lines)
        procs.append(lines)
    cont(4,x)
    return
def M5(x):
    """
    This is a Python function that allows the user to add different types of data (strings, bytes,
    words, and arrays) with labels to a global list called "data".
    
    :param x: The parameter x is an integer that determines which option the user has selected in the
    menu
    :return: nothing (i.e., None).
    """
    global data
    if x==1:
        n=input("Enter Label for your string (Eg: MSG):")
        s=input("Enter Your string (The indent and $ will be fixed automatically :)")+"$"
        s=f'{n} DB "{s[:s.find("$")+1]}"'
        data.append(s)
        print(f"\nData added: {s}")
    elif x==2:
        n=input("Enter Label for your Byte(s) (Eg: X):")
        s=n+" DB "+input("Enter Your Byte/Array comma seperated:")
        data.append(s)
        print(f"\nData added: {s}")
    elif x==3:
        n=input("Enter Label for your Word(s) (Eg: Y):")
        s=n+" DW "+input("Enter Your Word/Array comma seperated:")
        data.append(s)
        print(f"\nData added: {s}")
    elif x==4:
        n=input("Enter Label for your Dup Array (Eg: Z):")
        q=input("Enter the type of array you want (DB,DW,DD):").upper()
        while q not in ["DB","DW","DD"]:
            print("Invalid Choice!")
            q=input("Enter the type of array you want (DB,DW,DD):")
        check = 0
        while check==0:
            num = input("Enter number of dups you want: ")
            try:
                num = int(num)
                check=1
            except:
                print("Invalid Choice!")
        v = input("Enter the value you want to duplicate(Eg: 11H): ")
        s=f"{n} {num} DUP {q} ({v})"
        data.append(s)
        print(f"\nData added: {s}")
    elif x==5:
        n=input("Enter Label for your Dup Array (Eg: Z):")
        q=input("Enter the type of array you want (DB,DW,DD):").upper()
        while q not in ["DB","DW","DD"]:
            print("Invalid Choice!")
            q=input("Enter the type of array you want (DB,DW,DD):")
        check = 0
        while check==0:
            num = input("Enter number of dups you want: ")
            try:
                num = int(num)
                check=1
            except:
                print("Invalid Choice!")
        s=f"{n} {q} {num} DUP(0)"
        data.append(s)
        print(f"\nData added: {s}")
    cont(5,x)
    return
def M6(x):
    """
    The function M6 provides options to create a new file or edit a collection of code.
    
    :param x: The parameter x is an integer that determines which action to perform in the function M6
    """
    if x==1:
        name=input("Enter the new file name to store your program in\nLeave blank to revert to defaukt\n\n\t| ")+'.asm'
        if name!='':
            global PROGRAM
            PROGRAM = name[:name.find('.asm')+4]        
        print(f"{PROGRAM} will be used this time")
    elif x==2:
        print("\n\tComing soon - Right now you can create/edit collection.json to add you own code!\nformat:{_name_}:{'info':'_','procs':[] or 'macs':[] or 'code':[] + can also have 'data':[]}\nor check default dict in this py file")
    else:
        print("Coming soon!")
    sleep(2)
    ask()

def cont(menu,retarg):
    """
    This function prompts the user to continue with a specific action based on the menu option selected.
    
    :param menu: an integer representing the current menu or action being performed
    :param retarg: It is a variable that stores the current state or data of the program and is passed
    as an argument to the different functions called within the "cont" function. This allows the program
    to continue from where it left off after the user decides to continue editing, viewing, or adding
    macros, code, procedures
    :return: Nothing is being returned explicitly in this code. However, the function may indirectly
    return a value if it calls another function that returns a value.
    """
    if menu==0:
        msg = (input("Continue Editing?(Y/N): ")).upper()
        if ((msg).strip()[0]) == "Y":
            M0(retarg)
        elif ((msg).strip()[0]) == "N":
            ask()
        else:
            print("Invalid!")
            cont(menu,retarg)
            return
    elif menu==1:
        msg = (input("Continue Viewing?(Y/N): ")).upper()
        if ((msg).strip()[0]) == "Y":
            M1(retarg)
        elif ((msg).strip()[0]) == "N":
            ask()
        else:
            print("Invalid!")
            cont(menu,retarg)
            return
    elif menu==2:
        msg = (input("Continue Adding Macros?(Y/N): ")).upper()
        if ((msg).strip()[0]) == "Y":
            M2(retarg)
        elif ((msg).strip()[0]) == "N":
            ask()
        else:
            print("Invalid!")
            cont(menu,retarg)
            return
    elif menu==3:
        msg = (input("Continue Adding Code?(Y/N): ")).upper()
        if ((msg).strip()[0]) == "Y":
            M3(retarg)
        elif ((msg).strip()[0]) == "N":
            ask()
        else:
            print("Invalid!")
            cont(menu,retarg)
            return
    elif menu==4:
        msg = (input("Continue Adding Procedures?(Y/N): ")).upper()
        if ((msg).strip()[0]) == "Y":
            M4(retarg)
        elif ((msg).strip()[0]) == "N":
            ask()
        else:
            print("Invalid!")
            cont(menu,retarg)
            return
    elif menu==5:
        msg = (input("Continue Adding Data?(Y/N): ")).upper()
        if ((msg).strip()[0]) == "Y":
            M5(retarg)
        elif ((msg).strip()[0]) == "N":
            ask()
        else:
            print("Invalid!")
            cont(menu,retarg)
            return

#FINAL CODE GENERATOR
# The below code is calling two functions: `checkbackup()` and `ask()`.
checkbackup()
ask()
