<?php
//======================================================================
//START
//======================================================================
////////////////////////////////////////////////////////////////////////
//LOAD UTILITIES
////////////////////////////////////////////////////////////////////////
require_once("site/util.php");

////////////////////////////////////////////////////////////////////////
//INITIAL CHECKS
////////////////////////////////////////////////////////////////////////
if(!isset($action)){$action="";}
if(!isset($if)){$if="";}
$action_status="";
$action_error="";

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
////////////////////////////////////////////////////////////////////////
//ACTIONS
////////////////////////////////////////////////////////////////////////
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

////////////////////////////////////////////////////////////////////////
//FETCHING EVENTS
////////////////////////////////////////////////////////////////////////
if(!isBlank($action)){

if($action=="fetch"){

  // CHECK IF STATION IS ENABLED
  $sql="select station_receiving from Stations where station_id='$station_id';";
  $result=mysqlCmd($sql);
  $station_receiving=$result[0];
  if($station_receiving<0){
    echo "-1";
    return 0;
  }

  //FETCH QUAKES NOT FETCHED OR FETCHED TOO MUCH TIME AGO
  $results=mysqlCmd("select max(calctime1+calctime2+calctime3) from Quakes");
  $maxtime=$results[0];
  if(isBlank($maxtime)){$maxtime=0;}
  $maxtime=2*$NUMQUAKES*$maxtime;

  $sql="select * from Quakes where astatus+0=0 or (astatus+0>0 and astatus+0<4 and adatetime<>'' and TIME_TO_SEC(TIMEDIFF(NOW(),adatetime))>$maxtime) order by TIME_TO_SEC(TIMEDIFF(NOW(),adatetime)) desc limit $numquakes";

  $quakes=mysqlCmd($sql,$out=1);
  if($quakes==0){
    echo "No quakes available for fecthing.";
    return 0;
  }
  $disprops=array("quakeid","qjd","qlat","qlon","qdepth","qdate","qtime");
  foreach($quakes as $quake){
    foreach($disprops as $prop){
      $$prop=$quake["$prop"];
      echo "$prop='".$quake["$prop"]."',";
    }
    echo "<br/>";
    $sql="update Quakes set astatus='1',stationid='$station_id',adatetime=now() where quakeid='$quakeid';";
    mysqlCmd($sql);
  }
  return 0;
}

////////////////////////////////////////////////////////////////////////
//REPORT END OF ETERNA CALCULATIONS
////////////////////////////////////////////////////////////////////////
else if($action=="report"){
  $sql="update Quakes set astatus='2',stationid='$station_id',calctime1='$deltat',adatetime=now() where quakeid='$quakeid';";
  mysqlCmd($sql);
  return 0;
}

////////////////////////////////////////////////////////////////////////
//REPORTING END OF ANALYSIS
////////////////////////////////////////////////////////////////////////
else if($action=="analysis"){
  $sql="update Quakes set astatus='3',stationid='$station_id',calctime2='$deltat',adatetime=now(),qsignal='$qsignal',qphases='$qphases' where quakeid='$quakeid';";
  mysqlCmd($sql);
  return 0;
}

////////////////////////////////////////////////////////////////////////
//CHECK STATION
////////////////////////////////////////////////////////////////////////
else if($action=="checkstation"){
  $sql="select station_receiving from Stations where station_id='$station_id';";
  $result=mysqlCmd($sql);
  $status=$result[0];
  if($status==0){
    $sql="update Stations set station_status='6',station_statusdate=now() where station_id='$station_id';";
    mysqlCmd($sql);
  }
  if(isBlank($status)){
    $status=-2;
  }
  echo $status;
  return 0;
}

////////////////////////////////////////////////////////////////////////
//TEST DB
////////////////////////////////////////////////////////////////////////
else if($action=="testdb"){
  $sql="select count(quakeid) from Quakes;";
  $result=mysqlCmd($sql);
  echo $result[0];
  return 0;
}

////////////////////////////////////////////////////////////////////////
//CHECK STATION
////////////////////////////////////////////////////////////////////////
else if($action=="submit"){
  $sql="update Quakes set astatus='4',stationid='$station_id',adatetime=now(),calctime3='$deltat' where quakeid='$quakeid';";
  mysqlCmd($sql);
  return 0;
}

////////////////////////////////////////////////////////////////////////
//CHANGE STATION STATUS
////////////////////////////////////////////////////////////////////////
else if($action=="status"){
  $sql="update Stations set station_status=$station_status,station_statusdate=now() where station_id='$station_id';";
  mysqlCmd($sql);
  echo "Status for $station_id changed to $station_status<br/>";
  return 0;
}

////////////////////////////////////////////////////////////////////////
//PREREGISTER STATION
////////////////////////////////////////////////////////////////////////
else if($action=="preregister"){
  $station_dir="stations/.preregister/$station_id";
  if(!is_dir($station_dir)){
    shell_exec("mkdir -p $station_dir");
  }
  $fl=fopen("$station_dir/${station_id}rc","w");
  fwrite($fl,"station_id='$station_id';
station_arch='$station_arch';
station_nproc=$station_nproc;
station_mem=$station_mem;
station_mac='$station_mac';");

  fclose($fl);
  return;
}

////////////////////////////////////////////////////////////////////////
//REMOVE STATION
////////////////////////////////////////////////////////////////////////
else if($action=="remove"){
  if(is_dir("stations/$station_id")){
      echo "<i>Station $station_id removed.</i>";
      // REMOVE FROM DATABASE
      $sql="delete from Stations where station_id='$station_id';";
      mysqlCmd($sql);
      // REMOVE STATION INFORMATION
      shell_exec("mv stations/$station_id stations/.trash");
  }
  $if="activity";
}

////////////////////////////////////////////////////////////////////////
//REGISTER STATION
////////////////////////////////////////////////////////////////////////
else if($action=="register"){
  //CHECK IF MACHINE IS REGISTERED OR PREREGISTERED
  $station_dir="stations/$station_id";
  $station_predir="stations/.preregister/$station_id";
  if(is_dir($station_dir)){
      $action_status="Station already registered. Updating.";
  }else if(is_dir($station_predir)){
    $action_status="Station registered.";
    shell_exec("mv $station_predir $station_dir");
  }else{
    $action_error="Station not installed (preregistered) yet.";
  }

  //CREATING PUBLIC KEY
  $fl=fopen("$station_dir/key.pub","w");
  fwrite($fl,"no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty,command=\"scp -r -d -t ~/tQuakes/\" $station_key");
  fclose($fl);

  //UPDATING STATION IN DATABASE
  $station_receiving=0;
  $conf=parse_ini_file("$station_dir/${station_id}rc");
  foreach(array_keys($conf) as $key){
    $GLOBALS["$key"]=$conf["$key"];
  }
  $sql="insert into Stations (station_id,station_name,station_email,station_arch,station_nproc,station_mem,station_mac,station_receiving) values ('$station_id','$station_name','$station_email','$station_arch','$station_nproc','$station_mem','$station_mac','$station_receiving') on duplicate key update station_name=VALUES(station_name),station_email=VALUES(station_email),station_arch=VALUES(station_arch),station_nproc=VALUES(station_nproc),station_mem=VALUES(station_mem),station_mac=VALUES(station_mac),station_receiving=VALUES(station_receiving);";
  mysqlCmd($sql);
}

else {
  echo "Server responding: ",$DATE;
  return 0;
}
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
////////////////////////////////////////////////////////////////////////
//WEBPAGE
////////////////////////////////////////////////////////////////////////
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
// CHECK FOR STATUS
if($action_status!=""){
$action_status=<<<STATUS
<div style='background:lightblue;padding:10px'>$action_status</div>
STATUS;
}
if($action_error!=""){
$action_error=<<<ERROR
<div style='background:pink;padding:10px'>$action_error</div>
ERROR;
}

// COMMON CONTENT
echo<<<PORTAL
<html>
<head>
<script src="site/jquery.js"></script>
</head>
<body>
  <h1>
    <a href="?">tQuakes</a><br/>
    <i style="font-size:18px">Earthquakes and Tides</i>
  </h1>
<a href="?">Home</a> | 
<a href="?if=download">Download</a> |
<a href="?if=stats">Statistics</a> |
<a href="?if=data">Data Products</a> |
<a href="?if=search">Search</a> |
<a href="?if=activity">Stations Activity</a> |
<a href="?if=register">Register Station</a> 
<!--<a href="update.php">Update</a> |-->
<hr/>
PORTAL;

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//DOWNLOAD
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if($if=="download"){
echo<<<PORTAL
$tQuakes can be downloaded in different forms:
<ul>
<li>
  <b>Calculation station</b>: Install a calculation station and help
  us to analyse a huge database of Earthquakes.  
  <ul>
    <li>
      Installation script for Linux
      clients: <a href="site/install-station.sh">install-station.sh</a>
    </li>
  </ul>
</li>

<li>
  <b>Calculation server</b>: create your own calculation server to run
  custom analysis on custom earthquakes database.  This site is
  running on the server $WEBSERVER.
  <ul>
    <li><a href="$GITREPO">Github repositorty</a>.</li>
  </ul>
</li>

</ul>
PORTAL;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//DATA PRODUCTS
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="data"){

echo<<<PORTAL

One of the most important products of $tQuakes is data. A lot of it.

Data containing information about Earthquakes around the globe (more
specifically in Colombia and South America) and the lunisolar tides
affecting the places where those Earthquakes happened.

Here are some of the available data products from $tQuakes:
<ul>
PORTAL;

//==================================================
//DATABASE
//==================================================
$file="data/sql/Quakes.sql.7z";
$base=rtrim(shell_exec("basename $file"));
$size=round(filesize($file)/1024.0,0);
$time=date("F d Y H:i:s",filemtime($file));
echo<<<PORTAL
<li>
  <b>Earthquakes database:</b> The complete database of Earth quakes
  analysed by $tQuakes.
  <ul>
    <li>File: <a href="$file">$base</a></li>
    <li>Size: $size kB</li>
    <li>Last update: $time</li>
  </ul>
</li>
PORTAL;

//==================================================
//INSTALLATION SCRIPT
//==================================================
$file="data/sql/tQuakes.sh";
$base=rtrim(shell_exec("basename $file"));
$size=round(filesize($file)/1024.0,0);
$time=date("F d Y H:i:s",filemtime($file));
echo<<<PORTAL
<li>
  <b>Earthquakes database installer:</b> Bash script to install
  database in a Linux (debian-like) server.
  <ul>
    <li>File: <a href="$file">$base</a></li>
    <li>Size: $size kB</li>
    <li>Last update: $time</li>
  </ul>
</li>
PORTAL;

//==================================================
//PLOTS
//==================================================
$numcols=4;
$width=100/$numcols;
$output=shell_exec("find $STATSDIR -name '*.png'");
$listplots=preg_split("/\n/",$output);
$plotlist="<li><b>Plots:</b><br/><table border=0px><tr><td colspan=$numcols></td>";
$i=0;
$md5sums=array("foo");
$plotscripts=array();
foreach($listplots as $plot)
{
  if(($i%$numcols)==0){$plotlist.="</tr><tr>";}
  if(isBlank($plot)){continue;}
  $plotname=rtrim(shell_exec("basename $plot"));
  $plotbase=preg_split("/\./",$plotname)[0];
  $plotparts=preg_split("/__/",$plotbase);
  $plotroot=$plotparts[0];
  //print_r($plotscripts);
  //echo array_search($plotroot,$plotscript);
  if(!isBlank(array_search($plotroot,$plotscripts))){
    continue;
  }else{
    //echo "Metiendo $plotroot<br/>";
    array_push($plotscripts,$plotroot);
  }
  //echo "$plotroot<br/>";
  $plotmd5=$plotparts[1];
  if(array_search($plotmd5,$md5sums)){continue;}
  else{array_push($md5sums,$plotmd5);}

  $replot="";
  if($QADMIN){
    $replot="<a href='update.php?replotui&plot=$plotroot&md5sum=$plotmd5' target='_blank'>Replot</a> |";
  }

$plotlist.=<<<PLOT
  <td width="$width=100%" valign="top">
  <center>
  <i>$plotroot</i><br/>
  $replot 
  <a href="$STATSDIR/$plotroot.history/${plotroot}__$plotmd5.conf" target="_blank">Conf</a> |
  <a href="update.php?plothistory&plot=$plotroot" target="_blank">History</a>
  <br/>
  <i style="font-size:10px">$plotmd5</i>
  <a href="$plot" target="_blank">
  <img src="$plot" width="100%">
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
echo "$plotlist</li>";
echo "</ul>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//STATS
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="stats"){
  
  $statlog="$SCRATCHDIR/stats.log";
  if(file_exists($statlog)){shell_exec("cp $statlog $statlog.prev");}
  $numquakes=mysqlCmd("select count(quakeid) from Quakes");
  $numfetched=mysqlCmd("select count(quakeid) from Quakes where astatus+0>0;");
  $perfetched=round($numfetched[0]/(1.0*$numquakes[0])*100,2);
  $numanalysed=mysqlCmd("select count(quakeid) from Quakes where astatus+0>0 and astatus+0<4;");
  $numsubmit=mysqlCmd("select count(quakeid) from Quakes where astatus+0=4;");
  $persubmit=round($numsubmit[0]/(1.0*$numquakes[0])*100,2);
  $firstquake=mysqlCmd("select adatetime from Quakes limit 1;");
  $tfirst=$firstquake[0];
  $lastquake=mysqlCmd("select max(adatetime) from Quakes where adatetime<>'';");
  $elapsed=mysqlCmd("select TIMEDIFF(max(adatetime),'$tfirst') from Quakes where adatetime<>'';");
  $elapsedsecs=mysqlCmd("select TIME_TO_SEC(TIMEDIFF(max(adatetime),'$tfirst')) from Quakes where adatetime<>'';");
  $perquake=round($elapsedsecs[0]/$numsubmit[0],2);
  $pending=round(($numquakes[0]-$numsubmit[0])*$perquake,0);
  $projectedend=mysqlCmd("select DATE_ADD(max(adatetime),INTERVAL $pending SECOND) from Quakes where adatetime<>''");
  $results=mysqlCmd("select avg(calctime1) from Quakes where calctime1<>''");$avgcalc1=round($results[0],2);
  $results=mysqlCmd("select avg(calctime2) from Quakes where calctime2<>''");$avgcalc2=round($results[0],2);
  $results=mysqlCmd("select avg(calctime3) from Quakes where calctime3<>''");$avgcalc3=round($results[0],2);
  $avgtot=$avgcalc1+$avgcalc2+$avgcalc3;
  $speedup=round($avgtot/$perquake,3);
  $singlespeedup=round(($avgcalc1+$avgcalc2)/$perquake,3);
									    
$stats=<<<STAT
<p>
  <ul>
    <li>
      <b>Number of Earthquakes in database</b>: $numquakes[0]
    </li>
    <li>
      <b>Fetched Earthquakes</b>: $numfetched[0] [ $perfetched% ]
    </li>
    <li>
      <b>Earthquakes being processed</b>: $numanalysed[0]
    </li>
    <li>
      <b>Submitted Earthquakes</b>: $numsubmit[0] [ $persubmit% ]
    </li>
    <li>
      <b>Time of start</b>: $firstquake[0]
    </li>
    <li>
      <b>Time of last status</b>: $lastquake[0]
    </li>
    <li>
      <b>Elapsed time</b>: $elapsed[0] [ $perquake secs/earthquake ]
    </li>
    <li>
      <b>Average ETERNA time</b>: $avgcalc1
    </li>
    <li>
      <b>Average Analysis time</b>: $avgcalc2
    </li>
    <li>
      <b>Average Submission time</b>: $avgcalc3
    </li>
    <li>
      <b>Average time per quake</b>: $avgtot
    </li>
    <li>
      <b>Speed-up</b>: Distributed: <i style='color:red'>$speedup</i>, Single: <i style='color:red'>$singlespeedup</i>
    </li>
    <li>
      <b>Estimated remaining time</b>: $pending seconds
    </li>
    <li>
      <b>Estimated end date</b>: $projectedend[0]
    </li>
  </ul>
</p>
STAT;

   $fl=fopen("$SCRATCHDIR/stats.log","w");
   fwrite($fl,"<html><body>$DATE<br/>$stats</body></html>");
   fclose($fl);

   echo $stats;
   echo "<a href=$SCRATCHDIR/stats.log.prev target=_blank>Previous</a> | <a href=$SCRATCHDIR/stats.log target=_blank>Present</a>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//SEARCH
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="search"){

  // INPUT
  if(isBlank($offset)){$offset=0;}
  if(isBlank($limit)){$limit=10;}
  if(isBlank($search)){$searchdb="quakeid<>''";} 
  else{$searchdb="quakeid<>'' and $search";}
  $search_url=urlencode($search);

  // SAVE SEARCH HISTORY
  $fl=fopen("log/history.log","a");
  fwrite($fl,"$DATE;;$searchtxt;;$search\n");
  fclose($fl);

  // SEARCH
  $result=mysqlCmd("select count(quakeid) from Quakes where $searchdb;");
  $numquakes=$result[0];
  if($limit>$numquakes){$limitdb=$numquakes;}
  else{$limitdb=$limit;}
  $quakes=mysqlCmd("select * from Quakes where $searchdb limit $offset,$limitdb;",$qout=1);

  // GET NEXT
  $offset_prev=$offset-$limit;
  if($offset_prev<0){$offset_prev=1;}
  $offset_next=$offset+$limit;
  if($offset_next>$numquakes){$offset_next=$numquakes-$limit_next;}

  $limit_prev=$limit;
  if(($offset_next+$limit)<=$numquakes){$limit_next=$limit;}
  else{$limit_next=$numquakes-$offset_next;}
  
  $end=$offset+$limit-1;
  $offset_all=$numquakes-$limit;

  // CONTROL BUTTONS
  $control=<<<CONTROL
<div style="font-size:10px;padding:10px;">
<a href="?if=search&search=$search_url&offset=1&limit=$limit"><<</a> 
<a href="?if=search&search=$search_url&offset=$offset_prev&limit=$limit_prev">Prev</a> ...
<a href="?if=search&search=$search_url&offset=$offset_next&limit=$limit_next">Next</a>
<a href="?if=search&search=$search_url&offset=$offset_all&limit=$limit">>></a> 
</div>
CONTROL;

  //EXAMPLES
  $examples_cont="<div id='examples' style='background:pink;padding:10px;display:none'>Examples:<ul>";
  $examples_set=searchExamples();
  $i=$examples_set[0];
  $examples=$examples_set[1];
  $examples_txt=$examples_set[2];
  $examples_url=$examples_set[3];
  for($j=0;$j<=$i;$j++){
    $examples_txt_url=urlencode($examples_txt[$j]);
$examples_cont.=<<<EXAMPLES
  <li>$examples_txt[$j]:<br/>
  <a href="index.php?if=search&search=$examples_url[$j]&searchtxt=$examples_txt_url">$examples[$j]</a>
EXAMPLES;
  }
  $examples_cont.="</ul></div>";

  // TABLE HEADER
echo<<<TABLE
<form action="index.php" method=get>
<table>
  <tr>
    <td>Description of search:</td>
    <td><input type="text" name="searchtxt" size="50" value="$searchtxt"></td>
  </tr>
  <tr>
    <td valign="top">Search:<br/>
      <a style="font-size:10px" href="JavaScript:void(null)" onclick="$('#examples').toggle('fast',null)">
	Examples
      </a>,
      <a style="font-size:10px" href="update.php?history">History</a>
    </td>
    <td><input type="text" name="search" size="100" value="$search"></td>
  </tr>
  <tr>
    <td>Number of quakes:</td>
    <td><input type="text" name="limit" value=$limit></td>
  </tr>
  <tr>
    <td colspan=2><input type="submit" name="if" value="search"></td>
  </tr>
</table>
$examples_cont
</form>

<center>
  <h4>Quakes $offset-$end ($limit/$numquakes)</h4>
$control
<table border=1px style="font-size:12px">
<tr>
  <td>Num.</td>
  <td>Quake id.</td>
  <td>Status</td>
  <td>Lat.,Lon.</td>
  <td>Depth</td>
  <td>Date/Time</td>
  <td>M<sub>l</sub></td>
  <td>Location</td>
</tr>
TABLE;

  $i=$offset;
  foreach($quakes as $quake){
    foreach(array_keys($quake) as $key){
      $$key=$quake["$key"];
    }
    $quake_status_txt=$QUAKE_STATUS[$astatus];
    $departamento=preg_replace("/_/"," ",$departamento);
    $municipio=preg_replace("/_/"," ",$municipio);

echo<<<TABLE
  <tr>
    <td>$i</td>
    <td><a href="?if=quake&quakeid=$quakeid">$quakeid</a></td>
    <td>$quake_status_txt</td>
    <td>$qlat,$qlon</td>
    <td>$qdepth</td>
    <td>$qdatetime</td>
    <td>$Ml</td>
    <td>$municipio, $departamento</td>
  </tr>
TABLE;

    $i++;
  }
  echo "</table>$control</center>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//STATION
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="station"){
  $result=mysqlCmd("select * from Stations where station_id='$station_id'",$qout=1);
  $station=$result[0];
  echo "<h3>Station $station_id</h3><ul>";
  foreach(array_keys($station) as $key){
    if(preg_match("/^\d+$/",$key)){continue;}
    $value=$station["$key"];
    echo "<li><b>$key</b>: $value</li>";
  }
  echo "</ul>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//QUAKE
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="quake"){
  
  // RECOVER QUAKE INFO
  $result=mysqlCmd("select * from Quakes where quakeid='$quakeid'",$qout=1);
  $quake=$result[0];
  
  $fullinfo="";
  $basicinfo="";
  foreach(array_keys($quake) as $key){
    if(preg_match("/^\d+$/",$key)){continue;}
    $value=$$key=$quake["$key"];
    $fullinfo.="<li><b>$key</b>: $value</li>";
  }

  
  // BASIC INFO
  $departamento=preg_replace("/_/"," ",$departamento);
  $municipio=preg_replace("/_/"," ",$municipio);
  $quake_status_txt=$QUAKE_STATUS[$astatus];
$basicinfo.=<<<BASIC
  <li><b>Date and time</b>: $qdatetime</li>
  <li><b>Location</b>: $municipio ($departamento)</li>
  <li><b>Geographic position</b>: lat. $qlat deg., lon. $qlon deg.</li>
  <li><b>Depth</b>: $qdepth km</li>
  <li><b>Status</b>: $quake_status_txt.</li>
  <li><b>Station</b>: $stationid.</li>
BASIC;
  
  // DOWNLOAD
  $dirquakes="$HOMEDIR/$TQUSER/tQuakes/";
  if(file_exists($dirquakes."$quakeid-eterna.tar.7z")){

    //REMOVE PREVIOUS DOWNLOAD QUAKES
    //shell_exec("rm -r $SCRATCHDIR/*"); //ONLY IF YOU WANT TO PRESERVE

    //CREATE QUAKE ID
    $quakedir="$SCRATCHDIR/$quakeid";
    if(!is_dir("$quakedir") or isset($replotall) or 0){
      echo "<i>Creating directory for $quakeid...</i><br/>";
      shell_exec("mkdir -p $quakedir/");
      shell_exec("cp -rf $dirquakes/$quakeid-* $quakedir/");
      
      // ZIP ALL FILES
      shell_exec("cd $quakedir;p7zip -d $quakeid-eterna.tar.7z");
      shell_exec("cd $quakedir;p7zip -d $quakeid-analysis.tar.7z");
      shell_exec("cd scratch/$SESSID;tar cf $quakeid.tar $quakeid/$quakeid-*");
      
      // UNZIP ALL FILES
      shell_exec("cd $quakedir;tar xf $quakeid-eterna.tar");
      shell_exec("cd $quakedir;tar xf $quakeid-analysis.tar");

      // COPY AND PLOTTING SCRIPTS
      shell_exec("cd $quakedir;rm -rf *.py");
      shell_exec("cd $quakedir;for plot in ../../../plots/quakes/*.py;do ln -s \$plot;done");
      shell_exec("for plot in $quakedir/*.py;do PYTHONPATH=. MPLCONFIGDIR=/tmp python \$plot;done");
    }
    $size_eterna=round(filesize("$quakedir/$quakeid-eterna.tar")/1024.0,0);
    $size_analysis=round(filesize("$quakedir/$quakeid-analysis.tar")/1024.0,0);
    $size_full=round(filesize("$SCRATCHDIR/$quakeid.tar")/1024.0,0);
    
    // PLOTS
    $output=shell_exec("ls -m $quakedir/*.png");
    $listplots=preg_split("/\s*,\s*/",$output);
    foreach($listplots as $plot){
      $plotname=rtrim(shell_exec("basename $plot"));
      $plotbase=preg_split("/\./",$plotname)[0];
$plots.=<<<PLOT
<li><b>Plot</b>:
  <ul>
    <li><a name="$plotbase">File</a>: <a href="$plot">$plotname</a></li>
    <li>Preview:<br/>
      <a href="$plot" target="_blank">
	<img src="$plot" width="400px">
      </a>
    </li>
    <li><a href="update.php?replot&plot=$plot">Replot</a></li>
  </ul>
PLOT;
    }

    // LIST
$download=<<<DOWN
  <li><b>Eterna results: </b><a href="$SCRATCHDIR/$quakeid/$quakeid-eterna.tar">$quakeid-eterna.tar</a> ($size_eterna kB)</li>
  <li><b>Fourier transform: </b><a href="$SCRATCHDIR/$quakeid/$quakeid-analysis.tar">$quakeid-analysis.tar</a> ($size_analysis kB)</li>
  <li><b>Full results: </b><a href="$SCRATCHDIR/$quakeid.tar">$quakeid.tar</a> ($size_full kB)
DOWN;
  }else{
    $download="(No download available)";
  }

  // DISPLAY INFO
  $referer=$_SERVER["HTTP_REFERER"];
echo<<<QUAKE
<a href="$referer">Back</a> |
<a href="index.php?if=quake&quakeid=$quakeid&replotall">Replot all</a>
<h3>Earthquake $quakeid</h3>

<h4>Basic information</h4>
<ul>
  $basicinfo
</ul>

<h4>Download</h4>
<ul>
  $download
</ul>

<h4>Plots</h4>
<ul>
  $plots
</ul>

<h4>Full information</h4>
<ul>
  $fullinfo
</ul>
QUAKE;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//ACTIVITY
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="activity"){
  $stationlog="$SCRATCHDIR/stations.log";
  if(file_exists($stationlog)){shell_exec("cp $stationlog $stationlog.prev");}
  $stations=mysqlCmd("select * from Stations",$qout=1);
  $table="";

$table.=<<<TABLE
<table border=1px>
<tr>
  <td>Name</td>
  <td>Station Id.</td>
  <td>Fetched<br/>(time ETERNA)</td>
  <td>Analysing<br/>(time analysis)</td>
  <td>Completed<br/>(time submit)</td>
  <td>Time avg.</td>
  <td>Score</td>
  <td>Status</td>
  <td>Last update</td>
</tr>
TABLE;

 $results=mysqlCmd("select count(quakeid) from Quakes");
 $totquakes=$results[0];
 $totanalysing=0;
 $totnumquakes=0;
 $totfetched=0;
 $numstations=0;
 $timetotavg=mysqlCmd("select avg(calctime1+calctime2+calctime3) from Quakes where calctime3<>'';");
 $avgcalctime=0;
 $avgscore=0;
 $iavg=0;
  foreach($stations as $station){
    foreach(array_keys($station) as $key){
      $$key=$station["$key"];
    }
    $sqlbase="index.php?if=search&search=";
    $urlfetched=urlencode("stationid='$station_id' and astatus+0>=0");
    $sqlfetched="$sqlbase$urlfetched";
    $urlanalysing=urlencode("stationid='$station_id' and astatus+0>0 and astatus+0<4");
    $sqlanalysing="$sqlbase$urlanalysing";
    $urlnumquakes=urlencode("stationid='$station_id' and astatus+0=4");
    $sqlnumquakes="$sqlbase$urlnumquakes";

    $station_status_txt=$STATION_STATUS[$station_status];
    $calctime1=mysqlCmd("select avg(calctime1) from Quakes where stationid='$station_id' and calctime1<>'';");
    $calctime2=mysqlCmd("select avg(calctime2) from Quakes where stationid='$station_id' and calctime2<>'';");
    $calctime3=mysqlCmd("select avg(calctime3) from Quakes where stationid='$station_id' and calctime3<>'';");

    $numquakes=mysqlCmd("select count(quakeid),avg(calctime3) from Quakes where stationid='$station_id' and astatus='4';");
    $fetched=mysqlCmd("select count(quakeid),avg(calctime1) from Quakes where stationid='$station_id' and astatus+0>0;");
    $analysing=mysqlCmd("select count(quakeid),avg(calctime2) from Quakes where stationid='$station_id' and astatus+0>0 and astatus+0<4;");
    mysqlCmd("update Stations set station_numquakes='$numquakes[0]' where station_id='$station_id';");

    $totnumquakes+=$numquakes[0];
    $totanalysing+=$analysing[0];
    $totfetched+=$fetched[0];

    $timeeterna=round($calctime1[0],2);
    $timeanalysis=round($calctime2[0],2);
    $timesubmission=round($calctime3[0],2);

    $timeavg=round($timeeterna+$timeanalysis+$timesubmission,2);
    $score=round($timetotavg[0]/$timeavg,2);
    $scorecolor="blue";
    if($fetched[0]>0){
      $avgcalctime+=$timeavg;
      $avgscore+=$score;
      $iavg++;
    }
    
    if($score<1){$scorecolor="red";}

$table.=<<<TABLE
  <tr>
    <td><a href="?if=station&station_id=$station_id">$station_name</a></td>
    <td><a href="?if=register&station_id=$station_id&station_name=$station_name&station_email=$station_email">$station_id</td>
    <td><a href="$sqlfetched">$fetched[0]</a>  ($timeeterna)</td>
    <td><a href="$sqlanalysing">$analysing[0]</a> ($timeanalysis)</td>
    <td><a href="$sqlnumquakes">$numquakes[0]</a> ($timesubmission)</td>
    <td>$timeavg</td>
    <td><span style=color:$scorecolor>$score</span></td>
    <td>$station_status_txt</td>
    <td>$station_statusdate</td>
  </tr>
TABLE;
 $numstations+=1;

  }

  $avgcalctime=round($avgcalctime/$iavg,2);
  $avgscore=round($avgscore/$iavg,2);
  $fracfetched=round($totfetched/$totquakes*100,2);
  $fracanalysing=round($totanalysing/$totquakes*100,2);
  $fracnumquakes=round($totnumquakes/$totquakes*100,2);

$table.=<<<TABLE
   <tr>
     <td>Num. stations : $numstations</td>
     <td style=text-align:right>TOTALS</td>
     <td>$totfetched</td>
     <td>$totanalysing</td>
     <td>$totnumquakes</td>
     <td>$avgcalctime</td>
     <td>$avgscore</td>
     <td colspan=2></td>
   </tr>
   <tr>
     <td colspan=2 style=text-align:right>TOTALS (%)</td>
     <td>$fracfetched%</td>
     <td>$fracanalysing%</td>
     <td>$fracnumquakes%</td>
     <td colspan=4></td>
   </tr>
</table>
TABLE;

   $fl=fopen($stationlog,"w");
   fwrite($fl,"<html><body>$DATE<br/>$table</body></html>");
   fclose($fl);

   echo $table;
   echo "<a href=$stationlog.prev target=_blank>Previous</a> | <a href=$stationlog target=_blank>Present</a>";

}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REGISTER
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="register"){
  $delete="";
  if(!isset($station_name)){$station_name="SEAP UdeA";}
  if(!isset($station_email)){$station_email="seapudea@gmail.com";}
  if(isset($station_id)){
	$station_key=shell_exec("cat stations/$station_id/key.pub");
	$delete="<input type=submit name=action value=remove>";
  }
echo<<<PORTAL
$action_status
$action_error
<form action="index.php" method="post" enctype="multipart/form-data" accept-charset="utf-8">
  <input type=hidden name=if value=register>
  <table border=0px>
    <tr>
      <td valign=top>Station ID:</td>
      <td><input type=text name=station_id maxlength=14 size=8 value=$station_id></td>
    </tr>
    <tr>
      <td valign=top>Name:</td>
      <td><input type=text name=station_name value="$station_name"></td>
    </tr>
    <tr>
      <td valign=top>E-mail:</td>
      <td><input type=text name=station_email value="$station_email"></td>
    </tr>
    <tr>
      <td valign=top>Upload key:</td>
      <td><textarea name=station_key cols=60 rows=10>$station_key</textarea></td>
    </tr>
    <tr>
      <td valign=top colspan=2>
	<input type=submit name=action value=register> $delete
      </td>
    </tr>
  </table>
</form>
PORTAL;
}
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//WELCOME MESSAGE
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else{
echo<<<PORTAL
<p>
  Welcome to the website of $tQuakes, a project of the Solar, Earth and Planetary Physics
Group (SEAP) of the University of Antioquia (Medellin, Colombia) in
collaboration with the National University in Colombia.
</p>
<p>
$tQuakes (Earthquakes
and Tides) is a tool intended to explore the relationship between the
lunisolar tides and the triggering of earthquakes.
</p>
<h2>References</h2>
PORTAL;
require_once("site/references.php");
}
//======================================================================
//END
//======================================================================
?>
<?php
echo<<<FOOTER
<hr/>
<i style="font-size:12px">
  Developed by Gloria Moncayo, Jorge I. Zuluaga & Gaspar Monsalve (2015), sessid: $SESSID
</i>
</body></html>
FOOTER;
?>
