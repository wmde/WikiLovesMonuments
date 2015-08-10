<?php

use Silex\Application;
use Symfony\Component\HttpFoundation\Response;

require __DIR__.'/vendor/autoload.php';


$app = new Application();

$app->get( "/", function() {
	return "WLM redirect script";
} );

$app->get( "/redirect/{pageName}/{id}/{campaign}/{lat}/{lon}",
	function ( Application $app, $pageName, $id, $campaign, $lat, $lon ){
		return $app->redirect( "http://example.com/", Response::HTTP_MOVED_PERMANENTLY );
	} )
	->assert( 'campaign', '[-a-z]+')
	->value( 'lat', '' )
	->value( 'lon', '' );
return $app;
