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
$conf=parse_ini_file("common");
foreach(array_keys($conf) as $key){
  $GLOBALS["$key"]=$conf["$key"];
}

////////////////////////////////////////////////////////////////////////
//VARIABLES
////////////////////////////////////////////////////////////////////////
session_start();
$SESSID=session_id();
foreach(array_keys($_GET) as $field){$$field=$_GET[$field];}
foreach(array_keys($_POST) as $field){$$field=$_POST[$field];}
$tQuakes="<a href='http://github.com/seap-udea/tQuakes'>tQuakes</a>";
$GITREPO="http://github.com/seap-udea/tQuakes";
$FORM="<form method='post' enctype='multipart/form-data' accept-charset='utf-8'>";
$STATUS="";
$ERRORS="";
$URLPAGE=$_SERVER["REQUEST_URI"];

////////////////////////////////////////////////////////////////////////
//VERIFY IDENTITY
////////////////////////////////////////////////////////////////////////
$QPERM=0;
$NAME="Anynymous";
if(isset($_SESSION["ulevel"])){
  $QPERM=$_SESSION["ulevel"];
  $NAME=$_SESSION["uname"];
  $EMAIL=$_SESSION["email"];
}
$PERMCSS="";
$type="inline";
$perm="$type";
$nperm="none";
if($QPERM>0){
  $perm="$type";
  $nperm="none";
}
$PERMCSS.=".level0{display:$perm;}\n.nolevel0{display:$nperm;}\n";
for($i=1;$i<=4;$i++){
  $perm="none";
  $nperm="$type";
  if($i<=$QPERM){$perm="$type";$nperm="none";}
  $PERMCSS.=".level$i{display:$perm;}\n.nolevel$i{display:$nperm;}\n";
}
$PERMCSS.=".level5{display:none;}\n.nolevel5{display:$type;}\n";
$PERM=array("0"=>"Anónimo",
	    "1"=>"User",
	    "2"=>"Administrator",
	    );

////////////////////////////////////////////////////////////////////////
//ENUM
////////////////////////////////////////////////////////////////////////
$STATION_STATUS=array("Idle","Fetching","Preparing","Running","Analysing","Submiting","Disabled");
$QUAKE_STATUS=array("Waiting","Fetched","Calculated","Analysed","Submitted");

////////////////////////////////////////////////////////////////////////
//ROUTINES
////////////////////////////////////////////////////////////////////////
function generateRandomString($length = 10) {
  $characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  $randomString = '';
  for ($i = 0; $i < $length; $i++) {
    $randomString .= $characters[rand(0, strlen($characters) - 1)];
  }
  return $randomString;
}
function errorMsg($msg)
{
  global $ERRORS;
  $ERRORS.="<p>".$msg."</p>";
}

function statusMsg($msg)
{
  global $STATUS;
  $STATUS.="".$msg."<br/>";
}
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

function myExec($cmd,$tmp="/tmp")
{
  $code=exec("($cmd) 2> $tmp/exec.error;echo $?",$output);
  $stdout=implode("\n",array_slice($output,0,-1));
  $stderr=shell_exec("cat $tmp/exec.error");
  $color="green";
  if($code>0){$color="red";}
$outtxt=<<<OUTPUT
<b style='color:$color'>Execution output:</b><br/>
<ul>
<li><b>Command</b>:<pre>$cmd</pre></li>
<li><b>Stdout</b>:<pre>$stdout</pre></li>
<li><b>Stderr</b>:<pre>$stderr</pre></li>
<li><b>Error code</b>:<pre>$code</pre></li>
</ul>
OUTPUT;
  return array($code,$stdout,$stderr,$outtxt);
}

function parseParams($params)
{
  $parameters=array();
  $parts=preg_split("/;/",$params);
  foreach($parts as $part){
    $comps=preg_split("/=/",$part);
    $param=$comps[0];
    $value=$comps[1];
    $parameters["$param"]=$value;
  }
  return $parameters;
}

////////////////////////////////////////////////////////////////////////
//DATABASE INITIALIZATION
////////////////////////////////////////////////////////////////////////
$DB=mysqli_connect("localhost",$DBUSER,$DBPASSWORD,$DBNAME);
$result=mysqlCmd("select now();",$qout=0,$qlog=0);
$DATE=$result[0];

//COMPONENTS
$COMPONENTS=array( 0, 1,    2, 4, 5,  9);
$COMPONENTS_DICT=array(array("pot",-1,"Tidal potential","m<sup>2</sup>/s<sup>2</sup>"),
		       array("grav",0,"Tidal gravity","nm/s<sup>2</sup>"),
		       array("tilt",1,"Tidal tilt","mas"),
		       array("vd",2,"Vertical displacement","mm"),
		       array("hd",3,"Horizontal displacement","mm"),
		       array("vs",4,"Vertical strain","nstr"),
		       array("hs",5,"Horizontal strain","nstr"),
		       array("areal",6,"Areal strain","nstr"),
		       array("shear",7,"Shear","nstr"),
		       array("volume",8,"Volume strain","nstr"),
		       array("hst",9,"Horizontal strain (Az = 90)","nstr")
		       );

////////////////////////////////////////////////////////////////////////
//DIRECTORIES
////////////////////////////////////////////////////////////////////////
$SCRATCHDIR="scratch/$SESSID/";
if(!is_dir($SCRATCHDIR) and !isset($action)){shell_exec("mkdir -p $SCRATCHDIR");}
if(isset($_SESSION["email"])){
  $email=$_SESSION["email"];
  $emailnoat=preg_replace("/@/","",$email);
  $USERDIR="users/$emailnoat";
  if(!is_dir($USERDIR)){
    shell_exec("mkdir -p $USERDIR");
  }
  $SCRATCHDIR=$USERDIR;
}
$STATSDIR="plots/analysis/";
?>
