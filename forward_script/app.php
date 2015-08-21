<?php

use Silex\Application;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\RuntimeException as ProcessException;
use Wikimedia\ForwardScript\PageInformationCollector;
use Wikimedia\ForwardScript\ApplicationException;
use Wikimedia\ForwardScript\ErrorResponse;

require __DIR__.'/vendor/autoload.php';


$app = new Application();

// Settings
$app['cache_dir'] = __DIR__.'/cache';
$app['commons_api_url'] = 'https://commons.wikimedia.org/w/api.php';
$app['wikipedia_api_url'] = 'https://de.wikipedia.org/w/api.php';
$app['python_path'] = realpath( __DIR__ . '/../update-bot/' );
$app['default_categories_config'] = $app['python_path'] . '/config/commonscat_mapping.json';
$app['pageinfo_script'] = 'python -m wlmbots.pageinfo';
$app['commons_upload_url'] = 'https://commons.wikimedia.org/wiki/Special:UploadWizard?';

// Services
$app['cache'] = $app->share( function ( $app ) {
	return new \Doctrine\Common\Cache\FilesystemCache( $app['cache_dir'] );
} );
$app['commons_api'] = $app->share( function ( $app ) {
	return new \Mediawiki\Api\MediawikiApi( $app[ 'commons_api_url' ] );
} );
$app['wikipedia_api'] = $app->share( function ( $app ) {
	return new \Mediawiki\Api\MediawikiApi( $app[ 'wikipedia_api_url' ] );
} );
$app['campaign_validator'] = $app->share( function ( $app ) {
	return new \Wikimedia\ForwardScript\CampaignValidator( $app[ 'commons_api' ] );
} );
$app['pageinfo'] = $app->share( function ( $app ) {
	$defaultCategories = json_decode( file_get_contents( $app['default_categories_config'] ), true );
	$process = new Process( $app['pageinfo_script'], $app['python_path'] );
	return new PageInformationCollector( $app[ 'wikipedia_api' ], $process, $defaultCategories );
} );
$app->register( new Silex\Provider\MonologServiceProvider(), array(
	'monolog.logfile' => __DIR__.'/app_errors.log',
	'monolog.level' => 'WARNING'
) );

// Error handling
$app->error( function ( ApplicationException $e, $code ) use ( $app ) {
	return new ErrorResponse( $e->getMessage() );
} );

$app->error( function ( ProcessException $e, $code ) use ( $app ) {
	return new ErrorResponse( $e->getMessage() );
} );

// Routes
$app->get( '/', function() {
	return 'WLM redirect script';
} );

$app->get( '/redirect/{pageName}/{campaign}',
	function ( Application $app, Request $request, $pageName, $campaign ) {
		$campaignCacheId = "campaign_{$campaign}";
		if ( $app['cache']->contains( $campaignCacheId ) ) {
			$campaignIsValid = $app['cache']->fetch( $campaignCacheId );
		}
		else {
			$campaignPageName = 'Campaign:'.preg_replace( '/^Campaign:/', '', $campaign );
			$campaignIsValid = $app['campaign_validator']->isValidCampaign( $campaignPageName );
			$cacheTime = $campaignIsValid ? 604800 : 300;
			$app['cache']->save( $campaignCacheId, $campaignIsValid, $cacheTime );
		}
		if ( !$campaignIsValid ) {
			throw new ApplicationException( 'Invalid campaign name.' );
		}
		$id = $request->get( 'id', '' );
		$pageInfo = $app['pageinfo']->getInformation( $pageName, $id );
		$coordinates = [
			'lat' => $request->get( 'lat', '' ),
			'lon' => $request->get( 'lon', '' ),
		];
		$queryBuilder = new \Wikimedia\ForwardScript\QueryBuilder();
		$redirectUrl = $app['commons_upload_url'];
		$redirectUrl .= 'campaign='.urlencode( $campaign );
		$redirectUrl .= $queryBuilder->getQuery( $pageInfo, $pageName, $id, $coordinates );
		return $app->redirect( $redirectUrl, Response::HTTP_MOVED_PERMANENTLY );
	} );

return $app;
