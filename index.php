<?php
//======================================================================
//START
//======================================================================
////////////////////////////////////////////////////////////////////////
//CONFIGURATION
////////////////////////////////////////////////////////////////////////
$USER="tquakes";
$PASSWORD="quakes2015";
$DATABASE="tQuakes";

$conf=parse_ini_file("configuration");
foreach(array_keys($conf) as $key){
  $GLOBALS["$key"]=$conf["$key"];
}

////////////////////////////////////////////////////////////////////////
//ROUTINES
////////////////////////////////////////////////////////////////////////
function sqlNoblank($out)
{
  $res=mysqli_fetch_array($out);
  $len=count($res);
  if($len==0){return 0;}
  return $res;
}
function mysqlCmd($sql,$qout=0)
{
  global $DB,$DATE;
  if(!($out=mysqli_query($DB,$sql))){die("Error:".mysqli_error($DB));}
  if(!($result=sqlNoblank($out))){return 0;}
  if($qout){
    $result=array($result);
    while($row=mysqli_fetch_array($out)){array_push($result,$row);}
  }
  return $result;
}
function isBlank($string)
{
  if(!preg_match("/\w+/",$string)){return 1;}
  return 0;
}

////////////////////////////////////////////////////////////////////////
//VARIABLES
////////////////////////////////////////////////////////////////////////
foreach(array_keys($_GET) as $field){$$field=$_GET[$field];}
foreach(array_keys($_POST) as $field){$$field=$_POST[$field];}
$tQuakes="<a href='http://github.com/seap-udea/tQuakes'>tQuakes</a>";
$GITREPO="http://github.com/seap-udea/tQuakes";

////////////////////////////////////////////////////////////////////////
//DATABASE INITIALIZATION
////////////////////////////////////////////////////////////////////////
$DB=mysqli_connect("localhost",$DBUSER,$DBPASSWORD,$DBNAME);
$result=mysqlCmd("select now();",$qout=0,$qlog=0);
$DATE=$result[0];

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
////////////////////////////////////////////////////////////////////////
//ACTIONS
////////////////////////////////////////////////////////////////////////
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

////////////////////////////////////////////////////////////////////////
//FETCHING EVENTS
////////////////////////////////////////////////////////////////////////
if(isset($action)){

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
  $sql="update Quakes set astatus='2',stationid='$station_id',adatetime=now() where quakeid='$quakeid';";
  mysqlCmd($sql);
  return 0;
}

////////////////////////////////////////////////////////////////////////
//REPORTING END OF ANALYSIS
////////////////////////////////////////////////////////////////////////
else if($action=="analysis"){
  $sql="update Quakes set astatus='3',stationid='$station_id',adatetime=now(),qsignal='$qsignal',qphases='$qphases' where quakeid='$quakeid';";
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
//CHECK STATION
////////////////////////////////////////////////////////////////////////
else if($action=="submit"){
  $sql="update Quakes set astatus='4',stationid='$station_id',adatetime=now() where quakeid='$quakeid';";
  mysqlCmd($sql);
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
  if(file_exists("stations/authorized_keys")){
    $out=shell_exec("grep '$station_key' stations/authorized_keys");
  }else{$out="";}
  if(isBlank($out)){
    shell_exec("(echo;cat $station_dir/key.pub) >> stations/authorized_keys");
  }

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
$numquakes=mysqlCmd("select count(quakeid) from Quakes");
echo<<<PORTAL
<html>
<head>
</head>
<body>
<h1>
<a href=?>tQuakes</a>
</h1>
<a href="?if=register">Register Station</a> | 
<a href="?if=activity">Stations Activity</a> |
<a href="?if=data">Data Products</a> |
<a href="?if=calculate">Calculate</a> |
<a href="?if=download">Download</a> 
<p>
  Number of Earthquakes in database: $numquakes[0]
</p>
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
<a href="site/install-station.sh">Install a calculation station</a>.
</li>
<li>Clone from the <a href="$GITREPO">github repositorty</a></li>
</ul>
PORTAL;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//ACTIVITY
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="activity"){
  $stations=mysqlCmd("select * from Stations",$qout=1);
echo<<<TABLE
<table border=1px>
<tr>
  <td>Station Id.</td>
  <td>Status</td>
</tr>
TABLE;
  foreach($stations as $station){
    $station_id=$station["station_id"];
echo<<<TABLE
<tr><td>$station_id</td></tr>
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
      <td><input type=text name=station_id maxlength=11 size=8 value=$station_id></td>
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
Welcome to the website of the $tQuakes project. $tQuakes (Earthquakes
and Tides) is an innitiative of the Solar, Earth and Planetary Physics
Group (SEAP) of the University of Antioquia (Medellin, Colombia) in
collaboration with the National University in Colombia.
</p>
<p>
$tQuakes is a tool intended to explore the relationship between the
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
Developed by Gloria Moncayo & Jorge I. Zuluaga (2015)
</i>
</body></html>
