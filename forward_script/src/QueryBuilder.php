<?php


namespace Wikimedia\ForwardScript;

class QueryBuilder {

	/**
	 * Generate a query string from available information
	 *
	 * @param PageInformation $info Information about the checked
	 * @param string $pageName Wikipedia page name
	 * @param string $id Unique monument id
	 * @param array $coordinates Contains "lat" and "lon" keys (which may be empty)
	 * @return string
	 */
	public function getQuery( PageInformation $info, $pageName, $id = '', array $coordinates = [] ) {
		$query = array_merge( array_filter( $coordinates ), [ 'categories' => $info->getCategory() ] );
		if ( $info->hasUsableId() ) {
			$query['objref'] = implode( '|', ['de', $pageName, $id] );
		}
		if ( $info->hasValidId() ) {
			$query['fields[]'] = $id;
		}
		return '&' . http_build_query( $query );
	}
}
