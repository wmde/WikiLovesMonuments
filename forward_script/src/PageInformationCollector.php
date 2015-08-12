<?php

namespace Wikimedia\ForwardScript;

use Mediawiki\Api\MediawikiApi;
use Mediawiki\Api\SimpleRequest;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\RuntimeException;
use Wikimedia\ForwardScript\ApplicationException;

/**
 * Get page content and categories from Wikipedia, return information about the page.
 *
 * @package Wikimedia\ForwardScript
 */
class PageInformationCollector {

	/**
	 * @var MediawikiApi
	 */
	protected $api;

	/**
	 * @var Process
	 */
	protected $processCommand;

	/**
	 * @var array
	 */
	protected $defaultCategories;

	public function __construct( MediawikiApi $api, Process $processCommand, $defaultCategories=[] ) {
		$this->api = $api;
		$this->processCommand = $processCommand;
		$this->defaultCategories = $defaultCategories;
	}

	public function getInformation( $pageTitle, $monumentId ) {
		$response = $this->api->getRequest( new SimpleRequest( "query", array(
			'titles' => $pageTitle,
			'prop' => 'categories|revisions',
			'rvprop' => 'content'
		) ) );
		$firstPage = array_values( $response[ "query" ][ "pages" ] )[ 0 ];
		if ( isset( $firstPage[ "missing" ] ) ) {
			throw new ApplicationException( "Page '$pageTitle' not found." );
		}
		if ( isset( $firstPage[ "invalid" ] ) ) {
			throw new ApplicationException( "Page name is invalid." );
		}
		$firstRevision = $firstPage["revisions"][0];
		if ( $firstRevision["contentformat"] !== "text/x-wiki" ) {
			throw new ApplicationException( "Page is not a wiki text page." );
		}
		$this->processCommand->setInput( $firstRevision["*"] );
		$monumentIdParam = ' ' . escapeshellarg( $monumentId );
		$this->processCommand->setCommandLine(
			$this->processCommand->getCommandLine() . $monumentIdParam
		);
		$this->processCommand->run();
		if ( !$this->processCommand->isSuccessful() ) {
			throw new RuntimeException( $this->processCommand->getErrorOutput() );
		}

		$info = json_decode( $this->processCommand->getOutput() );
		$this->determineCategory( $info, $firstPage["categories"] );
		return $info;
	}

	protected function determineCategory( $info, $pageCategories ) {
		if ( !empty( $info->category ) ) {
			return;
		}
		foreach ( $pageCategories as $categoryInfo ) {
			if ( !empty( $this->defaultCategories[$categoryInfo["title"]] ) ) {
				$info->category = $this->defaultCategories[$categoryInfo["title"]];
				return;
			}
		}
		throw new ApplicationException( "No valid category found for page." );
	}


}
