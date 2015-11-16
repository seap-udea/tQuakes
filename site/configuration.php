<?php
$LOGIN_INFORMATION=array('admin'=>'123');
$pass=<<<PASS
<!--
<?php
\$PASS_INFORMATION=array(
PASS;
  foreach(array_keys($LOGIN_INFORMATION) as $key){
    $md5=md5($key.'%'.$LOGIN_INFORMATION["$key"]);
    $pass.="'$md5'=>'$key',";
  }
$pass=trim($pass,",");
$pass.=<<<PASS
);
?>
-->
PASS;
  echo $pass;
?>
<?php
$PASS_INFORMATION=array('55af568a0add378b4d9dd1b0542f8b8a'=>'admin');
?>
