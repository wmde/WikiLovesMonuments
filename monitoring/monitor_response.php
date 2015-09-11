#!/usr/bin/php -q
<?php
/**
 * Monitoring script to check if the forward script is working.
 */

include __DIR__ . '/config.php';
require __DIR__ . '/functions.php';

$ch = curl_init( $checkURL );

curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
curl_setopt( $ch, CURLOPT_HEADER, true );
curl_setopt( $ch, CURLOPT_NOBODY, true );
curl_setopt( $ch, CURLOPT_USERAGENT, 'WLM monitoring script' ); // Tool labs refuses connections without UA

$response = curl_exec( $ch );

$httpCode = curl_getinfo( $ch, CURLINFO_HTTP_CODE );
list( $resultHasError, $errorReason ) = resultHasErrors( $httpCode, $response, $expectedLocation );
if ( $resultHasError ) {
	$errorMessage = "Error: $errorReason\n\n";
	$errorMessage .= "Got the following result back:\n\n$response";
	$curlError = curl_error( $ch );
	if ( $curlError ) {
		$errorMessage .= "\nCURL error: $curlError\n";
	}
	notifyConditionally(
		$notifyMail,
		"$subjectPrefix Forward script check failed",
		$errorMessage,
		$notificationInterval
	);
}

curl_close( $ch );
