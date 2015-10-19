<?php
//======================================================================
//START
//======================================================================
////////////////////////////////////////////////////////////////////////
//LOAD UTILITIES
////////////////////////////////////////////////////////////////////////
require_once("site/util.php");
$refresh_time=1;
$target_url=$_SERVER["HTTP_REFERER"];
$content="Refreshing";

////////////////////////////////////////////////////////////////////////
//ACTIONS
////////////////////////////////////////////////////////////////////////

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REPLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($replot)){
   $name=preg_split("/\./",$plot)[0];
   $cmd="PYTHONPATH=. MPLCONFIGDIR=/tmp python plots/stats/$name.py";
   echo "Plotting: $cmd<br/>";
   $out=shell_exec("PYTHONPATH=. MPLCONFIGDIR=/tmp python plots/stats/$name.py &> /tmp/error");
   echo "$out<br/>";
   $content="Replot succesful...";
   $target_url=$target_url."#".$aname;
   echo "Target: $target_url<br/>";
   $refresh_time=1;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REPLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($replot2)){
   $name=preg_split("/\./",$plot)[0];
   $parts=preg_split("/\//",$name);
   $aname=$parts[count($parts)-1];
   $cmd="PYTHONPATH=. MPLCONFIGDIR=/tmp python plots/stats/$name.py";
   echo "Plotting: $cmd<br/>";
   $out=shell_exec("PYTHONPATH=. MPLCONFIGDIR=/tmp python $name.py &> /tmp/error");
   echo "$out<br/>";
   $content="Replot succesful...";
   $target_url=$target_url."#".$aname;
   echo "Target: $target_url<br/>";
   $refresh_time=1;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//SEARCH HISTORY
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($history)){
  $histfile="log/history.log";
  if(file_exists($histfile)){
    $lines=file($histfile);
    $content="<h2>Search History</h2><a href=$target_url>Back</a><ul>";
    foreach($lines as $line){
      if(isBlank($line)){continue;}
      $parts=preg_split("/;;/",$line);
      $date=$parts[0];
      $explanation=$parts[1];
      $query=$parts[2];
      $query_url=urlencode($query);
      if(!isBlank($explanation)){
	$content.="<li>$date<br/>$explanation<br/>";
      }else{$content.="<li>$date<br/>";}
      $content.="<a href='$query_url'>$query</a></li>";
    }
    $content.="</ul>";
    $refresh_time=-1;
  }else{
    echo "No history";
  }
}
?>

<?php

//======================================================================
//START
//======================================================================
echo<<<CONTENT
<html>
  <head>
    <meta http-equiv="refresh" content="$refresh_time;URL=$target_url">
  </head>
  <body>
    $content
  </body>
</html>
CONTENT;
?>
