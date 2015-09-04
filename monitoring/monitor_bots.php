#!/usr/bin/php -q
<?php
/**
 * Use the output of the 'qstat' tool to check if the bots are running.
 */

include __DIR__ . '/config.php';

$result = exec('qstat', $output, $returnVar);

foreach ( $checkPatterns as $checkPattern => $description ) {
    if ( !preg_match( $checkPattern, $result ) ) {
        $errmsg = "$description is not found in qstat, please check.\n" ;
        mail( $notifyMail, "$subjectPrefix $description is not running", $errmsg );
    }
}
