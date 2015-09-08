<?php

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
