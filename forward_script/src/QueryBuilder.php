<?php


namespace Wikimedia\ForwardScript;

class QueryBuilder {

	public function getQuery( $info, $pageName, $id="", $lat="", $lon="" ) {
		$category = preg_replace( "/^(:?Category|Kategorie):/", "", $info->category );
		$query = [ "categories" => $category ];
		if ( $lat ) {
			$query["lat"] = $lat;
		}
		if ( $lon ) {
			$query["lon"] = $lon;
		}
		if ( $id && empty( $info->duplicate_ids ) && empty( $info->id_not_found ) ) {
			$query["objref"] = implode( "|", ["de", $pageName, $id] );
		}
		if ( !empty( $info->valid_id ) ) {
			$query["fields[]"] = $id;
		}
		$queryString = "";
		foreach ( $query as $param => $value ) {
			$queryString .= "&" . $param . "=" . urlencode( $value );
		}
		return $queryString;
	}

}
