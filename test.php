<?php
#IPP projetk 2 - interpret jazyka iipcode20
#autor: Vojtech Krejcik
#login: xkrejc68

function getNameByDirectory($dir){
	$dir = preg_replace('/^(.*\/)+/',"",$dir);
	return preg_replace('/\.src/',"", $dir);	
}
function echoFail($name){
	echo "<li>".$name." <font color=\"red\">FAILED</font></li>";
}

function echoPass($name){
	echo "<li>".$name." <font color=\"green\">PASSED</font></li>";
}
function main() {
#ZPRACOVANI ARGUMENTU
#---------------------------------------------------------------#
	$longopts = array(
		"help",
		"directory::",
		"recursive",
		"parse-script::",
		"int-script::",
		"parse-only",
		"int-only",
		"jexamxml=::",
	);
	
	$directory = getcwd();
	$optid;
	$options = getopt("h",$longopts, $optid);
	$recursive = FALSE;
	$parseOnly = FALSE;
	$intOnly = FALSE;
	$jxml ="/pub/courses/ipp/jexamxml/jexamxml.jar";
	$parseDirectory = getcwd()."/parse.php";
	$interpretDirectory = getcwd()."/interpret.py";
	if(array_key_exists("help", $options)){
		echo " --help - vypis napovedy
 --directory=path testy bude hledat v zadaném adresáři
 --recursive testy bude hledat nejen v zadaném adresáři, ale i rekurzivně ve všech jeho podadresářích;
 --parse-script=file soubor se skriptem v PHP 7.4 pro analýzu zdrojového kódu v IPP-code20
 --int-script=file soubor se skriptem v Python 3.8 pro interpret XML reprezentace kódu v IPPcode20
 --parse-only bude testován pouze skript pro analýzu zdrojového kódu v IPPcode20 
 --int-only bude testován pouze skript pro interpret XML reprezentace kódu v IPPcode20
 --jexamxml=file soubor s JAR balíčkem s nástrojem A7Soft JExamXML.\n";
		if($optid !=2) return 10;
		return 0;
	}

	if(array_key_exists("directory", $options)){
		$directory = $options["directory"];
	}

	if(array_key_exists("recursive", $options)){
		$recursive = TRUE;
	}
	
	if(array_key_exists("parse-only", $options)){
		$parseOnly = TRUE;
	}

	if(array_key_exists("jexamxml", $options)){
		$jxml = $options["jexamxml"];
	}	
	if($intOnly && $parseOnly){
		return 10;
	}

	if($intOnly){
		if(array_key_exists("parse-script", $options)){
			return 10;
		}	

	}

	if($parseOnly){
		if(array_key_exists("int-script", $options)){
			return 10;
		}	

	}
		#HLAVICKA HTML	
	#---------------------------------------------#
  echo "<!DOCTYPE html>
	<html>
		<head>
			<title>IPP testy</title>
		</head>
		<body>
			<h1>IPP projekt - testy</h1>
		<ul>
";


#---------------------------------------------------------------#
	#PROCHAZENI ADRESARU
	#otestovat fopen jako exception
#---------------------------------------------------------------#
	$passedTestsAll = 0;
	$failedTestsAll = 0;
	$passedTestsLast = 0;
	$failedTestsLast = 0;
	$lastDir = "";
	$first = TRUE;
	$test;
	$tests = array();
	$Dir = new RecursiveDirectoryIterator($directory);

	if($recursive) $Iterator = new RecursiveIteratorIterator($Dir);
	else $Iterator =  new IteratorIterator($Dir);
	$TestFiles = new RegexIterator($Iterator, '/^.+\.src$/i', RecursiveRegexIterator::GET_MATCH);
	foreach($TestFiles as $files){
		$name = getNameByDirectory($files[0]);
		$test = preg_replace('/.src/', "", $files[0]);			
		$currentTestDir = preg_replace("/".$name."/", "", $test);
		
		if(strcmp($lastDir, $currentTestDir)){
			$lastDir = $currentTestDir;
			if(!$first){
				echo "</ul><br>
				Summary of directory  <font color=\"green\">PASSED:</font>".$passedTestsLast." <font color=\"red\">FAILED:</font>".$failedTestsLast."<br>
";}
			$first =FALSE;
				echo	"<h3>".$currentTestDir."</h3>
				<ul>";
			$passedTestsLast = 0;
			$failedTestsLast = 0;
		}
			array_push($tests, $test);
		
			if(!file_exists($test.".rc")){
				$f = fopen($test.".rc", "w");
				fwrite($f,"0");
				fclose($f);
			}
		
			if(!file_exists($test.".in")){
				$f = fopen($test.".in", "w");
				fclose($f);
			}
		
			if(!file_exists($test.".out")){
				$f = fopen($test.".out", "w");
				fclose($f);
			}

				#TESTOVANI
			#---------------------------------------------#
			$someArray = array();
			$file = fopen($test.".rc", "r");
			$wanted_retval = fread($file, 10);
			fclose($file);

			if($parseOnly){
				exec("php ".$parseDirectory." < ".$test.".src > result.tmp 2>errs.tmp",$someArray, $retval);	
				if($wanted_retval != $retval){	
					echoFail($name);
					$failedTestsAll++;
					$failedTestsLast++;
				}else{
					if($retval){
						echoPass($name);
						$passedTestsAll++;
						$passedTestsLast++;
							
					}else{
						exec("java -jar ".$jxml." ".$test.".out result.tmp diffs.xml", $someArray, $retval);
						if($retval){
							echoFail($name);	
							$failedTestsAll++;
							$failedTestsLast++;
						}
						else{ 
							echoPass($name);
							$passedTestsAll++;
							$passedTestsLast++;
						}

					}
				}
				
			}else{ 
				if($intOnly){
					exec("python3.8 ".$interpretDirectory." < ".$test.".src > result.tmp", $someArray, $retval);		
				}else{ #both
			
					exec("php7.4 ".$parseDirectory." < ".$test.".src > result.tmp 2>errs.tmp",$someArray, $retval);	
					exec("python3.8 ".$interpretDirectory." < ".$test.".src > result.tmp", $someArray, $retval);		
				}
				
				if($retval){
					echoPass($name);		
					$passedTestsAll++;
					$passedTestsLast++;


				}else{
					exec("diff ".$test."out result.tmp", $someArray, $retval);
					if($retval){
						echoFail($name);	
						$failedTestsAll++;
						$failedTestsLast++;
					}
					else{
						echoPass($name);
						$passedTestsAll++;
						$passedTestsLast++;

					}
				}
			}
		}

			#KONEC HTML	
		#---------------------------------------------#
	echo "</ul><br>
				Summary of directory  <font color=\"green\">PASSED:</font>".$passedTestsLast." <font color=\"red\">FAILED:</font>".$failedTestsLast."<br>
<br><br>";
		echo "<h2>Summary  <font color=\"green\">PASSED:</font>".$passedTestsAll." <font color=\"red\">FAILED:</font>".$failedTestsAll."</h3>";
		echo "		</body>
		</html>";	
	}


		return main();



	?>
