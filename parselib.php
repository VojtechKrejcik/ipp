<?php

// konstruktor na zaklade textoveho retezce vyhodnoti
// typ a operacni kod argumentu, ktere jsou udrznovany v danych promenych tridy
class argument{
    public $ogOpcode;
    public $type;
    public $opcode;
    public function __construct($operand) {
        $this->ogOpcode = $operand;
        if(preg_match("[@]",$operand)){
            $operand = preg_split("[@]",$operand);
            switch($operand[0]){
                case "int":
                    $this->type = "int";
                    $this->opcode = $operand[1];

                    break;
                case "bool":
                    if(!preg_match("/^(true|false)$/", $operand[1]) ? true : false){
                        throw new Exception(23);
                    }
                    $this->type = "bool";

                    $this->opcode = $operand[1];
                    break;
                case "GF":
                case "LF":
                case "TF":
                    if(!preg_match("/^[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*/", $operand[1]) ? true : false){
                        throw new Exception(23);
                    }
                    $this->type = "var";
                    $this->opcode = $this->ogOpcode;

                    break;
                case "string":
                    $this->type = "string";
                    $this->opcode = $operand[1];
                    break;
                case "nil":
                    if($operand[1] != "nil"){
                        throw new Exception(23);
                    }
                    $this->type = "nil";     
                    $this->opcode = $operand[1];
                    break;
                default:
                    if(!empty($operand[0])) throw new Exception(23);
                    break;
            }
        }else{
            switch($operand){
                case "int":
                case "string":
                case "bool":
                    $this->type = "type";
                    $this->opcode = $operand;
                    $this->ogOpcode = $operand;
                    break; 
                case (preg_match("/^[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*/", $operand) ? true : false):
                    $this->type = "label";     
                    $this->opcode = $operand;     

                    break;
                default:
                    if(!empty($operand)) throw new Exception(23);
                    break;  
            }
        }
    }

}
//funkce vypisuje argumenty instrukci dle zadani
//volano jen v writeInstruction
//vypise xml pro arguemnt, $order - je int, rozhoduje zda arg1, arg2, nebo arg3
//operand - opcode argumentu
function writeArg($xml,$order, $operand){
    
    xmlwriter_start_element($xml, "arg$order");
        xmlwriter_start_attribute($xml, "type");
        xmlwriter_text($xml, $operand->type);
        xmlwriter_end_attribute($xml);
        xmlwriter_text($xml, $operand->opcode);
       
    xmlwriter_end_element($xml);
}


//vypise xml pro instrukci
//pro vypis arguemntu vola funkci __*writeArg*__
//Argumenty jsou ulozeny v array $operands
//v $nArgs je int  urcujici pocet argumentu(0-3) 
function writeInstruction($xml, $order, $opcode, $operands, $nArgs){
    xmlwriter_start_element($xml, "instruction");
    xmlwriter_start_attribute($xml, "order");
    xmlwriter_text($xml, $order);
    xmlwriter_start_attribute($xml, "opcode");
    xmlwriter_text($xml, $opcode);
    xmlwriter_end_attribute($xml);
    if($nArgs >= 1){
        writeArg($xml, 1, $operands[0]);
    }
    if($nArgs >= 2){
        writeArg($xml, 2, $operands[1]);
    }
    if($nArgs == 3){
        writeArg($xml, 3, $operands[2]);
    }
    
    
    xmlwriter_end_element($xml);
}

//overi zda typ je neterminalem <symb>, vraci TRUE/FALSE
function isSymb($type){
   if($type == "var" || $type == "int" || $type == "string" || $type == "bool"){
       return TRUE;
   }else{
       return FALSE;
   } 
}

?>