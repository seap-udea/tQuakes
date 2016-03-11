<?php
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
////////////////////////////////////////////////////////////////////////
//PREAMBLE
////////////////////////////////////////////////////////////////////////
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//UTILITIES
require_once("site/util.php");
header("Content-Type: text/html;charset=UTF-8");

//CONTENT
$CONTENT="";
$SUBMENU="";

//VARIABLES
if(!isset($action)){$action="";}
if(!isset($if)){$if="";}

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
////////////////////////////////////////////////////////////////////////
//ACTIONS
////////////////////////////////////////////////////////////////////////
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if(!isBlank($action)){
  ////////////////////////////////////////////////////////////////////////
  //REMOVE STATION
  ////////////////////////////////////////////////////////////////////////
  if($action=="remove"){
    if(is_dir("stations/$station_id")){
      // REMOVE FROM DATABASE
      $sql="delete from Stations where station_id='$station_id';";
      mysqlCmd($sql);
      // REMOVE STATION INFORMATION
      shell_exec("mv stations/$station_id stations/.trash");
      statusMsg("Station $station_id removed.");
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
      $status="Station $station_id already registered. Updating.";
    }else if(is_dir($station_predir)){
      $status="Station $station_id registered.";
      shell_exec("mv $station_predir $station_dir");
    }else{
      $ERROR="Station not installed (preregistered) yet.";
    }

    //CREATING PUBLIC KEY
    $fl=fopen("$station_dir/key.pub","w");
    fwrite($fl,"no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty,command=\"scp -r -d -t ~/tQuakes/\" $station_key");
    fclose($fl);
    
    //SEND A MESSAGE TO ADMINISTRATOR
    if(!mysqlCmd("select * from Stations where station_id='$station_id'")){
      $urlstring="station_id=$station_id&station_name=$station_name&station_email=$station_email";
$message=<<<M
<p>
  Dear administrator,
</p>
<p>
  A user has registered a new calculation station in this $tQuakes
  server.  The station is not yet activated.  Please use the link
  below to activate the station and start sending data to that
  station.
</p>
<p>
  <a href="$WEBSERVER/index.php?if=register&$urlstring">Click to activate station</a>
</p>
<p>
  Please remember that you have to be logged in as the administrator
  in order to activate the station.
</p>
<p>Best wishes,</p>
<p>
  <b>$tQuakes Administrator</b>
</p>
M;
       $subject="[tQuakes] New tQuakes computing station";
       sendMail($EMAIL_USERNAME,$subject,$message,$EHEADERS);
    }


    //UPDATING STATION IN DATABASE
    if(isBlank($station_receiving)){$station_receiving=0;}
    $conf=parse_ini_file("$station_dir/${station_id}rc");
    foreach(array_keys($conf) as $key){
      $GLOBALS["$key"]=$conf["$key"];
    }
    $sql="insert into Stations (station_id,station_name,station_email,station_arch,station_nproc,station_mem,station_mac,station_receiving) values ('$station_id','$station_name','$station_email','$station_arch','$station_nproc','$station_mem','$station_mac','$station_receiving') on duplicate key update station_name=VALUES(station_name),station_email=VALUES(station_email),station_arch=VALUES(station_arch),station_nproc=VALUES(station_nproc),station_mem=VALUES(station_mem),station_mac=VALUES(station_mac),station_receiving=VALUES(station_receiving);";
    mysqlCmd($sql);
    header("Refresh:0;url=$WEBSERVER/?status=$status");
  }
  ////////////////////////////////////////////////////////////////////////
  //NEW USER
  ////////////////////////////////////////////////////////////////////////
  else if($action=="Create"){
    $if="newuser";
    //TEST FORM
    if(isBlank($email) or
       !preg_match("/@/",$email)){
      errorMsg("You should provide a valid e-mail");
      goto endaction;
    }
    if(mysqlCmd("select * from Users where email='$email'")){
      errorMsg("A user with this e-mail already exists"); 
      goto endaction;
    }      
    if(isBlank($password)){
      errorMsg("Password invalid");
      goto endaction;
    }
    if($password!=$cpassword){
      errorMsg("Paswords does not match");
      goto endaction;
    }
    if(isBlank($uname)){
      errorMsg("Invalid name");
      goto endaction;
    }
    if(strlen($ERRORS)==0){
      //DATABASE ENTRY
      $password=md5($password);
      $ulevel="1";
      insertSql("Users",array("uname"=>"",
			      "email"=>"",
			      "password"=>"",
			      "ulevel"=>"")
		);

      //MESSAGES
      statusMsg("User has been registered.  Please check your e-mail to activate the
account.");

$message=<<<M
<p>
  Dear $name,
</p>
<p>
  We have received your request to open an account in $tQuakes
  website.  In order to use your account you need to activate it using
  the link below:
</p>
<p>
  <a href="$WEBSERVER/index.php?action=activate&email=$email">Click to activate your account</a>
</p>
<p>Best wishes,</p>
<p>
  <b>$tQuakes Administrator</b>
</p>
M;
       $subject="[tQuakes] Account activation";

       sendMail($email,$subject,$message,$EHEADERS);
    }
    if(isset($if)){unset($if);}
  }
  ////////////////////////////////////////////////////////////////////////
  //ACTIVATE
  ////////////////////////////////////////////////////////////////////////
  else if($action=="activate"){
    if($result=mysqlCmd("select * from Users where email='$email'")){
      mysqlCmd("update Users set activate='1' where email='$email'");
      header("Refresh:0;url=$WEBSERVER/?if=user&status=Your account has been activated");
    }else{
      errorMsg("La cuenta de $email no existe.");
    }
  }
  ////////////////////////////////////////////////////////////////////////
  //RECOVER
  ////////////////////////////////////////////////////////////////////////
  else if($action=="Change"){
    //TEST FORM
    if(isBlank($pass1) or
       isBlank($pass2)){
      errorMsg("No password provided");
      goto endaction;
    }
    if($pass1!=$pass2){
      errorMsg("Password does not match");
      goto endaction;
    }
    $results=mysqlCmd("select * from Users where email='$email'");
    $spass=$results["password"];
    if($pass!=$spass){
      errorMsg("Authentication failed.");
      goto endaction;
    }
    if(strlen($ERRORS)==0){
      $password=md5($pass1);
      mysqlCmd("update Users set password='$password' where email='$email'");
      header("Refresh:0;url=$WEBSERVER/?if=user&status=Password modified");
    }
  }
  ////////////////////////////////////////////////////////////////////////
  //RECOVER
  ////////////////////////////////////////////////////////////////////////
  else if($action=="Recover"){

    if($results=mysqlCmd("select * from Users where email='$email'")){

      $pass=$results["password"];
      $uname=$results["uname"];

$message=<<<M
<p>
  Dear $uname,
</p>
<p>
  We have received a request to recover your password in $tQuakes. In
  order to proceed please use the link below:
</p>
<p>
  <a href="$WEBSERVER/index.php?if=setpassword&email=$email&pid=$pass">Click
  to change your password</a>
</p>
<p>Best wishes,</p>
<p>
  <b>$tQuakes Administrator</b>
</p>
M;
      $subject="[tQuakes] Password reset";

      sendMail($email,$subject,$message,$EHEADERS);

      statusMsg("We have sent a recovery message to your e-mail");
    }else{
      errorMsg("E-mail not recognized.");
      goto endaction;
    }
  }
  ////////////////////////////////////////////////////////////////////////
  //CLEAN STATS
  ////////////////////////////////////////////////////////////////////////
  else if($action=="cleanstats"){
   shell_exec("cd $STATSDIR;make clean");
   statusMsg("Cleaned...");
  }
  ////////////////////////////////////////////////////////////////////////
  //REPLOT STATS
  ////////////////////////////////////////////////////////////////////////
  else if($action=="restats"){
   shell_exec("cd $STATSDIR;make plotall");
   header("Refresh:0;url=?if=data&status=Replot");
  }
  ////////////////////////////////////////////////////////////////////////
  //LOGOUT
  ////////////////////////////////////////////////////////////////////////
  else if($action=="logout"){
    session_unset();
    $urlref="?";
    statusMsg("Logout succesful");
    header("Refresh:0;url=$urlref");
  }
  ////////////////////////////////////////////////////////////////////////
  //LOGIN
  ////////////////////////////////////////////////////////////////////////
  else if($action=="Login"){
    //TEST FORM
    if(isBlank($email) or
       !preg_match("/@/",$email)){
      errorMsg("Invalid e-mail");
      goto endaction;
    }
    if(isBlank($password)){
      errorMsg("Password no provisto");
      goto endaction;
    }
    if(!mysqlCmd("select * from Users where email='$email'")){
      errorMsg("No user with that e-mail");
      goto endaction;
    }
    if(!mysqlCmd("select * from Users where email='$email' and activate='1'")){
      errorMsg("Your account is not active yet.");
      goto endaction;
    }
    if(strlen($ERRORS)==0){
      //CHECK IF USER EXISTS
      if($results=mysqlCmd("select * from Users where email='$email'")){
	$subpass=md5($password);
	if($subpass==$results["password"]){
	  session_start();
	  foreach(array_keys($results) as $key){
	    if(preg_match("/^\d$/",$key)){continue;}
	    $_SESSION["$key"]=$results[$key];
	  }
	  if(preg_match("/user/",$urlref)){$urlref="index.php";}
	  statusMsg("Login succesful");
	  header("Refresh:0;url=$urlref");
	}else{
	  errorMsg("Invalid password");
	}
      }else{
	errorMsg("User not recognized");
      }
    }
  }

  ////////////////////////////////////////////////////////////////////////
  //CLEAN 
  ////////////////////////////////////////////////////////////////////////
  else if($action=="cleansynthetic"){
    statusMsg("Cleaning synthetic earthquakes");
    shell_exec("rm -r $SCRATCHDIR/*.tar $SCRATCHDIR/???????");
  }
  else if($action=="cleanhistory"){
    statusMsg("Cleaning history");
    shell_exec("rm -r $SCRATCHDIR/history.log");
  }

  ////////////////////////////////////////////////////////////////////////
  //CALCULATE
  ////////////////////////////////////////////////////////////////////////
  else if($action=="calculate" or $action="plot"){

    //========================================
    //CHECK INPUT FORM
    //========================================
    if(isBlank($qlat)){
      errorMsg("You must provide a latitude");
      goto endaction;
    }
    if(isBlank($qlon)){
      errorMsg("You must provide a longitude");
      goto endaction;
    }
    if(isBlank($qdepth)){
      errorMsg("You must provide a depth");
      goto endaction;
    }
    if(isBlank($qdatetime)){
      errorMsg("You must provide a date");
      goto endaction;
    }
    $qjd=rtrim(shell_exec("PYTHONPATH=. python util/date2jd.py '$qdatetime'"));
    if(isBlank($qjd)){
      errorMsg("Bad date");
      goto endaction;
    }
    statusMsg("All fields checked...");

    //========================================
    //PREPARE VARIABLES
    //========================================
    if(!isset($qpreserve)){$qpreserve=0;}
    statusMsg("Preserve $qpreserve");

    //========================================
    //GENERATE NEW QUAKEID
    //========================================
    $quakestr=sprintf("QUAKE-lat_%+08.4f-lon_%+09.4f-dep_%+010.4f-JD_%.5f",$qlat,$qlon,$qdepth,$qjd);
    statusMsg("Quake string: $quakestr");
    $md5str=md5($quakestr);
    $tquakeid=strtoupper(substr($md5str,0,7));
    statusMsg("New quakeid $tquakeid");
    while(mysqlCmd("select quakeid from Quakes where quakeid='$tquakeid';")){
      $tquakeid=str_shuffle($tquakeid);
    }

    //========================================
    //CHECK IF QUAKEID IS IN DB
    //========================================
    $quakeindb=mysqlCmd("select * from Quakes where quakeid='$quakeid' and qjd='$qjd'");
    if(!$quakeindb){
      statusMsg("Quakeid $quakeid not in database...");
      $qpreserve=0;
    }else{
      statusMsg("Stored quakestr: ".$quakeindb["quakestr"]);
      //IF QUAKESTR DOES NOT MATCH THE QUAKE PARAMETERS HAVE CHANGED
      if($quakeindb["quakestr"]!=$quakestr){
	$qcopy=0;
	$qpreserve=0;
	$quakeid=$tquakeid;
	statusMsg("Quakestrs does not match");
	statusMsg("New quakeid $quakeid");
      }else{
	statusMsg("Quakestrs match");
      }
    }
    statusMsg("After checking $qpreserve");

    //========================================
    //CHECK IF A QUAKEID HAS HAD BEEN PROVIDED
    //========================================
    $qcopy=0;
    if(isset($quakeid)){
      if(!$qpreserve){
	//IF NO PRESERVE THE NEW QUAKEID IS THE CALCULATED ONE
	if($quakeid!=$tquakeid){$quakeid=$tquakeid;}
      }else{
	//IF QUAKE IS PRESERVED CREATE A COPY OF THE DIRECTORY OF EARTHQUAKE
	$qcopy=1;
      }
    }
    statusMsg("Copy $qcopy");
    statusMsg("Final $quakeid");

    //========================================
    //CREATE QUAKE SCRATCH DIRECTORY
    //========================================
    $quakedir="$SCRATCHDIR/$quakeid";
    if(!is_dir($quakedir)){
      shell_exec("mkdir -p $quakedir");
      statusMsg("Scratch directory created...");
    }
    
    //========================================
    //CHECKTYPE
    //========================================
    /*
      There are the following types of earthquakes:
      1) Earthquake in database (qdb=1):
         1.0) Earthquake is not calculated (qdone=0)
	 1.1) Earthquake is already calculated (qdone=1)
      0) Earthquake not in database (qdb=0):
         0.0) Earthquake is in queue (qdone=0)
	 0.1) Earthquake is already calculated (qdone=1)
     */

    //TYPE BY DEFAULT
    $qdb=0;$qdone=0;

    $quakeindb=mysqlCmd("select * from Quakes where quakeid='$quakeid' and qjd='$qjd'");
    if($quakeindb){
      statusMsg("Quake in db");
      $qdb=1;
      //CHECK IF IT'S DONE
      if(mysqlCmd("select * from Quakes where quakeid='$quakeid' and astatus+0=4")){
	statusMsg("Quake done");
	$qdone=1;
      }else{
	statusMsg("Quake in db but not done");
	if(file_exists("data/tQuakes/$quakeid.conf")){
	  statusMsg("Quake already prepared");
	  $qdone=1;
	}else{
	  statusMsg("Quake not prepared");
	  $qdone=0;
	}
      }
    }else{
      statusMsg("Quake not in db");
      $qdb=0;
      if(file_exists("data/tQuakes/$quakeid.conf")){
	statusMsg("Quake already prepared");
	$qdone=1;
      }else{
	statusMsg("Quake not prepared");
	$qdone=0;
      }
    }
    statusMsg("Quake type: qdb=$qdb, qdone=$qdone...");
    
    //========================================
    //IF QUAKE HAS NOT BEEN CALCULATED
    //========================================
    if(!$qdone){

      //CREATE CALCULATION DIRECTORY
      $cquakedir="data/quakes/$quakeid";
      if(!is_dir($cquakedir)){
	shell_exec("mkdir -p $cquakedir");
	statusMsg("Calculation directory created...");

	shell_exec("cp -rd data/quakes/TEMPLATE/* $cquakedir");
	shell_exec("cp -rd data/quakes/TEMPLATE/.[a-z]* $cquakedir");
	
	//SPLIT DATETIME
	$parts=preg_split("/\s+/",$qdatetime);
	$date=$parts[0];
	$time=$parts[1];
	
	//CREATE CONFIGURATION
	$fl=fopen("$cquakedir/quake.conf","w");
$conf=<<<C
qdepth='$qdepth'
quakeid='$quakeid'
qlat='$qlat'
qdate='$date'
qlon='$qlon'
qtime='$time'
qjd='$qjd'

C;
         fwrite($fl,$conf);
	 fclose($fl);
	 
	 //========================================
	 //PREPARE RUN
	 //========================================
	 shell_exec("PYTHONPATH=. python $cquakedir/quake-prepare.py $quakeid");
	 statusMsg("Eterna files generated...");
      }
      statusMsg("Quake $quakeid in queue...");
      goto endcalculate;
    }

    //========================================
    //IF QUAKE HAS BEEN ALREADY CALCULATED
    //========================================
    else{
      if($qdb){
	statusMsg("Quake $quakeid in db...");
	$dirquakes="$HOMEDIR/$TQUSER/tQuakes/";
      }else{
	statusMsg("Quake $quakeid not in db...");
	$dirquakes="data/tQuakes/";
      }

      //========================================
      // RECOVER QUAKE INFO
      //========================================
      $filequake="$dirquakes/$quakeid-eterna.tar.7z";

      //CHECK IF PRECALCULATED FILES ALREADY EXISTS
      if(file_exists($filequake)){
	statusMsg("Results for $quakeid found...");

	//CHECK IF THEY HAVE BEEN UNZIPED
	if(!file_exists("$quakedir/$quakeid-eterna.tar")){
	  statusMsg("Unzipping files...");
	  shell_exec("cp -rf $dirquakes/$quakeid-* $quakedir/");
	  shell_exec("cp -rf $dirquakes/$quakeid.conf $quakedir/");
	  shell_exec("cd $quakedir;p7zip -d $quakeid-eterna.tar.7z");
	  shell_exec("cd $quakedir;p7zip -d $quakeid-analysis.tar.7z");
	  shell_exec("cd $SCRATCHDIR;tar cf $quakeid.tar $quakeid/$quakeid-*");
	  
	  //UNTAR ALL FILES
	  shell_exec("cd $quakedir;tar xf $quakeid-eterna.tar");
	  shell_exec("cd $quakedir;tar xf $quakeid-analysis.tar");
	  
	  //COPY SUPPORTING PYTHON FILES
	  shell_exec("cd $quakedir;ln -s ../../../tquakes.py");
	  shell_exec("cd $quakedir;ln -s ../../../util");
	  shell_exec("cd $quakedir;ln -s ../../../configuration");
	  shell_exec("cd $quakedir;ln -s ../../../plots/analysis/makefile");

	  //COPY PLOTTING SCRIPTS
	  foreach($COMPONENTS as $ncomp){
	    $component=$COMPONENTS_DICT[$ncomp+1];
	    $symbol=$component[0];
	    $componentname=$component[2];
	    foreach($QUAKE_PLOTS as $plot){
	      foreach(array("py","conf","html","history") as $ext){
		$cmd="cp -r plots/analysis/quake-$plot.$ext $quakedir/quake-$plot-$symbol.$ext";
		shell_exec($cmd);
	      }
	      shell_exec("echo >> $quakedir/quake-$plot-$symbol.conf");
	      shell_exec("echo 'component=\"$symbol\"' >> $quakedir/quake-$plot-$symbol.conf");
	      shell_exec("echo 'description=\"Plot $plot for component $componentname\"' >> $quakedir/quake-$plot-$symbol.conf");
	    }
	  }

	  //CREATE A COPY WITH THE NEW QUAKEID
	  if($qcopy){
	    statusMsg("Linking $tquakeid with $quakeid...");
	    shell_exec("cd $SCRATCHDIR/;ln -s $quakeid $tquakeid");
	    shell_exec("cd $SCRATCHDIR/;ln -s $quakeid.tar $tquakeid.tar");
	  }

	}//End tar file exists
      }//End quake has been completed
    }
    
    //========================================
    //GENERATE REPORT
    //========================================
    $tideresults="<h2><a name=results>Results</a></h2>";
    $SUBMENU.="<a href='#results'>Results</a> : ";
    
    //FILES
    $size_eterna=round(filesize("$quakedir/$quakeid-eterna.tar")/1024.0,0);
    $size_analysis=round(filesize("$quakedir/$quakeid-analysis.tar")/1024.0,0);
    $size_full=round(filesize("$SCRATCHDIR/$quakeid.tar")/1024.0,0);

    //QUAKE PROPERTIES
    $quakeconf="$quakedir/$quakeid.conf";
    $quake=parse_ini_file($quakeconf);
	   
    //COMPONENT SIGNAL
    $signaltxt.="<h3><a nmae=signal>Component signal</a></h3><ul>";
    $SUBMENU.="<a href='#signal'>Signal</a> | ";

    $signals=preg_split("/;/",$quake["qsignal"]);
    $i=0;
    foreach($signals as $signal){
      $ncomp=$COMPONENTS[$i];
      $component=$COMPONENTS_DICT[$ncomp+1];
      $namecomponent=$component[2];
      $units=$component[3];
      if(isBlank($signal)){continue;}
      $signaltxt.="<li><b>$namecomponent</b>:$signal $units</li>";
      $i++;
    }
    $signaltxt.="</ul>";
    $tideresults.=$signaltxt;

    //COMPONENT PHASES
    $SUBMENU.="<a href='#phases'>Phases</a> | ";

    $phases=preg_split("/;/",$quake["qphases"]);
$phasetxt=<<<P
<h3><a name=phases>Component phases</a></h3>
<table border=1px cellspacing=0px>
<tr>
<td>Component</td>
<td>Semi diurnal</td>
<td>Diurnal</td>
<td>Fornightly</td>
<td>Monthly</td>
</tr>
P;

    $i=0;
    foreach($COMPONENTS as $ncomp){
      $component=$COMPONENTS_DICT[$ncomp+1];
      $namecomponent=$component[2];
      $phasetxt.="<tr><td>$namecomponent</td>";
      for($j=0;$j<4;$j++){
	$iphase=8*$i+4+$j;
	$phasetime=$phases[$iphase];
	$parts=preg_split("/:/",$phasetime);
	$time=$parts[0];
	$phase=$parts[1];
	$phasetxt.="<td>$phase</td>";
      }
      $phasetxt.="</tr>";
      $i++;
    }
    
    $phasetxt.="</table>";
    $tideresults.=$phasetxt;
    $SUBMENU.="<a href='#download'>Download</a> | ";
    
$tideresults.=<<<T
  <h3><a name=download>Downloads</a></h3>
  <ul>
    <li><a href=$quakeconf target=_blank>Summary file</a></li>
    <li><a href=$quakedir/$quakeid-eterna.tar>Eterna results</a> ($size_eterna kB)</li>
    <li><a href=$quakedir/$quakeid-analysis.tar>Analysis results</a> ($size_analysis kB)</li>
    <li><a href=$SCRATCHDIR/$quakeid.tar>All results</a> ($size_full kB)</li>
  </ul>
  
T;

    //SHOW PLOTS
    if($action=="plot"){
      //========================================
      //PLOT
      //========================================
      $SUBMENU.="<a href='#plots'>Plots</a> | ";
      $tideresults.="<h3><a name=plots>Plots</a></h3>";
      $plots="";

      $plotmd5s=array();
      foreach($COMPONENTS as $ncomp){
	$component=$COMPONENTS_DICT[$ncomp+1];
	$symbol=$component[0];
	$componentname=$component[2];
	foreach($QUAKE_PLOTS as $plot){
	  $plotbase="quake-$plot-$symbol";
	  $description=shell_exec("cat $quakedir/$plotbase.html");
	  if(isBlank($description)){$description="<h4>$plotbase</h4>";}
	  statusMsg("Generating plot $plotbase...");
	  $output=shell_exec("find -L $quakedir -name '${plotbase}__*.png'");
	  if(isBlank($output)){
	    $cmd="cd $quakedir;python $plotbase.py";
	    shell_exec($cmd);
	    $output=shell_exec("find -L $quakedir -name '${plotbase}__*.png'");
	  }else{
	    statusMsg("Plot already generated...");
	  }
	  $listpng=preg_split("/\n/",$output);
	  $plots.="$description<div class='plotstack'>";
	  foreach($listpng as $png){
	    if(isBlank($png)){continue;}
	    $pngname=rtrim(shell_exec("basename $png"));
	    $pngbase=preg_split("/\./",$pngname)[0];
	    $pngparts=preg_split("/__/",$pngbase);
	    $pngmd5=$pngparts[1];
	    if(in_array($pngmd5,$plotmd5s)){continue;}
	    else{array_push($plotmd5s,$pngmd5);}
	    $plot=parse_ini_file("$quakedir/$plotbase.history/$pngbase.conf");
	    if(isset($plot["description"])){$deschist=$plot["description"];}
	    else{$deschist="No description";}
	    $plotfigure=generateFigure($quakedir,$plotbase,$pngmd5);
	    $plots.="$plotfigure";
	    statusMsg("Plot generated...");
	    //break;
	  }
	  $plots.="</div>";
	}
	//break;
      }
      statusMsg("All plots generated...");
      $tideresults.=$plots;
    }

  endcalculate:
    if(!$qdone){
      $tideresults.="Processing request...<br/><img src=img/loader.gif>";
      header("Refresh:3;url=$URLPAGE&action=$action&quakeid=$quakeid&qlat=$qlat&qlon=$qlon&qdepth=$qdepth&qdatetime=$qdatetime&qjd=$qjd");
    }

  }//End action=calculate

  ////////////////////////////////////////////////////////////////////////
  //REGISTER STATION
  ////////////////////////////////////////////////////////////////////////
  else {
    echo "Server responding: ",$DATE;
    return 0;
  }
  endaction:
    $CONTENT.="";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
////////////////////////////////////////////////////////////////////////
//WEBPAGE
////////////////////////////////////////////////////////////////////////
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if(0){}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//USER
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="user"){
  if($QPERM<1){
$CONTENT.=<<<C
<h3>User login</h3>
$FORM
<input type="hidden" name="urlref" value="$urlref">
<table>
<tr>
  <td>E-mail:</td>
  <td><input type="text" name="email" placeholder="Su e-mail" value="$email"></td>
</tr>
<tr>
  <td>Password:</td>
  <td><input type="password" name="password" placeholder="Contraseña"></td>
</tr>
<tr>
  <td colspan=2>
    <input type="submit" name="action" value="Login">
  </td>
</tr>
<tr>
  <td colspan=2>
    <a href=?if=newuser>New user</a> |
    <a href=?if=recoverpass>Recover  password</a>
  </td>
</tr>
</table>
</form>
C;
  }else{
    $CONTENT="<i>You are already logged in as $NAME</i>";
  }
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//NEW USER
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="setpassword"){
  $results=mysqlCmd("select * from Users where email='$email'");
  $spass=$results["password"];
  if($pid==$spass){
$CONTENT.=<<<C
$FORM
<h3>Changing password for $email</h3>
<input type="hidden" name="pass" value="$pid">
<input type="hidden" name="email" value="$email">
<table>
<tr>
  <td>New password:</td>
  <td><input type="password" name="pass1" placeholder="Your new password"></td>
</tr>
<tr>
  <td>Confirm password:</td>
  <td><input type="password" name="pass2" placeholder="Repeat your password"></td>
</tr>
<tr>
  <td colspan=2>
    <input type="submit" name="action" value="Change">
  </td>
</tr>
</table>
</form>
C;
  }else{
    errorMsg("User not authorized");
    $CONTENT.="<i>Authentication failed</i>";
  }
}
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//NEW USER
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="newuser"){
$CONTENT.=<<<C
<form>
<h3>Nuevo usuario</h3>
<table>
<tr>
  <td>Name:</td>
  <td><input type="text" name="uname" placeholder="Name" value="$uname"></td>
</tr>
<tr>
  <td>E-mail:</td>
  <td><input type="text" name="email" placeholder="Your e-mail" value="$email"></td>
</tr>
<tr>
  <td>Password:</td>
  <td><input type="password" name="password" placeholder="Your password"></td>
</tr>
<tr>
  <td>Confirm password:</td>
  <td><input type="password" name="cpassword" placeholder="Your password"></td>
</tr>
<tr>
  <td colspan=2>
    <input type="submit" name="action" value="Create">
  </td>
</tr>
</table>
</form>
C;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//RECOVER PASS
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="recoverpass"){
$CONTENT.=<<<C
<form>
<h2>Password Recovery</h2>
<table>
<tr>
  <td>E-mail:</td>
  <td><input type="text" name="email" placeholder="Your registered e-mail"></td>
</tr>
<tr>
  <td colspan=2>
    <input type="submit" name="action" value="Recover">
  </td>
</tr>
</table>
</form>
C;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//DOWNLOAD
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="download"){
$CONTENT.=<<<C
<h2>Download tQuakes</h2>

<p>
  $tQuakes is an open source project.  You can download it directly
  from its <a href="$GITREPO" target="_blank">GitHub repository</a>.
</p>

<p>
  There are two branches:
  <ul>
    <li>
      The <b>master branch</b> which contains all the required
      "machinery" to run a $tQuakes server (serve a local database,
      compute own dataproducts, etc.) This branck comes with a
      preloaded earthquakes database (the database in
      the <a href="$MAINSERVER">main server</a>).  In
      order to download it you must have <b>~450 Mb</b> available.<br/><br/>

      To install this branch run:
      <blockquote class="cmd">
	git clone $GITREPO
      </blockquote>

    </li>
    <li>
      The <b>station branch</b> which contains all the required
      "machinery" to run individual processes sent by a $tQuakes
      server.  In order to download it you must have <b>~40 Mb</b>
      available.

      To install this branch run:
      <blockquote class="cmd">
	git clone --branch station --single-branch $GITREPO
      </blockquote>

    </li>
  </ul>

<p>
  In order to simplify the download and installation of a computation
  station you can also download and run this installation script: 

  <a href="site/install-station.sh">install-station.sh</a>.  The
  installation script is intended for clients running <b>Linux
  Debian</b> and has been extensively tested in <b>Ubuntu boxes</b>.
</p>
C;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REFERENCES
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="references"){
  require_once("site/references.php");
$CONTENT.=<<<C
<h2>References</h2>
$REFERENCES
C;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//DATA PRODUCTS
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="data"){
  $plotlist="";
$CONTENT.=<<<C

<h2>Data Products</h2>
<p>
  One of the most important products of $tQuakes is data. A lot of it.
  
  Data containing information about Earthquakes around the globe (more
  specifically in Colombia and South America) and the lunisolar tides
  affecting the places where those Earthquakes happened.

  Here are some of the available data products from $tQuakes.
</p>

<p>
  The plots shown here are just a sample of the analysis that have
  been performed on the database.  To see other results see the
  "history" of each plot.
</p>

<div class="level2 admin">
  Administrative area: 
  <a href="?if=data&action=cleanstats">Clean plots</a> | 
  <a href="?if=data&action=restats">Replot all</a> | 
  <a href="plot.php?plothell">Plot hell</a>
</div>
<p></p>
C;
 
   //==================================================
   //PLOTS
   //==================================================
 
   //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   //LIST OF SCRIPTS
   //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   $listplots=file("$STATSDIR/stats-sorting.txt");

   //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   //FOR EACH SCRIPT...
   //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   $SUBMENU.="<a name=submenu></a>";
   foreach($listplots as $plotprops){
     if(isBlank($plotprops)){continue;}
     $parts=preg_split("/:/",$plotprops);
     $submenu=$parts[0];
     $submenu_key=preg_replace("/\s/","_",$submenu);
     $SUBMENU.="<a href=#$submenu_key>$submenu</a> | ";
     $plot=$parts[1];
     $plotname=rtrim(shell_exec("basename $plot"));
     $plotbase=preg_split("/\./",$plotname)[0];

     //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     //LOOK FOR ALL PLOTS
     //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     $output=shell_exec("find $STATSDIR -name '${plotbase}__*.png'");
     if(isBlank($output)){
       $plotlist.="";
     }else{
       $description=shell_exec("cat $STATSDIR/$plotbase.html");
       $plotlist.="<a name=$submenu_key><a class='top' href=#submenu>Top</a>$description<div class='plotstack'>";
       $listhist=preg_split("/\n/",$output);
       $plotmd5s=array();
       foreach($listhist as $hist){
	 if(isBlank($hist)){continue;}
	 $histname=rtrim(shell_exec("basename $hist"));
	 $histbase=preg_split("/\./",$histname)[0];
	 $histparts=preg_split("/__/",$histbase);
	 $histmd5=$histparts[1];
	 if(in_array($histmd5,$plotmd5s)){continue;}
	 else{array_push($plotmd5s,$histmd5);}
	 $plot=parse_ini_file("$STATSDIR/$plotbase.history/$histbase.conf");
	 if(isset($plot["description"])){$deschist=$plot["description"];}
	 else{$deschist="No description";}

	 $plotfigure=generateFigure($STATSDIR,$plotbase,$histmd5,"","width:40vw;text-align:center;");
	 $plotlist.="<center>$plotfigure</center>";
	 break;
       }
       $plotlist.="</div>";
     }
     $i++;
  }
  $CONTENT.="$plotlist</li></ul>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//STATIONS INFORMATION
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="stations"){
  
  //////////////////////////////////////////////////////////////
  //BASIC STATISTICS
  //////////////////////////////////////////////////////////////
  $CONTENT.="<h2><a name='stats'></a>Basic Statistics</h2>";
  $SUBMENU.="<a href='#stats'>Basic Statistics</a> | ";
  
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
									    
$CONTENT.=<<<STAT
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

   //$CONTENT.="<a href=$SCRATCHDIR/stats.log.prev target=_blank>Previous</a> | <a href=$SCRATCHDIR/stats.log target=_blank>Present</a>";

   //////////////////////////////////////////////////////////////
   //STATIONS ACTIVITY
   //////////////////////////////////////////////////////////////
   $CONTENT.="<h2><a name='activity'>Stations Activity</a></h2>";
   $SUBMENU.="<a href='#activity'>Activity</a> | ";
   
  $stationlog="$SCRATCHDIR/stations.log";
  if(file_exists($stationlog)){shell_exec("cp $stationlog $stationlog.prev");}
  $stations=mysqlCmd("select * from Stations",$qout=1);

$CONTENT.=<<<TABLE
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

$CONTENT.=<<<TABLE
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

$CONTENT.=<<<TABLE
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

   //$CONTENT.="<a href=$stationlog.prev target=_blank>Previous</a> | <a href=$stationlog target=_blank>Present</a>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//SEARCH QUAKES
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="search"){

  ////////////////////////////////////////////////////////////////////////
  //SEARCH DATABASE
  ////////////////////////////////////////////////////////////////////////
  $CONTENT.="<h2><a name='search'>Search database</a></h2>";
  $SUBMENU.="<a href='#search'>Search</a> | ";

$CONTENT.=<<<C
<p>
  Use the following form to search on the earthquakes database.
  Queries should be written using
  the <a href="http://www.w3schools.com/sql/" target="_blank">SQL
  syntax</a> as if they started with <i>"select * from
  Quakes..."</i>. Avoid the use of <i>"limit"</i> since it is
  incompatible with the internal command of the search engine.
</p>
<p>
  Use the <b>Examples</b> link to see several examples of how to query
  the database.  The <b>Database</b> link shows you the fields of the
  Earthquakes database.
</p>
C;

  // INPUT
  if(isBlank($offset)){$offset=0;}
  if(isBlank($limit)){$limit=25;}
  if(isBlank($search)){$searchdb="quakeid<>''";} 
  else{$searchdb="quakeid<>'' and $search";}
  $search_url=urlencode($search);

  // SAVE SEARCH HISTORY
  if(!isBlank($search)){
    $fl=fopen("$SCRATCHDIR/history.log","a");
    fwrite($fl,"$DATE;;$searchtxt;;$search\n");
    fclose($fl);
  }

  // SEARCH
  $result=mysqlCmd("select count(quakeid) from Quakes where $searchdb;");
  $numquakes=$result[0];
  if($limit>$numquakes){$limitdb=$numquakes;}
  else{$limitdb=$limit;}
  $quakes=mysqlCmd("select * from Quakes where $searchdb limit $offset,$limitdb;",$qout=1);
  $extra=array();
  if(!isBlank($extracol)){
    $sql="select $extracol from Quakes where $searchdb";
    //echo "SQL=$sql<br/>";
    $extra=mysqlCmd($sql,$qout=1);
    //print_r($extra);
  }

  // GET NEXT
  $offset_prev=$offset-$limit;
  if($offset_prev<0){$offset_prev=1;}
  $offset_next=$offset+$limit;
  if($offset_next>$numquakes){$offset_next=$numquakes-$limit_next;}

  $limit_prev=$limit;
  if(($offset_next+$limit)<=$numquakes){$limit_next=$limit;}
  else{$limit_next=$numquakes-$offset_next;}
  
  $end=$offset+$limit-1;
  $offset_all=$numquakes-$limit+1;

  // CONTROL BUTTONS
  $control=<<<CONTROL
<div style="font-size:10px;padding:10px;">
<a href="?if=search&search=$search_url&offset=0&limit=$limit&extracol=$extracol#quakes"><<</a> 
<a href="?if=search&search=$search_url&offset=$offset_prev&limit=$limit_prev&extracol=$extracol#quakes">Prev</a> ...
<a href="?if=search&search=$search_url&offset=$offset_next&limit=$limit_next&extracol=$extracol#quakes">Next</a>
<a href="?if=search&search=$search_url&offset=$offset_all&limit=$limit&extracol=$extracol#quakes">>></a> 
</div>
CONTROL;

  //EXAMPLES
  $examples_cont="<div id='examples' class='explanation'><h2>Examples</h2><ul>";
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

  //DATABASE FIELDS
  $dbfields="<div id='dbfields' class='explanation'><h2>Database fields</h2>";
  $results=mysqlCmd("describe Quakes",$out=1);
  foreach($results as $field){
    $dbfields.=$field["Field"].", ";
  }
  $dbfields.="</div>";

  //HISTORY
$history=<<<H
<div id='history' class='explanation'>
</div>
H;

  // TABLE HEADER
$CONTENT.=<<<TABLE
$FORM
<table border="0px" cellspacing="0" style="width:100%;margin-left:0px;border:solid black 1px;padding:5px">
  <tr style="font-size:20px">
    <td valign="top" width="20%">Search:<br/>
      <a style="font-size:12px" href="JavaScript:void(null)" onclick="$('#examples').toggle('fast',null)">
	Examples
      </a>,
      <a style="font-size:12px" href="JavaScript:void(null)" onclick="$('#dbfields').toggle('fast',null)">
	Database
      </a>,
      <a style="font-size:12px" href="JavaScript:void(null)" onclick="updateHistory(this);$('#history').toggle('fast',null)">
	History
      </a>
    </td>
    <td valign="top"><input type="text" name="search" size="60" style="line-height:30px;font-size:20px" value="$search" placeholder="Your sql query"></td>
  </tr>
  <tr>
    <td valign="top">Extra columns:</td>
    <td valign="top"><input type="text" name="extracol" size="80" value="$extracol" placeholder="Additional columns"></td>
  </tr>
  <tr>
    <td valign="top">Description of search:</td>
    <td valign="top"><input type="text" name="searchtxt" size="80" value="$searchtxt" placeholder="Description of your query"></td>
  </tr>
  <tr>
    <td valign="top">Earthquakes per page:</td>
    <td valign="top"><input type="text" name="limit" size="5" value=$limit></td>
  </tr>
  <tr>
    <td colspan=2>
      <input type="submit" name="if" value="search">
      <input type="reset" value="clear">
    </td>
  </tr>
</table>
$examples_cont
$dbfields
$history
</form>

<center>
  <h4><a name="quakes">Quakes $offset-$end ($limit/$numquakes)</a></h4>
$control
<table border=1px style="font-size:12px" cellspacing="0px">
<tr class="header">
  <td class="level0">Num.</td>
  <td class="level0">Quake id.</td>
  <td class="level0">Lat.,Lon.</td>
  <td class="level0">Pos. error</td>
  <td class="level0">Depth</td>
  <td class="level0">Date/Time</td>
  <td class="level0">M<sub>l</sub></td>
  <td class="level0">Stations<sup>1</sup></td>
  <td class="level0">Cluster 1<sup>2</sup></td>
  <td class="level0">Location</td>
  <td class="level0">Extra.Col.</td>
  <td class="level2">Status</td>
  <td class="level2">Date status</td>
</tr>
<tr class="header">
  <td class="level0 txt">--</td>
  <td class="level0 txt">--</td>
  <td class="level0 txt">deg.,deg.</td>
  <td class="level0 txt">km, km</td>
  <td class="level0 txt">km&pm;km</td>
  <td class="level0 txt">D/M/YY H:M:S</td>
  <td class="level0 txt">--</td>
  <td class="level0 txt">--</td>
  <td class="level0 txt">--</td>
  <td class="level0 txt">City,Province,Country</td>
  <td class="level0 txt">--</td>
  <td class="level2 txt">--</td>
  <td class="level2 txt">--</td>
</tr>
TABLE;

  $fl=fopen("$SCRATCHDIR/subset.csv","w");
  $qh=1;
  $i=$offset;

  $extrafield=$extra[0];
  $extraval=sqlout2String($extrafield);
  if(isBlank($extraval)){$extraval="-";}

  foreach($quakes as $quake){

    if(isset($extra[$i])){
      //echo "$i defined...<br/>";
      $extrafield=$extra[$i];
      $extraval=sqlout2String($extrafield);
    }

    $fields="";
    $values="";
    foreach(array_keys($quake) as $key){
      if(preg_match("/^\d+$/",$key)){continue;}
      if($qh){
	$fields.="'$key', ";
      }
      $$key=$quake["$key"];
      $values.="'".$$key."', ";
    }
    $fields.="\n";
    $values.="\n";
    if($qh){
      $qh=0;
      fwrite($fl,$fields);
    }
    fwrite($fl,$values);
    $quake_status_txt=$QUAKE_STATUS[$astatus];
    $departamento=preg_replace("/_/"," ",$departamento);
    $municipio=preg_replace("/_/"," ",$municipio);

$CONTENT.=<<<TABLE
  <tr>
    <td class="level0 num">$i</td>
    <td class="level0 txt">
      <a href="?if=quakesimple&quakeid=$quakeid">$quakeid</a><br/>
      <a href="?if=quaketide&quakeid=$quakeid&action=calculate&qpreserve=1&quakeid=$quakeid&qlat=$qlat&qlon=$qlon&qdepth=$qdepth&qdatetime=$qdatetime&qjd=$qjd">tides</a>
    </td>
    <td class="level0 num">$qlat, $qlon</td>
    <td class="level0 num">&pm;$qlaterr,&pm;$qlonerr</td>
    <td class="level0 txt">$qdepth&pm;$qdeptherr</td>
    <td class="level0 num">$qdatetime</td>
    <td class="level0 txt">$Ml</td>
    <td class="level0 txt">$numstations</td>
    <td class="level0 txt">$cluster1</td>
    <td class="level0 txt">$municipio, $departamento, $country</td>
    <td class="level0 txt">$extraval</td>
    <td class="level2 txt">$quake_status_txt</td>
    <td class="level2 txt">$adatetime</td>
  </tr>
TABLE;

    $i++;
  }
  $CONTENT.="</table>$control</center>";
  fclose($fl);

$CONTENT.=<<<C
<p><b>Download</b>:<a href=$SCRATCHDIR/subset.csv>subset.csv</a></p>
<p><b>Notes:</b></p>
<ol>
  <li>
    The present dataset comes from the database compiled by the
    <a href=http://seisan.sgc.gov.co/RSNC target=_blank>Red
    Sismológica Nacional de Colombia</a>.
  </li>
  <li>
    Number of stations that detected the earthquake.
  </li>
  <li>
    Clusters are labeled in this way: 0 means that earthquake is not
    classified in a cluster; [LABEL] is the cluster to which an
    earthquake belong; [-LABEL] is the most intense earthquake in the
    cluster.
  </li>
</ol>
C;

  ////////////////////////////////////////////////////////////////////////
  //LIST OF CALCULATED EARTHQUAKES
  ////////////////////////////////////////////////////////////////////////
$CONTENT.=<<<C
<h2><a name='synthetic'>Synthetic earthquakes</a></h2> 

<p>
  The following table enumerates the synthetic Earthquake data you
  have used to calculate tides at locations, depths and times
  different from that available in the database.
</p>

C;

  $SUBMENU.="<a href='#synthetic'>Synthetic</a> | ";

  $output=shell_exec("cd $SCRATCHDIR;ls -m *.tar");
  $listquakes=preg_split("/\s*,\s*/",$output);
  statusMsg("Synthetic quakes:");

$tablesynth=<<<TABLE
<table border=1px style="font-size:12px" cellspacing="0px">
<tr class="header">
  <td class="level0">Quake id.</td>
  <td class="level0">Lat.,Lon.</td>
  <td class="level0">Depth</td>
  <td class="level0">Date/Time</td>
</tr>
<tr class="header">
  <td class="level0 txt">--</td>
  <td class="level0 txt">deg.,deg.</td>
  <td class="level0 txt">km</td>
  <td class="level0 txt">D/M/YY H:M:S</td>
</tr>
TABLE;

  $i=0;
  foreach($listquakes as $quake){
    if(isBlank($quake)){continue;}
    $parts=preg_split("/\./",$quake);
    $quakeid=$parts[0];
    if(mysqlCmd("select * from Quakes where quakeid='$quakeid'")){continue;}
    statusMsg("Quake $quakeid...");
    $quake=parse_ini_file("$SCRATCHDIR/$quakeid/quake.conf");
    $quakeid=$quake["quakeid"];
    $qlat=$quake["qlat"];
    $qlon=$quake["qlon"];
    $qdepth=$quake["qdepth"];
    $qdatetime=$quake["qdate"]." ".$quake["qtime"];
    $qjd=$quake["qjd"];

$tablesynth.=<<<TABLE
  <tr>
    <td class="level0 txt">
      <a href="?if=quakesimple&quakeid=$quakeid">$quakeid</a><br/>
      <a href="?if=quaketide&quakeid=$quakeid&action=calculate&qpreserve=1&quakeid=$quakeid&qlat=$qlat&qlon=$qlon&qdepth=$qdepth&qdatetime=$qdatetime&qjd=$qjd">tides</a>
    </td>
    <td class="level0 num">$qlat, $qlon</td>
    <td class="level0 txt">$qdepth</td>
    <td class="level0 num">$qdatetime</td>
  </tr>
TABLE;
    $i++;
  }
  $tablesynth.="</table>";
  if($i==0){
    $tablesynth="<i>(No synthetic earthquakes found)</i>";
  }
$CONTENT.=<<<C
<center>
  $tablesynth
</center>
  <p><a href=?if=search&action=cleansynthetic>Clean synthetic earthquakes</a></p>
C;
 
  ////////////////////////////////////////////////////////////////////////
  //UPLOAD EARTHQUAKES
  ////////////////////////////////////////////////////////////////////////
  $CONTENT.="<h2><a name='upload'>Upload earthquakes</a></h2>";
  $SUBMENU.="<a href='#upload'>Upload</a> | ";

$CONTENT.=<<<C
<center><img src="img/menatwork.png" width="10%"/></center>
C;

}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//STATION INFORMATION
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="station"){
  $result=mysqlCmd("select * from Stations where station_id='$station_id'",$qout=1);
  $station=$result[0];
  $CONTENT.="<h3>Station $station_id</h3><ul>";
  foreach(array_keys($station) as $key){
    if(preg_match("/^\d+$/",$key)){continue;}
    $value=$station["$key"];
    $CONTENT.="<li><b>$key</b>: $value</li>";
  }
  $CONTENT.="</ul>";
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//QUAKE SIMPLE INFORMATION
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="quakesimple"){
  
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // RECOVER QUAKE INFO
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  $result=mysqlCmd("select * from Quakes where quakeid='$quakeid'",$qout=1);
  $quake=$result[0];
  
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // FULL INFORMATION
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  $fullinfo="";
  $basicinfo="";
  $noinfo="<li><b>Missing information</b>:";
  foreach(array_keys($quake) as $key){
    if(preg_match("/^\d+$/",$key)){continue;}
    $value=$$key=$quake["$key"];
    if(!isBlank($value)){
      $fullinfo.="<li><b>$key</b>: $value</li>";
    }else{
      $noinfo.="$key, ";
    }
  }
  $noinfo=trim($noinfo,",");
  $noinfo.="</li>";
  
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // BASIC INFO
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  $departamento=preg_replace("/_/"," ",$departamento);
  $municipio=preg_replace("/_/"," ",$municipio);
  $quake_status_txt=$QUAKE_STATUS[$astatus];
$basicinfo.=<<<BASIC
  <li><b>Date and time</b>: $qdatetime</li>
    <li><b>Location</b>: $municipio ($departamento, $country)</li>
  <li><b>Geographic position</b>: lat. $qlat deg.(&pm;$qlaterr km),
  lon. $qlon deg. (&pm;$qlonerr km)</li>
  <li><b>Depth</b>: $qdepth&pm;$qdeptherr km</li>
  <li><b>Status</b>: $quake_status_txt.</li>
  <li><b>Station</b>: $stationid.</li>
BASIC;
  
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // GENERATE MAP
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  $quakedir="$SCRATCHDIR/$quakeid";
  if(!is_dir("$quakedir")){
    shell_exec("mkdir -p $quakedir/");
    shell_exec("cd $quakedir;rm -rf *.py");
    shell_exec("cp $HOMEDIR/$TQUSER/tQuakes/$quakeid.conf $quakedir/quake.conf");
    shell_exec("cp $HOMEDIR/$TQUSER/tQuakes/$quakeid.conf $quakedir");
    shell_exec("cd $quakedir;ln -s ../../../tquakes.py");
    shell_exec("cd $quakedir;ln -s ../../../util");
    shell_exec("cd $quakedir;ln -s ../../../configuration");
  }

  $img=shell_exec("ls $quakedir/quake-map*.png");
  if(isBlank($img)){
    shell_exec("cd $quakedir;cp -r ../../../plots/analysis/quake-map.* .");
    shell_exec("cd $quakedir;PYTHONPATH=. MPLCONFIGDIR=/tmp python quake-map.py");
    $img=shell_exec("ls $quakedir/quake-map*.png");
  }

  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  // RENDER
  // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  $referer=$_SERVER["HTTP_REFERER"];
$SUBMENU.=<<<QUAKE
<a href="$referer">Back</a> | 
QUAKE;
  $SUBMENU.="<a href='$WEBSERVER/?if=quaketide&quakeid=$quakeid&action=calculate&qpreserve=1&qlat=$qlat&qlon=$qlon&qdepth=$qdepth&qdatetime=$qdatetime&qjd=$qjd'>Tides</a>";
  
  preg_match("/__([^\.]+).png/",$img,$matches);
  $plotmd5=$matches[1];
  $plotfigure=generateFigure($quakedir,"quake-map",$plotmd5,
			     /*Description*/"",
			     /*figure style*/"float:right;width:50%;",
			     /*img style*/"",
			     /*figcaption style*/"");

$CONTENT.=<<<QUAKE

  $plotfigure

<h3>Earthquake $quakeid</h3>

<h4>Basic information</h4>
<ul>
  $basicinfo
</ul>

<h4>Full information</h4>
<ul style="width:80%;word-wrap:break-word">
  $fullinfo
  $noinfo
</ul>

<h4>Notes:</h4>
<ul>
  <li>
    <b>qsignal</b> value of the signal for each component.  Values are
    sorted in this way: gravitational acceleration (symbol gt,
    comp. num. 0, nm/s<sup>2</sup>), tidal tilt (t, 1, mas), vertical
    displacement (vd, 2, mm), vertical strain (vs, 3, corresponding to
    esp_zz, nstr), horizontal strain at azimuth 0 (hs0, 4, eps_qq,
    nstr), horizontal strain at azimuth 90 degrees (hsn, 5, esp_ll,
    nstr).
  </li>
  <li>
    <b>qphases</b> contain all the phases for every single component
    in the format: [fourier_phase1_sd]; [fourier_phase1_d];
    [fourier_phase1_fn]; [fourier_phase1_mn]; [time1_sd]:[phase1_sd];
    [time1_sd]:[phase1_sd]; [time1_d]:[phase1_d];
    [time1_fn]:[phase1_fn]; [time1_mn]:[phase1_mn]; where "sd" is
    semidiurnal, "d" is diurnal, "fn" is fornightly (~15 days) and
    "mn" is monthly.  For each component there is a set of fourier and
    time phases in the format above.
  </li>
</ul>
QUAKE;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//QUAKE TIDES
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="quaketide"){
  
  // RECOVER QUAKE INFO
  if(isset($quakeid)){
    $result=mysqlCmd("select * from Quakes where quakeid='$quakeid'",$qout=1);
    $quake=$result[0];
    
    foreach(array_keys($quake) as $key){
      if(preg_match("/^\d+$/",$key)){continue;}
      $value=$$key=$quake["$key"];
    }
    $departamento=preg_replace("/_/"," ",$departamento);
    $municipio=preg_replace("/_/"," ",$municipio);
  }

  // SUBMENU
  if(!isset($referer)){
    $referer=$_SERVER["HTTP_REFERER"];
  }
  
  if(!isset($qjd)){$qjd="<i style='font-size:10px;color:gray'>Enter the Date and time...</i>";}

$SUBMENU.=<<<QUAKE
<a href="$referer">Back</a> |
QUAKE;

$CONTENT.=<<<QUAKE
<h2>Earthquake Tides</h2>

<p>
  Use this form to modify or create new earthquake location and time
  in order to calculate tides.  Use the "calculate" button if you only
  want to get basic information about tides (signal value, tidal
  phases, etc.).  Use the "plot" button to get plots of the tidal
  timeseries and other related graphs.
</p>

<h3>Basic properties</h3>
$FORM
<table border=0px>
<tr>
  <td>Quake id.:</td>
  <td>
    <input id="quakeid" type="text" name="quakeid" value="$quakeid" placeholder="Wait for it..." readonly>
  </td>
</tr>
<tr>
  <td>Latitude:</td>
  <td>
    <input type="text" name="qlat" value="$qlat">
  </td>
</tr>
<tr>
  <td>Longitude:</td>
  <td>
    <input type="text" name="qlon" value="$qlon">
  </td>
</tr>
<tr>
  <td>Depth (km):</td>
  <td>
    <input type="text" name="qdepth" value="$qdepth">
  </td>
</tr>
<tr>
  <td valign="top">
    Date and time:<br/>
    <i style="font-size:10px">D/MM/YY HH:MM:SS</i>
  </td>
  <td valign="top">
    <input type="text" name="qdatetime" value="$qdatetime" onchange="updateJD(this)">
  </td>
</tr>
<tr>
  <td valign="top">
    Julian Day:
  </td>
  <td valign="top">
    <span id="qjd">$qjd</span>
  </td>
</tr>
<tr>
<td colspan=2>
<input type="submit" name="action" value="calculate">
<input type="submit" name="action" value="plot">
<input type="reset" value="reset">
</td>
</tr>
</table>
<input type="hidden" name="referer" value="$referer">
<input type="hidden" name="qpreserve" value="$qpreserve">
</form>
$tideresults
QUAKE;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//QUAKE INFORMATION
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
    <li><b>Location</b>: $municipio ($departamento, $country)</li>
  <li><b>Geographic position</b>: lat. $qlat deg., lon. $qlon deg.</li>
  <li><b>Depth</b>: $qdepth km</li>
  <li><b>Status</b>: $quake_status_txt.</li>
  <li><b>Station</b>: $stationid.</li>
BASIC;
  
  // DOWNLOAD
  $dirquakes="$HOMEDIR/$TQUSER/tQuakes/";
  $filequake=$dirquakes."$quakeid-eterna.tar.7z";
  if(file_exists($filequake)){

    //REMOVE PREVIOUS DOWNLOAD QUAKES
    //shell_exec("rm -r $SCRATCHDIR/*"); //ONLY IF YOU WANT TO PRESERVE

    //CREATE QUAKE ID
    $quakedir="$SCRATCHDIR/$quakeid";
    if(!is_dir("$quakedir") or isset($replotall) or 0){
      $CONTENT.="<i>Creating directory for $quakeid...</i><br/>";
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
    <li><a href="plot.php?replot&plot=$plot">Replot</a></li>
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

$SUBMENU.=<<<QUAKE
<a href="$referer">Back</a> |
<a href="index.php?if=quake&quakeid=$quakeid&replotall">Replot all</a>
QUAKE;

$CONTENT.=<<<QUAKE
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
<ul style="width:80%;word-wrap:break-word">
  $fullinfo
</ul>
QUAKE;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//REGISTER STATION
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else if($if=="register"){

  $delete="";
  if(!isset($station_name)){$station_name="SEAP UdeA";}
  if(!isset($station_email)){$station_email="seapudea@gmail.com";}
  if(isset($station_id)){
	$station_key=shell_exec("cat stations/$station_id/key.pub");
	$delete="<input type=submit name=action value=remove>";
  }
  if(!isset($station_receiving)){$station_receiving="0";}
  if(!isset($station_status)){$station_status="0";}
  
$CONTENT.=<<<C
<h2>Register a new station</h2>
<p>
  Use the following form to register or remove a calculation station.
  In order to register your station you need to download and install
  it (see <a href=?if=download>download</a> section).
</p>
<form action="index.php" method="post" enctype="multipart/form-data" accept-charset="utf-8">
  <input type=hidden name=if value=register>
  <table border=0px>
    <tr>
      <td valign=top>Station ID:</td>
      <td><input type=text name=station_id maxlength=14 size=20 value="$station_id" placeholder="Alphanumerical code"></td>
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
    <tr class="level3">
      <td valign=top>Receiving:</td>
      <td><input type=text name=station_receiving value="$station_receiving"></td>
    </tr>
    <tr class="level3">
      <td valign=top>Status:</td>
      <td><input type=text name=station_status value="$station_status"></td>
    </tr>
    <tr>
      <td valign=top colspan=2>
	<input type=submit name=action value=register> $delete
      </td>
    </tr>
  </table>
</form>
C;

  //LIST OF STATIONS
  $stations=mysqlCmd("select * from Stations",$qout=1);

$stationstxt=<<<T
<table border=1px cellspacing=0px>
<tr>
  <td class="level0">#</td>
  <td class="level0">Station ID</td>
  <td class="level0">Name</td>
  <td class="level3">E-mail</td>
  <td class="level3">Receiving</td>
  <td class="level3">Links</td>
</tr>
T;
  $i=1;
  foreach($stations as $station){
    $urlstring="";
    foreach(array_keys($station) as $key){
      $$key=$station["$key"];
      $urlstring.="$key=".$$key."&";
    }
$stationstxt.=<<<T
<tr>
  <td class="level0">$i</td>
  <td class="level0">$station_id</td>
  <td class="level0 txt">$station_name</td>
  <td class="level3 txt">$station_email</td>
  <td class="level3 txt">$station_receiving</td>
  <td class="level3 txt">
    <a href="?if=register&$urlstring">Edit</a>
  </td>
</tr>
T;
    $i++;
  }
  $stationstxt.="</table>";

$CONTENT.=<<<C
<h3>Available stations</h3>
<p>
  These are the available calculation stations for this server:
</p>
$stationstxt
C;
}

//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//HOME
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
else{
$CONTENT.=<<<C

<figure style="float:right;right:0px;width:35%;">	       
  <img src="img/tquakes-colombia.png" width="100%">
  <figcaption>Scatter plot of the earthquakes at and around Colombia</figcaption>
</figure>

<p style="font-size:2em">
  Welcome to $tQuakes!
</p>

<p>
</p>

<p>
  $tQuakes is a project of the <b>Solar, Earth and Planetary Physics
  Group (SEAP)</b> of the <a href=bit.ly/if-udea-website>Institute of
  Physics</a> (<a href=http://www.udea.edu.co>University of
  Antioquia</a>) in Medellin (Colombia), in collaboration with the
  Colombia's National University.
</p>

<p>
  $tQuakes (Earthquakes and Tides) is an <b>information platform</b>
  intended to explore the relationship between the lunisolar tides and
  the triggering of earthquakes.  It combines a <b>huge (and growing)
  database</b> of Earthquakes around the globe, with a <b>specialized
  set of analytical tools</b> able to filter, analyse and perform
  advanced graphical representations of the earthquake dataset and other
  analytical products obtained from them.  
</p>

<p>
  But $tQuakes is not only a databased with some related analytical
  products.  It also provide on-line computational capabilities,
  provided by an scalable <b>scavenging grid</b> of Linux servers,
  able to speed-up the complex analysis required to study the
  potential relationship between tides and seismicity.
</p>

<p>
  In this site you will find or be able to:

  <ul>

    <li>
      <a href=?if=search>Browse the Earthquakes database</a>. Detailed
      information about each earthquake is provided (location by
      coordinates, location by city, province and country, magnitude,
      depth date and time, etc.).  You will be able to perform simple
      and advanced queries on the database and download subsets.
    </li>

    <li>
      <a href=?if=search>Information on tides at earthquakes location
      and time</a>. Get information about tides at the times when the
      earthquakes in database happen.  Here you will find
      precalculated values and phases of tides for most of the
      earthquakes in our database.  $tQuakes provide values and phases
      for the most important phase components (vertical displacement,
      gravitational acceleration, horizontal and vertical strain,
      etc.)
    </li>

    <li>
      <a href=?if=calculate>Calculate tides at any location and
      time</a>. We provide a simple web interface to ETERNA, a
      software to calculate solid tides provided location, depth and
      tiem.
    </li>

    <li>
      <a href=?if=data>Access to analytical products</a>. Database
      administrators perform analysis on the database to study the
      statistical correlation between seismicity and tides.  Here you
      will find some analytical products for the database.
    </li>

    <li>
      <a href=?if=download>Download tQuakes</a>. $tQuakes is an open
      source project.  You may download the full $tQuakes server,
      including a previously feed database or the $tQuakes working
      station if you want to provide computing time to the project.
    </li>

    <li>
      <a href=?if=references>Get a complete list of references in the
      field</a>. We provide here the most complete list of peer
      reviewed papers, books, thesis and other documents related
      directly or indirectly to the investigation on the possible
      connection between tides and seismic activity.
    </li>
  </ul>
</p>
$CITATE
C;
}

//======================================================================
//END
//======================================================================
?>
<?php
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//STATUS MESSAGE
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
$MSG="";
/*
if(strlen($STATUS)){
$MSG.=<<<M
  <div class="status">
  $STATUS
  </div>
M;
}
if(strlen($ERRORS)){
$MSG.=<<<M
  <div class="errors">
  $ERRORS
  </div>
M;
}
*/
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//USER
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
if($QPERM>0){
  $NAME=$_SESSION["uname"];
$USER=<<<U
<p class='menuitem'>
$NAME<br/>
<a href='?action=logout'>Logout</a></p>
U;
}else{
$urlref=urlencode($_SERVER["REQUEST_URI"]);
$USER=<<<U
<p class='menuitem'><a href='?if=user&urlref=$urlref'>User</a></p>
U;
}
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
//CONTENT
//&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
$navstyle="";
if(!isBlank($SUBMENU)){
$navstyle="style='border-bottom:solid black 1px'";
}
echo<<<CONTENT
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
    <script src="site/jquery.js"></script>
    <script src="site/tquakes.js"></script>
    <link rel="stylesheet" type="text/css" href="site/tquakes.css"/>
    <style>
      $PERMCSS
    </style>
  </head>

  <body>
    $MSG
    <div style="background:lightgray;width:100%;height:95%">
    <header>
      <a href=$WEBSERVER><img class="tquakes" src="img/tquakes.png" style="height:100%"/></a>
      <img class="logogroup" src="img/LogoSEAP-White.jpg" align="middle"/>
    </header>
    <section>
      <span class="level0"><p class="menuitem"><a href="?">Home</a><hr/></p></span>
      <span class="level0"><p class="menuitem"><a href="?if=search">Earthquakes</a><hr/></p></span>
      <span class="level0"><p class="menuitem"><a href="?if=quaketide">Tides</a><hr/></p></span>
      <span class="level0"><p class="menuitem"><a href="?if=data">Products</a><hr/></p></span>
      <span class="level0"><p class="menuitem"><a href="?if=download">Download</a><hr/></p></span>
      <span class="level0"><p class="menuitem"><a href="?if=register">Station</a><hr/></p></span>
      <span class="level0"><p class="menuitem"><a href="?if=references">References</a><hr/></p></span>
      $USER
      <hr/>
      <span class="level2"><p class="menuitem"><a href="?if=stations">Computing Stations</a><hr/></p></span>
    </section>
    <aside>
      <nav $navstyle>
	$SUBMENU
      </nav>
      $CONTENT
    </aside>
    <div class="placebar">
      <b>Status bar</b><hr/>
      <span style=color:black>
	$STATUS
      </span>
      <span style=color:red>
	$ERRORS
      </span>
    </div>
    </div>
    <footer>
      <i>
	Developed by Jorge I. Zuluaga (2015) - sessid: $SESSID
      </i>
    </footer>
  </body>
</html>
CONTENT;
?>
