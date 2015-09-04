<?php

$checkPatterns = [
    '/\s+commonsbot\s+/' => 'Commons Bot'
];
$notifyMail = 'gabriel.birke@wikimedia.de';
$subjectPrefix = '[WLM-Monitor]';

$result = exec('qstat', $output, $returnVar);

foreach ( $checkPatterns as $checkPattern => $description ) {
    if ( !preg_match( $checkPattern, $result ) ) {
        $errmsg = "$description is not found in qstat, please check.\n" ;
        mail( $notifyMail, "$subjectPrefix $description is not running", $errmsg );
    }
}
