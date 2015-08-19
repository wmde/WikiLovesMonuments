<?php

// Remove prefix on tool labs to make our routes work behind the reverse proxy
if ( !empty( $_SERVER['HTTP_X_ORIGINAL_URI'] ) ) {
	foreach ( ['HTTP_X_ORIGINAL_URI', 'REQUEST_URI'] as $serverVar ) {
		$_SERVER[$serverVar] = preg_replace( "!^/wlm-de-utils!", '', $_SERVER[$serverVar] );
	}
}

$app = require __DIR__ . '/../app.php';

$app->run();
