<?php

header('Content-Type: application/json'); 

if(!isset($_REQUEST['i']) || !isset($_REQUEST['c'])){
    return '[]';
}

$guid = $_REQUEST['i'];
$c = $_REQUEST['c'];

$salt = hash('sha1', strrev(substr($guid, 0, -4))); 
$d = hash('md5', $salt . $guid);

//make sure that the hashes match
if($d != $c){ 
    return '[]';
} 

$redis = new Redis();
$redis->pconnect('localhost');
$ips = $redis->sMembers($guid);

echo json_encode($ips);

?>
