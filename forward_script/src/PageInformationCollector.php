<?php

namespace Wikimedia\ForwardScript;

use Mediawiki\Api\MediawikiApi;
use Mediawiki\Api\SimpleRequest;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\RuntimeException;

/**
 * Get page content and categories from Wikipedia, return information about the page.
 *
 * @package Wikimedia\ForwardScript
 */
class PageInformationCollector {

	/**
	 * @var MediawikiApi
	 */
	private $api;

	/**
	 * @var Process
	 */
	private $processCommand;

	/**
	 * @var array
	 */
	private $defaultCategories;

	public function __construct( MediawikiApi $api, Process $processCommand, array $defaultCategories=[] ) {
		$this->api = $api;
		$this->processCommand = $processCommand;
		$this->defaultCategories = $defaultCategories;
	}

	/**
	 * Get information about page categories and the monument ID.
	 *
	 * @param string $pageTitle
	 * @param string $monumentId
	 * @return PageInformation
	 */
	public function getInformation( $pageTitle, $monumentId ) {
		list( $content, $categories ) = $this->getPageContentAndCategoriesFromAPI( $pageTitle );
		$info = $this->getInformationFromProcess( $content, $monumentId );
		if ( empty( $info->category ) ) {
			$info->category = $this->determineCategory( $categories );
		}
		return new PageInformation( $info );
	}

	/**
	 * Query the MediaWiki API for page content and categories
	 *
	 * @param string $pageTitle
	 * @return array
	 */
	private function getPageContentAndCategoriesFromAPI( $pageTitle ) {
		$response = $this->api->getRequest( new SimpleRequest( 'query', array(
			'titles' => $pageTitle,
			'prop' => 'categories|revisions',
			'rvprop' => 'content'
		) ) );
		$firstPage = array_values( $response[ 'query' ][ 'pages' ] )[ 0 ];
		$this->validatePage( $firstPage );
		$firstRevision = $firstPage['revisions'][0];
		if ( $firstRevision['contentformat'] !== 'text/x-wiki' ) {
			throw new ApplicationException( 'Page is not a wiki text page.' );
		}
		$categories = empty( $firstPage['categories'] ) ? [] : $firstPage['categories'];
		return [$firstRevision['*'], $categories];
	}

	/**
	 * Check if the API result for a page contains markers for missing or invalid pages.
	 *
	 * @param array $page
	 */
	private function validatePage( array $page ) {
		if ( isset( $page[ 'missing' ] ) ) {
			throw new ApplicationException( "Page {$page['title']} not found." );
		}
		if ( isset( $page[ 'invalid' ] ) ) {
			throw new ApplicationException( 'Page name is invalid.' );
		}
	}

	/**
	 * Call the Python script with the monument ID and the page text to get information
	 * about page categories and the monument ID.
	 *
	 * @param string $pageContent
	 * @param string $monumentId
	 * @return object
	 */
	private function getInformationFromProcess( $pageContent, $monumentId ) {
		$this->processCommand->setInput( $pageContent );
		$monumentIdParam = $monumentId ? ' -i ' . escapeshellarg( $monumentId ) : '';
		$this->processCommand->setCommandLine(
			$this->processCommand->getCommandLine() . $monumentIdParam
		);
		$this->processCommand->run();
		if ( !$this->processCommand->isSuccessful() ) {
			throw new RuntimeException( $this->processCommand->getErrorOutput() );
		}
		return json_decode( $this->processCommand->getOutput() );
	}

	/**
	 * Map one of the configured default categories to the page category.
	 *
	 * This is the fallback method when the Python script doesn't return a category
	 * (because there was no usable one in the page text).
	 *
	 * @param array $pageCategories
	 * @return string
	 */
	private function determineCategory( array $pageCategories ) {
		foreach ( $pageCategories as $categoryInfo ) {
			if ( !empty( $this->defaultCategories[$categoryInfo['title']] ) ) {
				return $this->defaultCategories[$categoryInfo['title']];
			}
		}
		throw new ApplicationException( 'No valid category found for page.' );
	}


}
