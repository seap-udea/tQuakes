<?php
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
//VARIABLES
////////////////////////////////////////////////////////////////////////
foreach(array_keys($_GET) as $field){$$field=$_GET[$field];}
foreach(array_keys($_POST) as $field){$$field=$_POST[$field];}
$tQuakes="<a href='http://github.com/seap-udea/tQuakes'>tQuakes</a>";
$GITREPO="http://github.com/seap-udea/tQuakes";

////////////////////////////////////////////////////////////////////////
//ENUM
////////////////////////////////////////////////////////////////////////
$STATION_STATUS=array("Idle","Fetching","Preparing","Running","Analysing","Submiting","Disabled");
$QUAKE_STATUS=array("Waiting","Fetched","Calculated","Analysed","Submitted");

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

function searchExamples(){
  $i=-1;
  $examples_txt=array();
  $examples=array();
  $examples_url=array();
  
  $i++;
  array_push($examples_txt,"All quakes from 'departamentos' starting by 'ANT'");
  array_push($examples,"departamento like 'ANT%'");
  array_push($examples_url,urlencode($examples[$i]));

  $i++;
  array_push($examples_txt,"All quakes with magnitudes larger or equal than 2 order by magnitude in ascending order");
  array_push($examples,"Ml+0>2 order by Ml asc");
  array_push($examples_url,urlencode($examples[$i]));

  $i++;
  array_push($examples_txt,"All quakes between january 1st and june 30 1994 with depths larger than 100 km");
  array_push($examples,"STR_TO_DATE(qdate,'%d/%m/%Y') between '1994-01-01' and '1994-06-30' and qdepth+0>100");
  array_push($examples_url,urlencode($examples[$i]));
  
  return array($i,$examples,$examples_txt,$examples_url);
}


////////////////////////////////////////////////////////////////////////
//DATABASE INITIALIZATION
////////////////////////////////////////////////////////////////////////
$DB=mysqli_connect("localhost",$DBUSER,$DBPASSWORD,$DBNAME);
$result=mysqlCmd("select now();",$qout=0,$qlog=0);
$DATE=$result[0];

?>
