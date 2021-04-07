<?php

use function PHPSTORM_META\type;

include "parselib.php";
ini_set('display_errors', 'stderr');
//**__MAIN__**
    //vypis napovedy a spatne argumenty
$short_opt = "h";
$long_opt = array("help");
$args = getopt($short_opt, $long_opt, $optind);

//zpracovani arguemntu help, ukonceni s chybou, kdyz jiny argument
if(isset($args["help"])||isset($args["h"])){
    echo "Ocekavany vstup v ippcode20 na stdin\n";
    exit(0);
}else if(($args == FALSE)&&($optind > 1)){ 
    echo "error-> nepodporovane argumenty, pouzijte --help pro napovedu\n";
    exit(10);
}
//inicializace xml
$xml = xmlwriter_open_memory();
xmlwriter_set_indent($xml, 1);
$res = xmlwriter_set_indent_string($xml, ' ');
xmlwriter_start_document($xml, '1.0', 'UTF-8');
//hlavicka pro ippcode20
xmlwriter_start_element($xml, "program");
xmlwriter_start_attribute($xml, "language");
xmlwriter_text($xml, "IPPcode20");
xmlwriter_end_attribute($xml);

$order = 0;//order pro vypis do xml
$headerFlag = FALSE;//kontrolje jestli se nacetla hlaivcka
try {
    while($line = fgets(STDIN)){
        //preskoci cely radek, kdyz zacina komentarem
        if($line[0] == "#"){
            continue;
        }
        $line = preg_split('/#/', $line , -1, PREG_SPLIT_NO_EMPTY); //smaze komentar
        $line = $line[0];
        $words = preg_split('/[\s]+/', $line, -1, PREG_SPLIT_NO_EMPTY);//rozdeli podle mezer
        
        //prevedeni instrukce na upper case, pro jednodussi kontrolu
        $words[0] = strtoupper($words[0]);
        $arguments = array(); //inicializace array pro predavani argumentu
        if($order == 0){
            if($words[0]==".IPPCODE20"){
                $headerFlag = TRUE;
                $order++;
                continue;
            }
        }else{
            if($headerFlag == FALSE){
                throw new Exception(21);
            }
        }

        switch($words[0]){     
            //instrukce bez argumentu
            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                writeInstruction($xml, $order, $words[0], $arguments, 0);
                break;
            //instrukce s jednim args
            case "DEFVAR":
            case "POPS":
                $arg1 = new argument($words[1]);
                if($arg1->type != "var"){
                    throw new Exception(23);
                }
                array_push($arguments, $arg1);

                writeInstruction($xml, $order, $words[0], $arguments, 1);

                break;
            case "CALL":
            case "LABEL":
            case "JUMP":
                $arg1 = new argument($words[1]);
                if($arg1->type != "label"){
                    throw new Exception(23);
                }
                array_push($arguments, $arg1);

                writeInstruction($xml, $order, $words[0], $arguments, 1);
                break;
            case "EXIT":
            case "DPRINT":
            case "WRITE":
            case "PUSHS":

                $arg1 = new argument($words[1]);
                if(!isSymb($arg1->type)){
                    throw new Exception(23);
                }
                array_push($arguments, $arg1);

                writeInstruction($xml, $order, $words[0], $arguments, 1);

                break;
            //instrukce se dvemi args        
            case "MOVE":
            case "INT2CHAR":
            case "STRLEN":
            case "NOT":
            case "TYPE":

                $arg1 = new argument($words[1]);
                array_push($arguments, $arg1);
                if($arg1->type != "var"){
                    throw new Exception(23);
                }


                $arg2 = new argument($words[2]);
                array_push($arguments, $arg2);
                if(!isSymb($arg2->type)){
                    throw new Exception(23);
                }
                writeInstruction($xml, $order, $words[0], $arguments, 2);
                break;
            case "READ":
                $arg1 = new argument($words[1]);
                array_push($arguments, $arg1);
                if($arg1->type != "var"){
                    throw new Exception(23);
                }


                $arg2 = new argument($words[2]);
                array_push($arguments, $arg2);
                if($arg1->type != "type"){
                    throw new Exception(23);
                }
                
                writeInstruction($xml, $order, $words[0], $arguments, 2);
                break;
            //instrukce se tremi args        
            case "ADD":
            case "SUB":
            case "MUL":
            case "IDIV":
            case "LT":
            case "GT":
            case "EQ":
            case "AND":
            case "OR":
            case "STRI2INT":
            case "CONCAT":
            case "GETCHAR":
            case "SETCHAR":
                $arg1 = new argument($words[1]);
                array_push($arguments, $arg1);
                if($arg1->type != "var"){
                    throw new Exception(23);
                }
                
                $arg2 = new argument($words[2]);
                array_push($arguments, $arg2);
                if(!isSymb($arg2->type)){
                    throw new Exception(23);
                }
               
                $arg3 = new argument($words[3]);
                array_push($arguments, $arg3);
                if(!isSymb($arg3->type)){
                    throw new Exception(23);
                }
                writeInstruction($xml, $order, $words[0], $arguments, 3);
                break;

            case "JUMPIFEQ":
            case "JUMPIFNEQ":
               
                $arg1 = new argument($words[1]);
                array_push($arguments, $arg1);
                if($arg1->type != "label"){
                    throw new Exception(23);
                }
                
                $arg2 = new argument($words[2]);
                array_push($arguments, $arg2);
                if(!isSymb($arg2->type)){
                    throw new Exception(23);
                }
                
                $arg3 = new argument($words[3]);
                array_push($arguments, $arg3);
                if(!isSymb($arg3->type)){
                    throw new Exception(23);
                }
                writeInstruction($xml, $order, $words[0], $arguments, 3);
                break;
            
            default:
                throw new Exception(22);
                break;
        }
        $order++;
    }
}catch(Exception $e){
    if($e->getMessage() == 21) exit(21);
    else if($e->getMessage()==22) exit(22);
    else exit(23);
}

//konec xml 
xmlwriter_end_element($xml);
xmlwriter_end_document($xml);
//xml na stdout
echo xmlwriter_output_memory($xml);
exit(0);
?>