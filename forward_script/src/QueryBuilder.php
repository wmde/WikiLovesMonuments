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
	 * @param array $additionalCategories Additional category names that will be added to the
	 * 				category from page info
	 * @return string
	 */

	public function getQuery( PageInformation $info, $pageName, $id = '', array $coordinates = [],
							  array $additionalCategories = [] ) {
		$categories = implode( "|",  array_merge( [$info->getCategory()], $additionalCategories ) );
		$query = array_merge( array_filter( $coordinates ), [ 'categories' =>  $categories ] );
		if ( $info->hasUsableId() ) {
			$query['objref'] = implode( '|', ['de', $pageName, $id] );
		}
		if ( $info->hasValidId() ) {
			$query['fields[]'] = $id;
		}
		if ( $info->hasImage() ) {
			$query['updateImage'] = "1";
		}
		return '&' . http_build_query( $query );
	}
}
