#!/usr/bin/php -q
<?php
/**
 * Monitoring script to check if the forward script is working.
 */

include __DIR__ . '/config.php';

$ch = curl_init( $checkURL );

curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
curl_setopt( $ch, CURLOPT_HEADER, true );
curl_setopt( $ch, CURLOPT_NOBODY, true );
curl_setopt( $ch, CURLOPT_USERAGENT, "WLM monitoring script" ); // Tool labs refuses connections without UA

$response = curl_exec( $ch );

// TODO check for timeout

$httpCode = curl_getinfo( $ch, CURLINFO_HTTP_CODE );
if ( $httpCode !== 301 || stripos( $response, "Location: $expectedLocation" ) === false ) {
    $errmsg = "Got the following result back:\n\n$response";
    mail( $notifyMail, "$subjectPrefix Forward script check failed", $errmsg );
}

curl_close( $ch );
