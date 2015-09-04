<?php
/**
 * Monitoring script to check if the forward script is working.
 */

$checkURL = 'https://tools.wmflabs.org/wlm-de-utils/redirect/Benutzer%3AGabriel+Birke+%28WMDE%29%2FDemo+Liste+Baudenkmale+Bad+Wiessee/wlm-de-by?id=D-1-82-111-30&lat=11.70699&lon=47.73638';
$expectedLocation = 'https://commons.wikimedia.org/wiki/Special:UploadWizard';
$notifyMail = 'gabriel.birke@wikimedia.de';
$subjectPrefix = '[WLM-Monitor]';

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
