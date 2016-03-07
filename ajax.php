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
else if($action=="updatehistory"){
  $ps=parseParams($params);
  $histfile="$STOREDIR/history.log";
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
}
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//UPDATE HISTORY
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else if($action=="updatejd"){
  $ps=parseParams($params);
  $date=$ps["date"];
  $qjd=rtrim(shell_exec("PYTHONPATH=. python util/date2jd.py '$date'"));
  if(isBlank($qjd)){$html="Bad date";}
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
