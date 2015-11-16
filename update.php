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
//HISTORY OF PLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($plothistory)){
  $numcols=4;
  $width=100/$numcols;
  $refresh_time=-1;
  $output=shell_exec("ls -m plots/stats/$plot.history/*.png");
  $listplots=preg_split("/\s*,\s*/",$output);
  $plotlist="<table border=0px><tr><td colspan=$numcols></td>";
  $i=0;
  foreach($listplots as $ploth){
    if(($i%$numcols)==0){$plotlist.="</tr><tr>";}
    if(isBlank($ploth)){continue;}
    $plotname=rtrim(shell_exec("basename $ploth"));
    $plotname=preg_replace("/\.png/","",$plotname);
    $plotparts=preg_split("/__/",$plotname);
    $plotroot=$plotparts[0];
    $plotmd5=$plotparts[1];
    if($QADMIN){$replotu="<a href='update.php?replotui&plot=$plotroot&md5sum=$plotmd5'>Replot</a>,";}
$plotlist.=<<<PLOT
  <td width="$width=100%">
  <center>
  $replotu
  <a href="plots/stats/$plot.history/${plot}__$plotmd5.conf">Conf</a>
  <a href="$ploth" target="_blank">
  <img src="$ploth" width="100%">
  </a>
  </center>
  </td>
PLOT;
    $i++;
  }
  if($i==0){$plotlist.="<i>No plot in history</i>";}
  else{
    $rem=3-$i%3;
    if($rem){$plotlist.="<td colspan=$rem></td></tr>";}
  }
  $plotlist.="</table>";
  
$content=<<<CONTENT
<h2>History of $plot</h2>
$plotlist
CONTENT;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REPLOT UI
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($replotui)){
  if(!$QADMIN){
    echo "You don't have permissions for replotting...";
    $refresh_time=3;
  }else{
  $refresh_time=-1;
  $plotimg="plots/stats/${plot}__$md5sum.png";
  $conf=shell_exec("cat plots/stats/${plot}.history/${plot}__$md5sum.conf");
  $script=shell_exec("cat plots/stats/${plot}.py");
  if(!isset($backurl)){$backurl=$target_url;}
$content=<<<CONTENT

<a href="$backurl">Back</a><br/>

<h2>Replot of $plot</h2>

<table border=1px>
  <tr>
    <td width="50%">
      <a href="$plotimg" target="_blank">
	<img src="$plotimg" width="100%">
      </a>
    </td>
    <td valign="top">
      <form action="update.php" method="post">
	<input type="hidden" name="plot" value="$plot">
	<input type="hidden" name="md5sum" value="$md5sum">
	<input type="hidden" name="backurl" value="$backurl">

	<input type="submit" name="replot" value=replot><br/>
	Configuration:<br/>
	<textarea name="conf" cols=80 rows=20>$conf</textarea>
	Script:<br/>
	<textarea  name="script" cols=80 rows=20>$script</textarea>
      </form>
    </td>
  </tr>

</table>
CONTENT;
  }
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REPLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($replot)){
   $refresh_time=-1;

   //SAVE SCRIPT

   //SAVE CONFIGURATION

   //PLOT
   $target_url="update.php?replotui&plot=$plot&md5sum=$md5sum&backurl=$backurl";
   $cmd="PYTHONPATH=. MPLCONFIGDIR=/tmp python plots/stats/$plot.py";
   echo "Plotting: $cmd<br/>";
   echo "Returning to $target_url...";
   $fl=fopen("/tmp/a.py","w");
   fwrite($fl,$script);
   fclose($fl);
   
   /*
   $out=shell_exec("$cmd &> /tmp/error");
   echo "$out<br/>";
   $content="Replot succesful...";
   $target_url=$target_url."#".$aname;
   echo "Target: $target_url<br/>";
   $refresh_time=1;
   */
   echo "<br/>";
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
      $content.="<a href='$target_url&search=$query_url'>$query</a></li>";
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
