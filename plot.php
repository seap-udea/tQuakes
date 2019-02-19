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
if(!isset($dir)){$dir=$STATSDIR;}

////////////////////////////////////////////////////////////////////////
//ACTIONS
////////////////////////////////////////////////////////////////////////

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//CLEAR HISTORY OF PLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($plotrm)){
  $outpack=myExec("if ! mv -f $dir/${plot}.history/${plot}__${md5sum}.* $PLOTHELL;then mv $dir/${plot}__${md5sum}.* $PLOTHELL;fi");
  if($outpack[0]>0){$content.=$outpack[3];$refresh_time="-1";}
  else{$refresh_time=0;}
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//CLEAR HISTORY OF PLOT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($plotclear)){
  $outpack=myExec("mv -f $dir/${plot}.history/* $PLOTHELL/");
  if($outpack[0]>0){$content.=$outpack[3];$refresh_time="-1";}
  $plotmd5=rtrim(shell_exec("md5sum $dir/$plot.conf | cut -f 1 -d ' '"));
  $outpack=myExec("cp $dir/${plot}.conf $dir/${plot}.history/${plot}__$plotmd5.conf");
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
  $output=shell_exec("find $dir -name '${plot}__*.png'");
  $listplots=preg_split("/\n/",$output);
  $plotlist="";
  $i=0;
  $md5sums=array("foo");
  foreach($listplots as $ploth){
    if(($i%$numcols)==0){$plotlist.="";}
    if(isBlank($ploth)){continue;}
    $plotname=rtrim(shell_exec("basename $ploth"));
    $plotname=preg_replace("/\.png/","",$plotname);
    $plotparts=preg_split("/__/",$plotname);
    $plotroot=$plotparts[0];
    $plotmd5=$plotparts[1];
    if(array_search($plotmd5,$md5sums)){continue;}
    else{array_push($md5sums,$plotmd5);}
    $confile="$dir/$plotroot.history/$plotname.conf";
    $conf=parse_ini_file($confile);
    $description="No description";
    if(isset($conf["description"])){
      $description=$conf["description"];
    }
    $time=filemtime($confile);
    $datetime=date ("F d Y H:i:s.",$time);

$plotlist.=<<<PLOT

  <figure class="plot">
    <a href="$ploth" target="_blank">
      <img class="plot" src="$ploth">
    </a>
    <figcaption class="plot">
      $description<br/>[PID: $plotmd5, DATE: $datetime]<br/>
      <span class="level2">
	<a href='plot.php?dir=$dir&replotui&plot=$plotroot&md5sum=$plotmd5'target='_blank'>Replot</a> | 
      </span>
      <span class="level3">
	<a href='plot.php?dir=$dir&plotrm&plot=$plotroot&md5sum=$plotmd5'>Delete</a> | 
      </span>
      <a href="$dir/$plot.history/${plot}__$plotmd5.out" target="_blank">Out</a> | 
      <a href="$dir/$plot.history/${plot}__$plotmd5.conf" target="_blank">Conf</a>
    </figcaption>
  </figure>

PLOT;
    $i++;
  }
  if($i==0){$plotlist.="<i>No plot in history</i>";}
  else{
    $rem=3-$i%3;
    if($rem){$plotlist.="<td colspan=$rem></td></tr>";}
  }
  $plotlist.="";
  
  $clear="";
  if($QPERM){
    $clear="<a href='plot.php?dir=$dir&plotclear&plot=$plot'>Clear</a> | ";
  }
  
$content=<<<CONTENT
<span class="level3"><a href='plot.php?dir=$dir&plotclear&plot=$plot'>Clear</a> | </span>
<a href="JavaScript:void(null)" onclick="window.close()">Close</a> 
<h2>History of $plot</h2>
$plotlist
CONTENT;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REPLOT UI
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($replotui)){
  if(!$QPERM){
    echo "You don't have permissions for replotting...";
    $refresh_time=3;
  }else{
  $refresh_time=-1;

  $plotimg="$dir/${plot}__$md5sum.png";
  if(!file_exists($plotimg)){$plotimg="$dir/${plot}.history/${plot}__$md5sum.png";}

  $plotconf="$dir/${plot}.history/${plot}__$md5sum.conf";
  if(!file_exists($plotconf)){$plotconf="$dir/${plot}.conf";}

  $conf=shell_exec("cat $plotconf");
  $script=shell_exec("cat $dir/${plot}.py");
  $config=parse_ini_file("$plotconf");
  if(isset($config["description"])){
    $description=$config["description"];
  }else{
    $description="No description";
  }

  if(!isset($backurl)){$backurl=$target_url;}

$content=<<<CONTENT

  <a href="$backurl">Back</a> | 
  <a href="plot.php?dir=$dir&plothistory&plot=$plot" target="_blank">History</a> |
  <a href="JavaScript:void(null)" onclick="window.close()">Close</a>
  <br/>

<h2>Replot of $plot</h2>

<table border=0px cellspacing=0px>
  <tr>
    <td width="50%">
	<figure>
	  <figcaption>
	    $description
	  </figcaption>
	  <a href="$plotimg" target="_blank">
	    <img src="$plotimg" width="100%">
	  </a>
	</figure>
    </td>
    <td valign="top">
      <form action="plot.php" method="post">
	<input type="hidden" name="plot" value="$plot">
	<input type="hidden" name="md5sum" value="$md5sum">
	<input type="hidden" name="backurl" value="$backurl">
	<input type="hidden" name="dir" value="$dir">

	<input type="submit" name="replot" value=replot><br/>
	<p></p>
	<div class="level2">
	  <a href="JavaScript:void(null)" onclick="$('#configuration').toggle('fast',null)">Configuracion</a><br/>
	  <textarea id="configuration" name="conf" cols=90 rows=50 style="display:block">$conf</textarea><br/>
	</div>
	<p></p>
	<div class="level3">
	  <a href="JavaScript:void(null)" onclick="$('#script').toggle('fast',null)">Script</a><br/>
	  <textarea id="script" name="script" cols=90 rows=50 style="display:none">$script</textarea>
	</div>
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
   $fl=fopen("$dir/$plot.py","w");
   fwrite($fl,$script);
   fclose($fl);

   //SAVE CONFIGURATION
   $fl=fopen("$dir/$plot.conf","w");
   fwrite($fl,$conf);
   fclose($fl);
   $md5sum=rtrim(shell_exec("md5sum $dir/$plot.conf | cut -f 1 -d ' '"));
   $md5sum=substr($md5sum,0,5);

   //PLOT COMMAND
   $cmd="cd $dir;PYTHONPATH=. MPLCONFIGDIR=/tmp python $plot.py";
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
     $target_url="plot.php?dir=$dir&replotui&plot=$plot&md5sum=$md5sum&backurl=$backurl";
     //SAVE OUTPUT
     $fl=fopen("$dir/$plot.history/${plot}__$md5sum.out","w");
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

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//PLOT HELL
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(isset($plothell)){
  $refresh_time=-1;
  $output=shell_exec("find $PLOTHELL -name '*__*.png'");
  $listpng=preg_split("/\n/",$output);
  $content.="<h2>Plot hell</h2>";
  foreach($listpng as $png){
    $basename=shell_exec("basename $png");
    $plotbase=preg_split("/\./",$basename)[0];
    
    $conf="$PLOTHELL/$plotbase.conf";
    if(!file_exists($conf)){
      $conf="JavaScript:void(null)";
    }

    if(isBlank($png)){continue;}
$content.=<<<C
<figure style="float:left;width:20%">
  <a href="$png" target="_blank">
    <img src="$png" width="100%">
  </a>
  <figcaption>
  <a href=$conf target=_blank>$basename</a>
  </figcaption>
</figure>
C;
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
    <link rel="stylesheet" type="text/css" href="site/tquakes.css"/>
    <style>
      $PERMCSS
    </style>
    <meta http-equiv="refresh" content="$refresh_time;URL=$target_url">
  </head>
  <body>
    <header>
      <a href=$WEBSERVER><img class="tquakes" src="img/tquakes.png" style="height:100%"/></a>
      <img class="logogroup" src="img/LogoSEAP-White.jpg" align="middle"/>
    </header>
    $content
  </body>
</html>
CONTENT;
?>
