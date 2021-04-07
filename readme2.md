# Implementační dokumentace k 2. úloze do IPP 2019/2020  
Jméno a příjmení: Vojtěch Krejčík  
Login: xkrejc68

## Využívané moduly  

___re___ - pro regularní výrazy    

___xml.etree.ElementTree___ - pro zpracováni vstupního xml  

___getopt___ - pro zpracování argumentů  

___sys___ - pro práci se stdin  

## Základní funkcionalita

Po zpracování xml souboru pomoci funkcí z knihovny xml.etree.ElementTree je výsledný objekt procházen for cyklem a instrukce vloženy do slovniku
___instructions___, kde je k ním možné přistupovat pomocí atributu ___order___. Když se jedná o instrukci ___LABEL___ je vytvořeno návěstí ve slovníku
___labels___ kde klíčem je název návěstí a hodnotou ___order___.  

### Prace s proměnnými a rámci

Pro práci s rámci a proměnnými byla vytvořena třída ___Variables___, v jejíž atributech je slovnik ___global___ a ___temp___ pro globalní a lokální (ten je nastaven jako ___None___) rámec. Poté je tam atribut ___local_stack___, který je seznamem. Pracuje se s ním skrze metody ___createFrame___, ___psuhFrame___, ___popFrame___, tak aby fungoval jako zásobník. Pro práci s proměnnými jsou metody ___createVar___, ___updateVar___, ___getVar___, ___getValue___ (tato metoda funguje i s konstantami). Těmto metodám stačí předat název proměnné a samy zařídí, aby se přistupovalo ke správnému rámci.

### Běh programu

Hlavní smyčka iteruje skrze slovník instrukcí, vykonávání funkcí jednotlivých instukcí je řešeno pomocí rozsáhlého větvení pomocí příkazu if. Pro kazdou instukci s argumenty je volána funkce ___getArgs___ , případně ještě pro ověření typů metoda ___typeOfArgs___ (není řešeno ideálně).

## Testovací skript - test.php

Pro iterovaní adresáři je použita knihovna ___RecursiveDirectoryIterator___. Testy jsou řazeny podle složek. Na konci každé kategorie (složky) se vypíše souhrn všech testů dané kategorie. Na konci stránky je vypsán celkový souhrn všech testů. Pro přehlednost jsou úspěšné testy vypsané zeleně a neúspěšné červeně. Použity jsou základní tagy pro seznamy, nadpisy a odstavce. Barva textu je měněna v rámci html (není použito css)