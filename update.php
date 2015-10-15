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
if(isset($replot)){
   $name=preg_split("/\./",$plot)[0];
   $cmd="PYTHONPATH=. MPLCONFIGDIR=/tmp python plots/$name.py";
   echo "Plotting: $cmd<br/>";
   $out=shell_exec("PYTHONPATH=. MPLCONFIGDIR=/tmp python plots/$name.py &> /tmp/error");
   echo "$out<br/>";
   $content="Replot succesful...";
   $refresh_time=1;
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
