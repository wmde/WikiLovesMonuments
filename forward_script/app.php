<?php

use Silex\Application;
use Symfony\Component\HttpFoundation\Response;

require __DIR__.'/vendor/autoload.php';


$app = new Application();

$app["commons_api_url"] = "https://commons.wikimedia.org/w/api.php";
$app["commons_api"] = $app->share( function ( $app ) {
	return new \Mediawiki\Api\MediawikiApi( $app[ "commons_api_url" ] );
} );
$app["campaign_validator"] = $app->share( function ( $app ) {
	return new \Wikimedia\ForwardScript\CampaignValidator( $app[ "commons_api" ] );
} );

$app->get( "/", function() {
	return "WLM redirect script";
} );

$app->get( "/redirect/{pageName}/{id}/{campaign}/{lat}/{lon}",
	function ( Application $app, $pageName, $id, $campaign, $lat, $lon ) {
		if ( !$app["campaign_validator"]->isValidCampaign( $campaign ) ) {
			throw new RuntimeException( "Invalid campaign name." );
		}
		return $app->redirect( "http://example.com/", Response::HTTP_MOVED_PERMANENTLY );
	} )
	->assert( 'campaign', '[-a-z]+' )
	->value( 'lat', '' )
	->value( 'lon', '' );
return $app;
