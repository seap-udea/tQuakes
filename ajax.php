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
//DECLUSTER EARTHQUAKES
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else if($action=="decluster"){
  $ps=parseParams($params);

  //DECLUSTERING EARTHQUAKES
  $cmd="cd plots/processing;PYTHONPATH=. python decluster-quakes-R85.py ".$ps["all"]." 2> /tmp/decluster";
  $out=shell_exec($cmd);
  $err=shell_exec("cat /tmp/decluster");

  echo "$err";
}

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//INSERT EARTHQUAKES
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else if($action=="insertquakes"){
  $ps=parseParams($params);

  //INSERTANDO SISMOS
  $cmdinsert="PYTHONPATH=. python db/insertquakes.py ".$ps["output"]." ".$ps["label"]." 2>&1 |tee tmp/insert";
  $out2=shell_exec($cmdinsert);

  echo "$out2";
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
//UPDATE JULIAN DAY
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
//UPDATE HMOON AND HSUN
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
else if($action=="updatehmoonsun"){
  $ps=parseParams($params);
  $date=$ps["date"];
  $lon=$ps["lon"];
  $cmd="PYTHONPATH=. python util/hmoonsun.py '$date' $lon";
  $hmoonsun=rtrim(shell_exec($cmd));
  if(isBlank($hmoonsun)){$html="Bad date, eg. 24/12/09 00:00:00";}
  else{$html=$hmoonsun;}
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
