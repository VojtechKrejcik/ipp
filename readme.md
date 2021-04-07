# Implementační dokumentace k 1. úloze do IPP 2019/2020  
Jméno a příjmení: Vojtěch Krejčík  
Login: xkrejc68

## Využívané knihovny a funkce
XMLWriter - pro zapis do xml  
preg_split - pro oddeleni podle mezer, nebo #  
preg_match - pro overeni spravnosti

## Základní funckionalita
Program ze stdin načíta po řádcích. Řádky jsou pak zbaveny komentářů pomocí __preg_split__ a pak rozděleny na jednotlivá "slova" v array words. Správnost instrukce je vyhodnocena ve switchi. Když je ověřena načtou se argumenty instrukce. Pro argumenty jsem vytvořil třídu __"argument"__ (v podstatě ji využívám místo struktury, která mi v php chyběla). Správnost argumentu je vyhodnocena v __konstruktoru__ třídy a jsou udržovaný data o typu, opcode i původni opcode(u proměných se liší), protože jsem původně počítal s kontrolou typů i argumentů instrukcí. 

## Moje knihovna parselib.php
-třída __*argument*__ -  konstruktor na základě textového řetězce vyhodnoti typ a opcode argumentu
```php
<?php
class argument{
    public $ogOpcode;
    public $type;
    public $opcode;
    public function __construct($operand) {
?>
```
-__*writeArg($xml, $order, %operand)*__ - vypíše xml pro arguemnt, order - je int, rozhoduje zda arg1, arg2, nebo arg3
priklad: 
```
<arg1 type="var">GF@counter</arg1>
```
  
-__*writeInstruction($xml, $order, $opcode, $operands, $nArgs)*__  - vypise xml pro instrukci, pro vypis arguemntů volá funkci __*writeArg*__. Argumenty jsou uloženy v array $operands, v $nArgs je int  určující počet argumentů(0-3)  
příklad:  
```
<instruction order="4" opcode="JUMPIFEQ">
  <arg1 type="label">e</arg1>
  <arg2 type="var">GF@counter</arg2>
  <arg3 type="string">aaa</arg3>
 </instruction>```
