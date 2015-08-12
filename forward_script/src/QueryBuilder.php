<?php


namespace Wikimedia\ForwardScript;

class QueryBuilder {

	public function getQuery( $info, $pageName, $id='', $coordinates=[] ) {
		$category = preg_replace( '/^(:?Category|Kategorie):/', '', $info->category );
		$query = array_merge( array_filter( $coordinates ), [ 'categories' => $category ] );
		if ( $id && empty( $info->duplicate_ids ) && empty( $info->id_not_found ) ) {
			$query['objref'] = implode( '|', ['de', $pageName, $id] );
		}
		if ( !empty( $info->valid_id ) ) {
			$query['fields[]'] = $id;
		}
		return '&'.http_build_query( $query );
	}

}
