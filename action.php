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

  // ============================================================
  // CHECK IF STATION IS ENABLED
  // ============================================================
  $sql="select station_receiving from Stations where station_id='$station_id';";
  $result=mysqlCmd($sql);
  $station_receiving=$result[0];
  if($station_receiving<0){
    echo "-1";
    return 0;
  }

  // ============================================================
  // FETCH QUAKES NOT FETCHED OR FETCHED TOO MUCH TIME AGO
  // ============================================================
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
  $disprops=array("quakeid","qjd","qlat","qlon","qdepth","qdate","qtime","hmoon","hsun");
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
  $sql="update Quakes set astatus='3',stationid='$station_id',calctime2='$deltat',adatetime=now(),qsignal='$qsignal',qphases='$qphases',aphases='$aphases' where quakeid='$quakeid';";
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
//ELSE
////////////////////////////////////////////////////////////////////////

else {
  echo "Server responding: ",$DATE;
  return 0;
}
}
?>
