from os import chdir,listdir,mkdir
from datetime import datetime as dt
from time import sleep
import json

BACKUPFILE="masmbackups.json"
LL=50

#Edited Code
EDITED = False
c = []
# Add Data here
data = []
#Add custom procs here
procs = []
#Add custom macros here
macs = []
#Add your code here
code = []

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
    "String Display":{
        "code":['MOV AH,02H','INT 21H'],
        "info":"Prints an immidiate character\nTakes character (eg:'>') from DL\n[No register modification]"
    }
}

chdir("C:/")
if '8086' not in listdir():
    print(listdir())
    print("'C:/8086' not found New directory being created!")
    mkdir("8086")
chdir("C:/8086")
if 'collection.json' in listdir():
    with open('collection.json') as f:
        globals().update({"defaults":json.load(f)})

def checkbackup(x=0):
    global BACKUPFILE,EDITED,c
    if (BACKUPFILE not in listdir()) or (x==1):
        print(">-"*LL+'\n\t'+f"Backup file not detected, creating new!\n"+"-<"*LL+"\n")
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
    if x==1:s = ".MODEL SMALL\n.STACK 100H\n"
    else: s=''
    if has(macs):
        s += ';' + '=' * LL + "MACROS" + '=' * LL + '\n'
        for i in range(len(macs)):
            s += f"\n{macs[i]}\n"
    return s

def getData(x=1):
    m='\n\n;'+'='*LL+"CODE"+'='*LL+'\n'
    if has(data):
        s = '\n;'+'='*LL+"VARIABLES"+'='*LL+'\n'+".DATA"
        for i in range(len(data)):
            s += f"\n\t{data[i]}"
        if x==0:return s + '\n'
        return s + m+ "\n.CODE\nSTART:\n\tMOV AX,@DATA\n\tMOV DS,AX\n"
    else:
        return m+"\n.CODE\nSTART:\n"

def getCode(x=1):
    s = str()
    if has(code):
        for i in range(len(code)):
            s += f"\n\t{code[i]}"
    if x==0:return s
    return s + "\n\n\tMOV AH,4CH\n\tINT 21H\n"

def getProcs(x=1):
    s = str()
    if has(procs):
        s += ('\n;' + '=' * LL + "PROCEDURES" + '=' * LL + '\n')
        for i in range(len(procs)):
            s += f"\n{procs[i]}\n"
    if x==0:return s
    return s + "\nEND START"

def combiner(x=0):
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
    #0 - backup 1 - +write| 2 - return only
    if x==1:
        with open("mpro.asm","w") as f:
            f.write(combiner())
            print("Check C:/8086/mpro.asm on your DOSBOX!")
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

#CALL IF YOU WANT TO HAVE THESE PROCS/MACROS

def PRINT():
    macs.append('PRINT MACRO MSG\nPUSH AX\nPUSH DX\n\tMOV AH,09H\n\tLEA DX,MSG\t;msg to be displayed\n\tINT 21H\t\nPOP DX\nPOP AX\nENDM')
    
def DISPDEC():
    procs.append("""DISPDEC PROC\nPUSH AX\nPUSH BX\nPUSH CX\nPUSH DX\n\tMOV CL,0
    \tLEA SI,_YY\n\n    BCK:MOV DX,0    \n\tMOV BX,0AH    \n\tDIV BX\n\t\t\t   ;R-DX\t  Q-AX\n\tMOV CH,DL\t 
    \tADD CH,30H    \n\tMOV [SI],CH\t;[SI] <- CH <- DL <- R\n\t\n\tINC SI\n\tINC CL
    \tCMP AX,0\t   ;AX <- Q    \tJNZ BCK\n\n     PNT:\n\tDEC SI\n\tMOV DL,[SI]\n\tMOV AH,02H
    \tINT 21H\n\tDEC CL    \n\tJNZ PNT\nPOP DX\nPOP CX\nPOP BX\nPOP AX  \nRET\nDISPDEC ENDP""")
    data.append("_YY DB DUP 5 (0)")

def INP():
    procs.append('''INP PROC\n\t   PUSH BX\n\tPUSH CX\n\t   MOV AH,01H\n\t   INT 21H\t\t ;GET INPUT ASCII
    \t   CMP AL,3AH\n\t   JC G\n\t   SUB AL,7H\n\t G:SUB AL,30H\t  ;CONVERT ASCII AL TO HEX\n\t   MOV CL,04H
    \t   ROL AL,CL\n\t   MOV BL,AL\t   ;UPPER NIBBLE IN BL\n\t   MOV AH,01H\n\t   INT 21H\n\t   CMP AL,3AH
    \t   JC H\n\t   SUB AL,7H\t   ;NEW LOWER NIBBLE HEX IN AL\n\t H:SUB AL,30H
    \t   OR AL,BL\t\t;COMBINE NIBBLES TO MAKE A BYTE IN AL\n\n\t   POP CX\n\tPOP BX\n\t   RET\nINP ENDP''')

def DISPAL():
    procs.append('''DISPAL PROC\n\tPUSH DX\n\tPUSH CX\n\tPUSH AX\n\t\tMOV CH,AL
    \t\tMOV CL,4\n\t\tMOV DL,CH\n\t\tROL DL,CL\n\t\tAND DL,0FH\n\t\tCMP DL,0AH\n\t\tJC PP
    \t\tADD DL,7\n\t PP:ADD DL,30H\n\t\tMOV AH,2\n\t\tINT 21H\n\n\t\tMOV DL,CH\n\t\tAND DL,0FH
    \t\tCMP DL,0AH\n\t\tJC GG\n\t\tADD DL,7\n\t GG:ADD DL,30H\n\t\tMOV AH,2\n\t\tINT 21H\n\tPOP AX
    \tPOP CX\n\tPOP DX\n\tRET\nDISPAL ENDP''')

def get(key):
    collection=[]
    for name in defaults:
        obj = defaults[name]
        if key in obj:
            collection.append(obj)
    return collection

def linsel(x,line,lis,z="edit"):

    if x!=0 and x!=1:
        try:
            x = input(f"Enter {line} number to {z}: ")
            while int(x)-1 not in range(len(lis)):
                print("Invalid input enter again!")
                x = input(f"Enter {line} number to {z}: ")
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
        replacement = input("=="*LL+"\nEnter Replacement Line: ")
        if "\t" in lis[line] or "    " in lis[line]:
            lis[line] = "    "+replacement
        else: lis[line] = replacement
        return lis
    elif x==1:
        print("Edits Applied\n"+"=="*LL)
        for i in range(temp,temp2):
            if i==line:print(f"  | >",end="")
            print(f"{i+1}\t|{lis[i]}")
    
def ask(x=1):
    if x==1:print("--"*LL+"""\n0 - Apply Edits/Change Specific Lines\n\t|1| !Whole Program (Final)!\t|2| Macs\t|3| Code\t|4| Procs\t|5| Data\t
1 - View\n\t|11| - Whole Program\n\t|12| - Macros\n\t|13| - Code\n\t|14| - Procedures\n\t|15| - Data and Variables
2 - Add Macro\n\t|21| - Default Macros\n\t|22| - Custom Macro (with All PUSHS/POPS)\n\t|23| - Custom Blank Macro 
3 - Add Code\n\t|31| - Default Interrupts\n\t|32| - Add a line of code\n\t|33| - Add a Block of Code
4 - Add Procedure\n\t|41| - Default Procedures\n\t|42| - Custom Procedures (with All PUSHS/POPS)\n\t|43| - Custom Blank Procedure 
5 - Add Data\n\t|51| - String\n\t|52| - Byte(s)\n\t|53| - Word\n\t|54| - Dup Array\n\t|55| - 0 Array
6 - Save\n"""+"--"*40)
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
    elif temp == 6:
        print("Creating backup",end="")
        for i in range(6):
            sleep(0.5);print(".",end="")
        finalCode(1)
        print('\n'+LL*">"+"Writing to your DOSBOX directory!"+LL*"<"+"\n"+5*"\t"+"Ending Program")
        exit()
    elif temp == 0:
        print("Creating backup",end="")
        for i in range(6):
            sleep(0.5);print(".",end="")
        finalCode(0)
        print('\n'+LL*">"+"Backup Saved!"+LL*"<"+"\n"+5*"\t"+"Ending Program")
        exit()
    else:
        print("Invalid! choice")
        ask(0)
        return

def M0(x):
    if x==1 or x==11:
        global c
        global EDITED
        print(f"{'-'*LL}\nIf you make final changes here the other features of the program may not be used again without manually overwriting these changes!\n{LL*'-'}")

        if not EDITED:c = combiner().splitlines()
        if x==1:
            for i in range(len(c)):
                print(f"{i+1}\t|{c[i]}")
        line = input("="*LL+"\nEnter line number to edit (0-Back): ")
        try:
            temp = int(line)
            if temp>len(c) or temp<0:
                assert 420==69
            if temp==0:
                ask()
                return
        except:
            print("Invalid!")
            M0(11)
            return
        EDITED = True
        c=linsel(0,line,c)
        linsel(1,line,c)
        finalCode(0)
        cont(0,1)
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
        global procs,macs,data,code
        if "procs" in coll[line]:
            for i in coll[line]["procs"]:
                if i in procs:
                    print("Warning: Procedure fully or partially already in program!")
                    continue
                procs.append(i)
        if "data" in coll[line]:
            for i in coll[line]["data"]:
                if i in data:
                    print("Warning: Data fully or partially already in program!")
                    continue
                data.append(i)
        if "macs" in coll[line]:
            for i in coll[line]["macs"]:
                if i in macs:
                    print("Warning: Macro fully or partially already in program!")
                    continue
                macs.append(i)
        if "code" in coll[line]:
            for i in coll[line]["code"]:
                if i in macs:
                    print("Warning: Interrupt fully or partially already in program!")
                    continue
                code.append(i)
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
        global procs,macs,data
        if "procs" in coll[line]:
            for i in coll[line]["procs"]:
                if i in procs:
                    print("Warning: Procedure fully or partially already in program!")
                    continue
                procs.append(i)
        if "data" in coll[line]:
            for i in coll[line]["data"]:
                if i in data:
                    print("Warning: Data fully or partially already in program!")
                    continue
                data.append(i)
        if "macs" in coll[line]:
            for i in coll[line]["macs"]:
                if i in macs:
                    print("Warning: Macro fully or partially already in program!")
                    continue
                macs.append(i)
        if "code" in coll[line]:
            for i in coll[line]["code"]:
                if i in code:
                    print("Warning: Interrupt fully or partially already in program!")
                    continue
                code.append(i)
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
        global procs,macs,data,code
        if "procs" in coll[line]:
            for i in coll[line]["procs"]:
                if i in procs:
                    print("Warning: Procedure fully or partially already in program!")
                    continue
                procs.append(i)
        if "data" in coll[line]:
            for i in coll[line]["data"]:
                if i in data:
                    print("Warning: Data fully or partially already in program!")
                    continue
                data.append(i)
        if "macs" in coll[line]:
            for i in coll[line]["macs"]:
                if i in macs:
                    print("Warning: Macro fully or partially already in program!")
                    continue
                macs.append(i)
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

def cont(menu,retarg):
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
checkbackup()
ask()
