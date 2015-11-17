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
$content="";

////////////////////////////////////////////////////////////////////////
//ACTIONS
////////////////////////////////////////////////////////////////////////

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//CLEAR HISTORY OF PLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($plotrm)){
  $outpack=myExec("rm $STATSDIR/${plot}.history/${plot}__${md5sum}.*");
  if($outpack[0]>0){$content.=$outpack[3];$refresh_time="-1";}
  $refresh_time=0;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//CLEAR HISTORY OF PLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($plotclear)){
  $outpack=myExec("rm $STATSDIR/${plot}.history/*");
  if($outpack[0]>0){$content.=$outpack[3];$refresh_time="-1";}
  $plotmd5=rtrim(shell_exec("md5sum $STATSDIR/$plot.conf | cut -f 1 -d ' '"));
  $outpack=myExec("cp $STATSDIR/${plot}.conf $STATSDIR/${plot}.history/${plot}__$plotmd5.conf");
  if($outpack[0]>0){$content.=$outpack[3];$refresh_time="-1";}
  $content.="<script type='text/javascript'>window.close();</script>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//HISTORY OF PLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($plothistory)){
  $numcols=4;
  $width=100/$numcols;
  $refresh_time=-1;
  $output=shell_exec("find $STATSDIR -name '${plot}__*.png'");
  $listplots=preg_split("/\n/",$output);
  $plotlist="<table border=0px><tr><td colspan=$numcols></td>";
  $i=0;
  $md5sums=array("foo");
  foreach($listplots as $ploth){
    if(($i%$numcols)==0){$plotlist.="</tr><tr>";}
    if(isBlank($ploth)){continue;}
    $plotname=rtrim(shell_exec("basename $ploth"));
    $plotname=preg_replace("/\.png/","",$plotname);
    $plotparts=preg_split("/__/",$plotname);
    $plotroot=$plotparts[0];
    $plotmd5=$plotparts[1];
    if(array_search($plotmd5,$md5sums)){continue;}
    else{array_push($md5sums,$plotmd5);}
    if($QADMIN){$replotu="<a href='update.php?replotui&plot=$plotroot&md5sum=$plotmd5'target='_blank'>Replot</a> | <a href='update.php?plotrm&plot=$plotroot&md5sum=$plotmd5'>Delete</a> |";}
$plotlist.=<<<PLOT
  <td width="$width=100%">
  <center>
  $replotu
  <a href="$STATSDIR/$plot.history/${plot}__$plotmd5.out" target="_blank">Out</a> |
  <a href="$STATSDIR/$plot.history/${plot}__$plotmd5.conf" target="_blank">Conf</a>
  <br/>
  <i style="font-size:10px">$plotmd5</i>
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
  
  $clear="";
  if($QADMIN){
    $clear="<a href='update.php?plotclear&plot=$plot'>Clear</a> | ";
  }
  
$content=<<<CONTENT
$clear
<a href="JavaScript:void(null)" onclick="window.close()">Close</a> 
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

  $plotimg="$STATSDIR/${plot}__$md5sum.png";
  if(!file_exists($plotimg)){$plotimg="$STATSDIR/${plot}.history/${plot}__$md5sum.png";}

  $plotconf="$STATSDIR/${plot}.history/${plot}__$md5sum.conf";
  if(!file_exists($plotconf)){$plotconf="$STATSDIR/${plot}.conf";}

  $conf=shell_exec("cat $plotconf");
  $script=shell_exec("cat $STATSDIR/${plot}.py");
  if(!isset($backurl)){$backurl=$target_url;}
$content=<<<CONTENT

  <a href="$backurl">Back</a> | 
  <a href="update.php?plothistory&plot=$plot" target="_blank">History</a> |
  <a href="JavaScript:void(null)" onclick="window.close()">Close</a>
  <br/>

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
	<textarea name="conf" cols=80 rows=10>$conf</textarea>
	<a href="JavaScript:void(null)" onclick="$('#script').toggle('fast',null)">Script</a><br/>
	<textarea id="script" name="script" cols=80 rows=20 style="display:none">$script</textarea>
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
   $fl=fopen("$STATSDIR/$plot.py","w");
   fwrite($fl,$script);
   fclose($fl);

   //SAVE CONFIGURATION
   $fl=fopen("$STATSDIR/$plot.conf","w");
   fwrite($fl,$conf);
   fclose($fl);
   $md5sum=rtrim(shell_exec("md5sum $STATSDIR/$plot.conf | cut -f 1 -d ' '"));

   //PLOT COMMAND
   $cmd="cd $STATSDIR;PYTHONPATH=. MPLCONFIGDIR=/tmp python $plot.py";
   $outpack=myExec($cmd,$SCRATCHDIR);
   if($outpack[0]>0){
     $content.="<a href=$target_url>Back</a><br/>".$outpack[3];
     $refresh_time="-1";
   }else{
     $content.="Successful execution. New id $md5sum...";
     //DEBUGGING
     //$content.="<a href=$target_url>Back</a><br/>".$outpack[3];
     $refresh_time="1";
     $backurl=urlencode($backurl);
     $target_url="update.php?replotui&plot=$plot&md5sum=$md5sum&backurl=$backurl";
     //SAVE OUTPUT
     $fl=fopen("$STATSDIR/$plot.history/${plot}__$md5sum.out","w");
     fwrite($fl,$outpack[1]);
     fwrite($fl,"\n\n".$outpack[2]);
     fclose($fl);
   }
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
    <script src="site/jquery.js"></script>
    <meta http-equiv="refresh" content="$refresh_time;URL=$target_url">
  </head>
  <body>
    $content
  </body>
</html>
CONTENT;
?>
