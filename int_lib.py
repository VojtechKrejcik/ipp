#IPP projetk 2 - interpret jazyka iipcode20
#autor: Vojtech Krejcik
#login: xkrejc68

import re

def replaceES(string):
    try:
        for i in range(0,126):
            pat = "\\" + str(i).rjust(3, "0")
            string = string.replace(pat, chr(i))
    except:
        printError(199, "intrenal Erro - replacing escape sequencies")
    return string

class Nil:
    pass

def printError(code, message):
    print(message)
    exit(code)

#________________________________________________________
#vrati tuple argumentu a zkontruluje mnozstvi a spravnost (nekontroluje typ)
def getArgs(instruction, no_expected):

    if len(list(instruction)) != no_expected:
        printError(32, "spatny pocet argumentu") 
    checkArgs = set()
    args = set()
    for arg in instruction:
        try:
            if arg.attrib['type'] not in ('var', 'type', 'bool', 'string', 'int', 'nil', 'label') or len(arg.attrib) != 1:
                printError(32, "neznamy typ")
        except:
            printError(32, "prilis atributu argumentu")
        
        if arg.tag == "arg1":
            checkArgs.add(arg.tag)
            arg1 = arg
        elif arg.tag == "arg2":
            checkArgs.add(arg.tag)
            arg2 = arg
        elif arg.tag == "arg3":
            checkArgs.add(arg.tag)
            arg3 = arg
        else:
            printError(32, "nepodporovany argument")

    if no_expected != len(checkArgs):
        printError(32, "sptane mnozstvi arguentu")
    if no_expected == 1:
        return arg1

    if no_expected == 2:
        return arg1, arg2
            
    if no_expected == 3:
        return arg1, arg2, arg3

#==========================================================================#
#inicializace framu a jejich metody
class Variables:
    _global = {}
    _temp = None
    _local_stack = list() #pouzivano jako stack
    _call_stack = list() #tez stack

#___________________________________________________________________________
#vytvori temporart frame
    def createFrame(self):
        self._temp ={}


#___________________________________________________________________________
#vlozi temp frame na vrchol stacku local framu
    def pushFrame(self):
        if self._temp == None:
            printError(55, "zadny temporary ramec")
        else:
            self._local_stack.append(self._temp)
            self._temp = None


#___________________________________________________________________________
#presune posledni local frame do temp frame
    def popFrame(self):
        try:
            self._temp = self._local_stack.pop()
        except:
            printError(55, "no local frame")


#___________________________________________________________________________
#vytvori promenou "DEFVAR"
    def createVar(self, variable):
        frame, name = self.parseName(variable)
        if frame == "GF":
            if name in self._global:
                printError(52, "redefinice promene")
            self._global[name] = None
        elif frame == "TF": 
            if self._temp == None:
                printError(55, "zasobnik, nebyl inicializovan")
            if name in self._temp:
                printError(52, "redefinice promene") 
            self._temp[name] = None
        elif frame == "LF":
            try:
                if name in self._local_stack:
                    printError(52, "redefinice promene")
                self._local_stack[-1][name] = None
            except:
                printError(55, "lokalni ramec neexistuje")
        else:
            printError(32, "neexistujici typ ramce")


#___________________________________________________________________________
#priradi promene hodnotu (napriklad v instukcich add, subb,...)
    def updateVar(self, variable, value):
        frame, name = self.parseName(variable)
        self.getVar(variable) #overi jestli existuje, hodnotu nepotrebuji a vrati spravny error code
        if frame == "GF":
            self._global[name] = value
        elif frame == "TF":  
            self._temp[name] = value
        elif frame == "LF":
            try:
                self._local_stack[-1][name] = value
            except IndexError:
                printError(55, "neexistujici ramec - updateVar()")
        else:
            printError(32, "zase neexistujici typ ramce")

#___________________________________________________________________________
#vrati hodnotu v dane promene
    def getVar(self, variable):
        frame, name = self.parseName(variable)
        try:
            if frame == "GF":
                return self._global[name]
            elif frame == "TF":  
                if self._temp == None:
                    raise IndexError()
                return self._temp[name]
            elif frame == "LF":
                return self._local_stack[-1][name]
            else:
                printError(32, "neexistujici stack")
        except KeyError:
            printError(54, "promena neexistuje")
        except IndexError:
            printError(55, "ramec neexistuje")

#___________________________________________________________________________
#rozdeli promenou na jmeno framu a jmeno
    def parseName(self, variable):
        frame, name = variable.split("@", 2)
        if frame not in ("GF", "LF", "TF") or not bool(re.match(r'^[\w\?\!\@\*\$\_\-\&]+$', name)):
            printError(32, "takhle by to neslo")
        else:
            return frame, name


    def getValue(self, arg):
        if arg.attrib['type'] == "var":
            return self.getVar(arg.text)
        elif arg.attrib['type'] == "int":
            try:
                return int(arg.text)
            except:
                printError(32, "nevhodna hodnota int")
        elif arg.attrib['type'] == "string":
            return replaceES(arg.text)
        elif arg.attrib['type'] == "bool":
            if arg.text == "false":
                return False
            elif arg.text == "true":
                return True
            else:
                printError(32, "error u boolu v getValue")
        elif arg.attrib['type'] == 'nil':
            return Nil()
        else:
            printError(32, "neznamy typ")


#requires list as args

    def typeOfArgs(self, args, types):
            size = len(args)
        
            arg1, arg2, arg3 = True, True, True
            if size > 0:
                arg1 = isinstance(self.getValue(args[0]), types[0])
            if size >1:
                arg2 = isinstance(self.getValue(args[1]), types[1])
            if size == 3:
                arg3 = isinstance(self.getValue(args[2]), types[2])
            return arg1 and arg2 and arg3


