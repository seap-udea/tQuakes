<?php
//======================================================================
//START
//======================================================================
////////////////////////////////////////////////////////////////////////
//LOAD UTILITIES
////////////////////////////////////////////////////////////////////////
require_once("site/util.php");
$htm="";

if(0){}
////////////////////////////////////////////////////////////////////////
//ACTIONS
////////////////////////////////////////////////////////////////////////

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//UPDATE HISTORY
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else if($action=="insertquakes"){
  $ps=parseParams($params);

  //CONVIRTIENDO A CSV
  $xls2csv="LC_NUMERIC='sl' /usr/bin/ssconvert ".$ps["input"]." ".$ps["output"]." &> /tmp/ssconvert";
  $out1=shell_exec($xls2csv);

  //INSERTANDO SISMOS
  $cmdinsert="PYTHONPATH=. python db/insertquakes.py ".$ps["output"]." &> /tmp/insert";
  $cmdinsert="echo '$cmdinsert' > /tmp/insert";
  $out2=shell_exec($cmdinsert);

  echo "Valores outxls=$out1,outins=$out2";
}
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//UPDATE HISTORY
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else if($action=="updatehistory"){
  $ps=parseParams($params);
  $histfile="$SCRATCHDIR/history.log";
  if(file_exists($histfile)){
    $lines=file($histfile);
    $html="<h2>Search History</h2><ul>";
    foreach($lines as $line){
      if(isBlank($line)){continue;}
      $parts=preg_split("/;;/",$line);
      $date=$parts[0];
      $explanation=$parts[1];
      $query=$parts[2];
      $query_url=urlencode($query);
      if(!isBlank($explanation)){
	$html.="<li>$date<br/>$explanation<br/>";
      }else{$html.="<li>$date<br/>";}
      $html.="<a href='?if=search&search=$query_url'>$query</a></li>";
    }
    $html.="</ul>";
  }else{
    $html="No history";
  }
  $html.="<p><a href=?if=search&action=cleanhistory>Clean history</a></p>";
}
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//UPDATE HISTORY
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else if($action=="updatejd"){
  $ps=parseParams($params);
  $date=$ps["date"];
  $cmd="PYTHONPATH=. python util/date2jd.py '$date'";
  $qjd=rtrim(shell_exec("PYTHONPATH=. python util/date2jd.py '$date'"));
  if(isBlank($qjd)){$html="Bad date, eg. 24/12/09 00:00:00";}
  else{$html=$qjd;}
}

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//NOT RECOGNIZED
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else{
  $html.="Option not recognized";
}

////////////////////////////////////////////////////////////////////////
//RETURN
////////////////////////////////////////////////////////////////////////
echo $html;
?>
