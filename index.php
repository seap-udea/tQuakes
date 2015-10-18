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
  $sql="select * from Quakes where astatus+0=0 limit $numquakes;";
  $quakes=mysqlCmd($sql,$out=1);
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
  echo $result[0];
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
  $sql="update Quakes set astatus='4',stationid='$station_id',adatetime=now() where quakeid='$quakeid';";
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

  //INSTALLING PUBLIC KEY
  shell_exec("(echo;cat $station_dir/key.pub) >> stations/authorized_keys");

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
<aa href="?if=search">Search</a> |
<a href="?if=activity">Stations Activity</a> |
<a href="?if=register">Register Station</a> | 
<aa href="?if=calculate">Calculate</a> 
|
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
if($if=="data"){

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
$output=shell_exec("ls -m plots/*.png");
$listplots=preg_split("/\s*,\s*/",$output);
foreach($listplots as $plot)
{
   $plotname=rtrim(shell_exec("basename $plot"));
   $plotbase=preg_split("/\./",$plotname)[0];

echo<<<PLOT
<li><b>Plot</b>:
  <ul>
    <li><a name="$plotbase">File</a>: <a href="$plot">$plotname</a></li>
    <li>Preview:<br/>
      <a href="$plot">
	<img src="$plot" width="400px">
      </a>
    </li>
    <li><a href="update.php?replot&plot=$plotname&aname=$plotbase">Replot</a></li>
  </ul>


PLOT;
}

echo "</ul>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//DOWNLOAD
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="stats"){

  $numquakes=mysqlCmd("select count(quakeid) from Quakes");
  $numfetched=mysqlCmd("select count(quakeid) from Quakes where astatus+0>0;");
  $perfetched=round($numfetched[0]/(1.0*$numquakes[0])*100,1);
  $numanalysed=mysqlCmd("select count(quakeid) from Quakes where astatus+0>0 and astatus+0<4;");
  $numsubmit=mysqlCmd("select count(quakeid) from Quakes where astatus+0=4;");
  $persubmit=round($numsubmit[0]/(1.0*$numquakes[0])*100,1);

echo<<<PORTAL
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
  </ul>
</p>
PORTAL;
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
//ACTIVITY
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="activity"){
  $stations=mysqlCmd("select * from Stations",$qout=1);
echo<<<TABLE
<table border=1px>
<tr>
  <td>Name</td>
  <td>Station Id.</td>
  <td>Num. quakes</td>
  <td>Status</td>
  <td>Last update</td>
</tr>
TABLE;
  foreach($stations as $station){
    foreach(array_keys($station) as $key){
      $$key=$station["$key"];
    }
    $station_status_txt=$STATION_STATUS[$station_status];
    $numquakes=mysqlCmd("select count(quakeid) from Quakes where stationid='$station_id';");
    mysqlCmd("update Stations set station_numquakes='$numquakes' where station_id='$station_id';");
    
echo<<<TABLE
  <tr>
    <td><a href="?if=station&station_id=$station_id">$station_name</a></td>
    <td>$station_id</td>
    <td>$numquakes[0]</td>
    <td>$station_status_txt</td>
    <td>$station_statusdate</td>
  </tr>
TABLE;


  }
  echo "</table>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REGISTER
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="register"){
  if(!isset($station_name)){$station_name="SEAP UdeA";}
  if(!isset($station_email)){$station_email="seapudea@gmail.com";}
echo<<<PORTAL
$action_status
$action_error
<form action="index.php" method="post" enctype="multipart/form-data" accept-charset="utf-8">
  <input type=hidden name=if value=register>
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
	<input type=submit name=action value=register>
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
<hr/>
<i style="font-size:12px">
  Developed by Gloria Moncayo, Jorge I. Zuluaga & Gaspar Monsalve (2015)
</i>
</body></html>
