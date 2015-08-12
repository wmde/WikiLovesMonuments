<?php

use Wikimedia\ForwardScript\QueryBuilder;

class QueryBuilderTest extends PHPUnit_Framework_TestCase {

	public function testCategoryIsAdded() {
		$qb = new QueryBuilder();
		$query = $qb->getQuery( (object)['category' => 'Test'], 'Test Page' );
		$this->assertContains( '&categories=Test', $query );
	}

	public function testCategoryPrefixIsRemoved() {
		$qb = new QueryBuilder();
		$query = $qb->getQuery( (object)['category' => 'Category:Test'], 'Test Page' );
		$this->assertContains( '&categories=Test', $query );
	}

	public function testLatAndLonAreAdded() {
		$qb = new QueryBuilder();
		$query = $qb->getQuery( (object)['category' => 'Test'], 'Test Page', null,
			['lat' => '1', 'lon' => '2.2335455'] );
		$this->assertContains( '&lat=1', $query );
		$this->assertContains( '&lon=2.2335455', $query );
	}

	public function testEmptyLatAndLonAreFiltered() {
		$qb = new QueryBuilder();
		$query = $qb->getQuery( (object)['category' => 'Test'], 'Test Page', null,
			['lat' => '', 'lon' => ''] );
		$this->assertNotContains( '&lat=', $query );
		$this->assertNotContains( '&lon=', $query );
	}

	public function testObjRefIsAddedIfIdExists() {
		$qb = new QueryBuilder();
		$query = $qb->getQuery( (object)['category' => 'Test'], 'Test Page', '123' );
		$this->assertContains( '&objref=de%7CTest+Page%7C123', $query );
	}

	public function testObjRefIsLeftOutIfIdIsNotUnique() {
		$qb = new QueryBuilder();
		$info = (object)['category' => 'Test', 'duplicate_ids' => true];
		$query = $qb->getQuery( $info, 'Test Page', '123' );
		$this->assertNotContains( '&objref=de%7CTest+Page%7C123', $query );
	}

	public function testObjRefIsLeftOutIfIdIsNotFound() {
		$qb = new QueryBuilder();
		$info = (object)['category' => 'Test', 'id_not_found' => true];
		$query = $qb->getQuery( $info, 'Test Page', '123' );
		$this->assertNotContains( '&objref=de%7CTest+Page%7C123', $query );
	}

	public function testFieldsAreAddedIfIdIsValid() {
		$qb = new QueryBuilder();
		$info = (object)['category' => 'Test', 'valid_id' => true];
		$query = $qb->getQuery( $info, 'Test Page', '123' );
		$this->assertContains( '&fields%5B%5D=123', $query );
	}

}
