#IPP projetk 2 - interpret jazyka iipcode20
#autor: Vojtech Krejcik
#login: xkrejc68
import re
import xml.etree.ElementTree as ET
import getopt
import sys
from int_lib import *





def main():
    source = ""
    inputDir = ""
    
#============Parsing arguments==============#
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h" ,["help", "source=", "input="]) 
    except getopt.GetoptError as err:
        printError(10, "getopt selhal") 
    
    if args:
        printError(10, "nepodporovane argumenty") 
    
    for o, a in opts:
        if o in ("-h","--help"):
            print("--help - vypis napovedy\n--source=file - vstupní soubor s XML reprezentací zdrojového kódu\n--input=file - soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu")
            exit(0)
        elif o == "--source":
            source = a
        elif o == "--input":
            inputDir = a;

    if source == "":
        if inputDir == "":
            printError(10, "input, nebo source chybi")
        else:
            sourceFile = sys.stdin
            inputFile = open(inputDir)
    elif inputDir == "":
        sourceFile = open(source)
        inputFile = sys.stdin
    else:
        sourceFile = open(source)
        inputFile = open(inputDir)

#============Some other things==============#
    instructions = {}
    labels = {}
    try:    
        tree = ET.parse(sourceFile)
        program = tree.getroot()
    except:
        printError(31, "spatny format xml")
    #==============saving instruction elements to dictioanary with order as key==================#
    for instruction in program:
        if len(instruction.attrib) != 2:
            printError(32, "instrukce ma spatny pocet xml attributu")
        if instruction.tag == 'instruction' and 'order' in instruction.attrib and 'opcode' in instruction.attrib:
            try:
                if int(instruction.attrib['order']) < 1:
                    printError(32, "order mensi, nez nula")
            except:
                printError(32, "order neni cislo")
            #============creating dict of labels===========================================#
            if instruction.attrib['opcode'] == 'LABEL':
                label = list(instruction)[0].text
                if label in labels:
                    printError(52, "refefinice lejblu")

                labels[list(instruction)[0].text] = int(instruction.attrib['order'])
            if int(instruction.attrib['order']) in instructions:
                printError(32, "opakujici se order u instrukce")
            else:
                instructions[int(instruction.attrib['order'])] = instruction
        else:
            printError(32, "spatny xml")
    

    if not instructions.keys():
        exit(0)
    else:
         maxOrder = max(instructions.keys()) + 1
    order = 1



###############################################################################
###############################################################################
#running the program
    symbol = ("var", "int", "bool", "string", "nil")
    variables = Variables()
    while(order < maxOrder):
        if order not in instructions:
            order += 1
            continue
        inst = instructions[order].attrib['opcode'] #jmeno instrukce
        #=======================================================================#
        #matemticke funkce - sjednoceny protoze vyzaduji vsechny stejne argumenty
        if inst in ("ADD", "SUB", "MUL", "IDIV"):
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (int, int)):
                if inst == "ADD":
                    variables.updateVar(args[0].text, variables.getValue(args[1]) + variables.getValue(args[2]))
                if inst == "SUB":
                    variables.updateVar(args[0].text, variables.getValue(args[1]) - variables.getValue(args[2]))
                if inst == "MUL":
                    variables.updateVar(args[0].text, variables.getValue(args[1]) * variables.getValue(args[2]))
                if inst == "IDIV":
                    if variables.getValue(args[2]) == 0:
                        printError(57, "deleni nulou")
                    variables.updateVar(args[0].text, variables.getValue(args[1]) // variables.getValue(args[2]))
            else:
                printError(53, "matemticke operace vyzaduji var, int, int")
        elif inst == "MOVE":
            args = getArgs(instructions[order], 2)
            if args[0].attrib['type'] == "var" and args[1].attrib['type'] in symbol:
                variables.updateVar(args[0].text, variables.getValue(args[1]))
            else:
                printError(53, "MOVE potrebuje jako arg1 var a druhy <symb>")
        #======================================================================#
        #instruckce pro praci s framy a promenymi
        elif inst == "CREATEFRAME":
            if len(instructions[order]) != 0:
                printError(32, "instrukce bez argumentu ma argumenty")
            variables.createFrame()
        elif inst == "PUSHFRAME":
            if len(instructions[order]) != 0:
                printError(32, "instrukce bez argumentu ma argumenty")
            variables.pushFrame()
        elif inst == "POPFRAME":
            if len(instructions[order]) != 0:
                printError(32, "instrukce bez argumentu ma argumenty")
            variables.popFrame()
        elif inst == "DEFVAR":
            args = getArgs(instructions[order], 1)
            if args.attrib['type'] == 'var':
                variables.createVar(args.text)

        elif inst == "CALL":
            arg = getArgs(instructions[order], 1)
            if arg.attrib['type'] == 'label':
                variables._call_stack.append(1 + order)
                try:
                    order = labels[arg.text]
                except:
                    printError(52, "neexistujici navesti")
            else:
                printError(53, "instrukce call vyzaduje jako argument label")
        elif inst == "RETURN":
            if len(instructions[order]) != 0:
                printError(32, "instrukce bez argumentu ma argumenty")
            try:
                order = variables._call_stack.pop() - 1
            except:
                printError(56, "zadna hodnota v datovem zasobniku")
        #=========================================================================#
        #funkce pro porovnani a logicke funkce
        elif inst == "LT":
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and (variables.typeOfArgs(args[1:], (int, int)) or variables.typeOfArgs(args[1:], (bool, bool)) or variables.typeOfArgs(args[1:], (str, str))):
                variables.updateVar(args[0].text, variables.getValue(args[1]) < variables.getValue(args[2]))
            else:
                printError(53, "typy se neshoduji")
        
        elif inst == "GT":
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and (variables.typeOfArgs(args[1:], (int, int)) or variables.typeOfArgs(args[1:], (bool, bool)) or variables.typeOfArgs(args[1:], (str, str))):
                variables.updateVar(args[0].text, variables.getValue(args[1]) > variables.getValue(args[2]))
            else:
                printError(53, "typy se neshoduji")
        
        elif inst == "EQ":
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and (variables.typeOfArgs(args[1:], (int, int)) or variables.typeOfArgs(args[1:], (bool, bool)) or variables.typeOfArgs(args[1:], (str, str))):
                variables.updateVar(args[0].text, variables.getValue(args[1]) == variables.getValue(args[2]))
            elif args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (Nil, Nil)):     
                variables.updateVar(args[0].text, True)
            elif  (isinstance(variables.getValue(args[1]), Nil) or isinstance(variables.getValue(args[2]), Nil)):
                variables.updateVar(args[0].text, False)
            else:
                printError(53, "typy se neshoduji")
        
        elif inst == "AND":

            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (bool, bool)):
                variables.updateVar(args[0].text, variables.getValue(args[1] and variables.getValue(args[2])))
            else:
                print(variables.typeOfArgs(args[1:], (bool, bool)))
                printError(53, "logicke funkce vyzdaji argumenty typu var, bool, bool")
        elif inst == "OR":

            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (bool, bool)):
                variables.updateVar(args[0].text, variables.getValue(args[1]) or variables.getValue(args[2]))
            else:
                printError(53, "logicke funkce vyzdaji argumenty typu var, bool, bool")
        elif inst == "NOT":
            args = getArgs(instructions[order], 2)
            if args[0].attrib['type'] == "var" and isinstance(variables.getValue(args[1]), bool):
                variables.updateVar(args[0].text, not variables.getValue(args[1]))
            else:
                printError(53, "pozadovane argumenty var, bool")
        elif inst == "INT2CHAR":
            args = getArgs(instructions[order], 2)

            if args[0].attrib['type'] == "var" and isinstance(variables.getValue(args[1]), int):
                try:
                   variables.updateVar(args[0].text, chr(variables.getValue(args[1])))
                except:
                    printError(58, "spatna unicode sekvence")
            else:
                printError(53, "pozadovane argumenty var, bool")
        elif inst == "STRI2INT":
            args = getArgs(instructions[order], 3)
             
            if args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (str, int)):
                try:
                    variables.updateVar(args[0].text, ord(variables.getValue(args[1])[variables.getValue(args[2])]))
                except:
                    printError(58, "str2int")

            else:
                printError(53, "nepodporovane argumenty")

        elif inst == "LABEL":
            pass

        
        elif inst == "READ": 
            args = getArgs(instructions[order], 2)
            
            if args[0].attrib['type'] == "var" and args[1].attrib['type'] == 'type':
                if args[1].text not in ("int", "string", "bool"):
                    printError(57, "pozadovane typy jsou int, string, bool")
                inputLine =  inputFile.readline().rstrip()
                try:
                    if args[1].text == "int":
                        variables.updateVar(args[0].text, int(inputLine))
                    elif args[1].text == "bool":
                        variables.updateVar(args[0].text, inputLine.lower() == "true")
                    elif args[1].text == "string":
                        variables.updateVar(args[0].text, str(inputLine))
                except:
                    variables.updateVar(args[0].text, Nil())
            else:
                printError(53, "neni to typ -typ-")

        elif inst == "WRITE":
            arg = getArgs(instructions[order], 1)
             
            if isinstance(variables.getValue(arg), bool):
                if variables.getValue(arg):
                    print('true', end='')
                else:
                    print('false', end='')
            elif isinstance(variables.getValue(arg), (int, str)):
                print(variables.getValue(arg), end='')

            elif isinstance(variables.getValue(arg), Nil):
                print('', end='')

            
            elif isinstance(variables.getValue(arg), bool):
                if variables.getValue(arg):
                    print('true', end='')
                else:
                    print('false', end='')
            else:
                printError(53, "nepodporvany typ - write")
        
        elif inst == "CONCAT":
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (str, str)):
                variables.updateVar(args[0].text, variables.getValue(args[1]) + variables.getValue(args[2]))
            else:
                printError(53, "spatny typ argumentu")
            
        elif inst == "STRLEN":
            args = getArgs(instructions[order], 2)
            if args[0].attrib['type'] == "var" and isinstance(variables.getValue(args[1]), str):         
                variables.updateVar(args[0].text, len(variables.getValue(args[1])))
            else:
                printError(53, "spatny typ argumentu")
            
        elif inst == "GETCHAR":
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (str, int)):
                try:
                    variables.updateVar(args[0].text, variables.getValue(args[1])[variables.getValue(args[2])])
                except:
                    printError(58, "getchar velky spatny")
            else:
                printError(53, "spatny typ argumentu")
 
 
        elif inst == "SETCHAR":
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "var" and variables.typeOfArgs(args[1:], (int, str)):
                try:
                    index = variables.getValue(args[1])
                    string = variables.getValue(args[0])
                    result = string[:index] + variables.getValue(args[2]) + string[index + 1 :]
                    variables.updateVar(args[0].text, result)
                except:
                    printError(58, "setchar velky spatny")
            else:
                printError(53, "spatny typ argumentu")           

        elif inst == "JUMP":
            arg = getArgs(instructions[order], 1)
            if arg.attrib['type'] == "label":
                try:
                    order = labels[arg.text]
                except:
                    printError(52, "neexistujici navesti")

        elif inst == 'TYPE':
            args = getArgs(instructions[order], 2)
            if args[0].attrib['type'] == "var":
                if type(variables.getValue(args[1])).__name__ == "NoneType":
                    variables.updateVar(args[0].text, '')
                elif type(variables.getValue(args[1])).__name__  == "str":
                    variables.updateVar(args[0].text, type(variables.getValue(args[1])).__name__.lower() + "ing")
                elif type(variables.getValue(args[1])).__name__ in symbol:
                    variables.updateVar(args[0].text, type(variables.getValue(args[1])).__name__.lower())

            else:
                printError(53, "arg1 musi byt promena")


        elif inst == 'JUMPIFEQ':
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "label" and (variables.typeOfArgs(args[1:], (int, int)) or variables.typeOfArgs(args[1:], (bool, bool)) or variables.typeOfArgs(args[1:], (str, str))):
                if variables.getValue(args[1]) == variables.getValue(args[2]):
                    try:
                        order = labels[args[0].text]
                    except:
                        printError(52, "neexistujici navesti")

            elif args[0].attrib['type'] == "label" and variables.typeOfArgs(args[1:], (Nil, Nil)):     
                try:
                    order = labels[args[0].text]
                except:
                    printError(52, "neexistujici navesti")


            elif args[0].attrib['type'] == "label" and   (isinstance(variables.getValue(args[1]), Nil) or isinstance(variables.getValue(args[2]), Nil)):
                pass
            else:
                printError(53, "typy se neshoduji")

     
     
        elif inst == 'JUMPIFNEQ':
            args = getArgs(instructions[order], 3)
            if args[0].attrib['type'] == "label" and (variables.typeOfArgs(args[1:], (int, int)) or variables.typeOfArgs(args[1:], (bool, bool)) or variables.typeOfArgs(args[1:], (str, str))):
                if variables.getValue(args[1]) != variables.getValue(args[2]):
                    try:
                        order = labels[args[0].text]
                    except:
                        printError(52, "neexistujici navesti")


            elif args[0].attrib['type'] == "label" and variables.typeOfArgs(args[1:], (Nil, Nil)):     
                pass
            elif args[0].attrib['type'] == "label" and   (isinstance(variables.getValue(args[1]), Nil) or isinstance(variables.getValue(args[2]), Nil)):
                try:
                    order = labels[args[0].text]
                except:
                    printError(52, "neexistujici navesti")

               
            else:
                printError(53, "typy se neshoduji")


        elif inst == "EXIT": 
            arg = getArgs(instructions[order], 1)
            
            if isinstance(variables.getValue(arg), int):
                number = variables.getValue(arg)
                if number in range(0, 49):
                    exit(number)
                else:
                    printError(57, "value error")
            else:
                printError(53, "spatny typ")

        elif inst == "DPRINT":
            arg = getArgs(instructions[order], 1)
            if arg.attrib['type'] in symbol:
                print(variables.getValue(arg), file=sys.stderr)
            
        elif inst == "BREAK":

            print(order, file=sys.stderr)
            print(variables._temp,  file=sys.stderr)
            print(variables._local_stack,  file=sys.stderr)
            print(variables._global, file=sys.stderr)
        else:
            printError(32, "neznama instrukce")

        order+=1 
################################################################################
################################################################################

        #some error stuff
#============Closing files==============#
    if sourceFile is not sys.stdin:
        sourceFile.close()

    if inputFile is not sys.stdin:
        inputFile.close()

if __name__ == "__main__":
    try:
        main()
    except UnboundLocalError:
        printError(32, "arguments are not okay probably")

