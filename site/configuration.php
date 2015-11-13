<?php
$LOGIN_INFORMATION=array
    (
     'admin'=>'123',
     'facultad'=>'fcen2014',
     'fisica'=>'fisica2014',
     'matematicas'=>'matematicas2014',
     'biologia'=>'biologia2014',
     'quimica'=>'quimica2014',
     'profesor'=>'profesor2014',
     );

$INSTITUTOS=array
  (
   'admin'=>'Administrador',
   'facultad'=>'Facultad',
   'fisica'=>'Instituto de Física',
   'matematicas'=>'Instituto de Matemáticas',
   'biologia'=>'Instituto de Biología',
   'quimica'=>'Instituto de Química',
   'profesor'=>'Profesor'
   );

$USER="curriculo";
$PASSWORD="123";
$DATABASE="Curriculo";
if(!isset($_SERVER['SERVER_NAME'])){
$pass=<<<PASS
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
PASS;
  echo $pass;
}
?>
<?php
$PASS_INFORMATION=array('55af568a0add378b4d9dd1b0542f8b8a'=>'admin','4204c59a7565529f95b0b8c1f71e8dad'=>'facultad','32def115af796f8a51f6c84fbbb5d34f'=>'fisica','3d2e60870653882767097d6a6ae6622b'=>'matematicas','2965f1f5ccea4a39d1e7d4a9da31e8b1'=>'biologia','7d6473af2dafb9c6d797fdd1fc3e1bf5'=>'quimica','697606c8ebc11a7b4ae34ed26605292e'=>'profesor');
?>