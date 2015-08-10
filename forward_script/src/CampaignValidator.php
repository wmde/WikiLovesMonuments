<?php


namespace Wikimedia\ForwardScript;

use Mediawiki\Api\MediawikiApi;
use Mediawiki\Api\SimpleRequest;

/**
 * Checks if a given campaign name exists.
 *
 * This should only be used on Wikis where the "Campaign" namespace exists and has the ID 460.
 * It is intended for use with Wikimedia Commons.
 *
 * @package Wikimedia\ForwardScript
 */
class CampaignValidator
{

	const CAMPAIGN_NAMESPACE = 460;

	/**
	 * @var MediawikiApi
	 */
	protected $api;

	function __construct( MediawikiApi $api ) {

		$this->api = $api;
	}

	/**
	 * Check if the campaign exists and if it is in the "Campaign:" namespace.
	 *
	 * @param string $campaignName
	 * @return bool
	 */
	public function isValidCampaign( $campaignName ) {

		$response = $this->api->getRequest( new SimpleRequest( "query", array(
			'titles' => $campaignName,
		) ) );
		$firstPage = array_values( $response[ "query" ][ "pages" ] )[ 0 ];
		if ( empty( $firstPage[ "ns" ] ) || $firstPage[ "ns" ] != self::CAMPAIGN_NAMESPACE ) {
			return false;
		}
		if ( isset( $firstPage[ 'pageid' ] ) && !isset( $firstPage[ "missing" ] ) ) {
			return true;
		}
		return false;
	}

}
