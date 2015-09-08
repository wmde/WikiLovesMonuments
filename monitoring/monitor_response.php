#!/usr/bin/php -q
<?php
/**
 * Monitoring script to check if the forward script is working.
 */

include __DIR__ . '/config.php';

/**
 * Send notification mail if notification interval is exceeded.
 *
 * @param string $email
 * @param string $subject
 * @param string $body
 * @param int $notificationInterval Number of seconds between notifications
 */
function notifyConditionally( $email, $subject, $body, $notificationInterval ) {
	$lastNotify = __DIR__ . '/monitor_response.lastnotify.txt';
	if ( mustNotify( $lastNotify, $notificationInterval ) ) {
		$lines = [$email, $subject, $body];
		file_put_contents( $lastNotify, implode( "\n", $lines ) );
		mail( $email, $subject, $body );
	}
}

/**
 * Check if the notification mail should be sent by examining the modification date of the file.
 *
 * @param string $filename
 * @param int $notificationInterval
 * @return bool
 */
function mustNotify( $filename, $notificationInterval ) {
	if ( !file_exists( $filename ) ) {
		return true;
	}
	$currentInterval = time() - filemtime( $filename );
	return $currentInterval > $notificationInterval;
}

/**
 * Check if the HTTP code is a redirect and if the response headers contain the expected location
 * @param int $httpCode
 * @param string $response
 * @param string $expectedLocation
 * @return bool
 */
function resultHasErrors( $httpCode, $response, $expectedLocation ) {
	return $httpCode !== 301 ||
		$response === false ||
		stripos( $response, "Location: $expectedLocation" ) === false;
}

$ch = curl_init( $checkURL );

curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
curl_setopt( $ch, CURLOPT_HEADER, true );
curl_setopt( $ch, CURLOPT_NOBODY, true );
curl_setopt( $ch, CURLOPT_USERAGENT, 'WLM monitoring script' ); // Tool labs refuses connections without UA

$response = curl_exec( $ch );

$httpCode = curl_getinfo( $ch, CURLINFO_HTTP_CODE );
if ( resultHasErrors( $httpCode, $response, $expectedLocation ) ) {
    $errorMessage = "Got the following result back:\n\n$response";
	$errorMessage .= 'CURL error: ' . curl_error( $ch );
    notifyConditionally(
		$notifyMail,
		"$subjectPrefix Forward script check failed",
		$errorMessage,
		$notificationInterval
	);
}

curl_close( $ch );
