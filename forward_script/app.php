<?php

use Silex\Application;
use Symfony\Component\HttpFoundation\Response;

require __DIR__.'/vendor/autoload.php';


$app = new Application();

$app["cache_dir"] = __DIR__."/cache";
$app["cache"] = $app->share( function ( $app ) {
	return new \Doctrine\Common\Cache\FilesystemCache( $app["cache_dir"] );
} );
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
		$campaignCacheId = "campaign_{$campaign}";
		if ( $app["cache"]->contains( $campaignCacheId ) ) {
			$campaignIsValid = $app["cache"]->fetch( $campaignCacheId );
		}
		else {
			$campaignIsValid = $app["campaign_validator"]->isValidCampaign( $campaign );
			$cacheTime = $campaignIsValid ? 604800 : 300;
			$app["cache"]->save( $campaignCacheId, $campaignIsValid, $cacheTime );
		}
		if ( !$campaignIsValid ) {
			throw new RuntimeException( "Invalid campaign name." );
		}
		return $app->redirect( "http://example.com/", Response::HTTP_MOVED_PERMANENTLY );
	} )
	->assert( 'campaign', '[-a-z]+' )
	->value( 'lat', '' )
	->value( 'lon', '' );
return $app;
