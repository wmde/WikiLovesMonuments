<?php

use Wikimedia\ForwardScript\QueryBuilder;

class QueryBuilderTest extends PHPUnit_Framework_TestCase {

	private $pageInfo;

	protected function setUp() {
		$this->pageInfo = $this->getMockBuilder( 'Wikimedia\\ForwardScript\\PageInformation' )
			->disableOriginalConstructor()
			->getMock();
	}

	public function testCategoryIsAdded() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "getCategory" )->willReturn( "Test" );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page' );
		$this->assertContains( '&categories=Test', $query );
	}

	public function testAdditionalCategoriesAreAdded() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "getCategory" )->willReturn( "Test" );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', null, [], ["Foo", "Bar"] );
		$this->assertContains( '&categories=Test%7CFoo%7CBar', $query );
	}

	public function testLatAndLonAreAdded() {
		$qb = new QueryBuilder();
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', null,
			['lat' => '1', 'lon' => '2.2335455'] );
		$this->assertContains( '&lat=1', $query );
		$this->assertContains( '&lon=2.2335455', $query );
	}

	public function testEmptyLatAndLonAreFiltered() {
		$qb = new QueryBuilder();
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', null,
			['lat' => '', 'lon' => ''] );
		$this->assertNotContains( '&lat=', $query );
		$this->assertNotContains( '&lon=', $query );
	}

	public function testObjRefIsAddedIfIdIsUsable() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "hasUsableId" )->willReturn( true );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', '123' );
		$this->assertContains( '&objref=de%7CTest+Page%7C123', $query );
	}

	public function testObjRefIsLeftOutIfIdIsNotUsable() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "hasUsableId" )->willReturn( false );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', '123' );
		$this->assertNotContains( '&objref=de%7CTest+Page%7C123', $query );
	}

	public function testFieldsAreAddedIfIdIsValid() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "hasValidId" )->willReturn( true );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', '123' );
		$this->assertContains( '&fields%5B%5D=123', $query );
	}

	public function testFieldsAreLeftOutIfIdIsInvalid() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "hasValidId" )->willReturn( false );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', '123' );
		$this->assertNotContains( '&fields%5B%5D=123', $query );
	}

	public function testUpdateListIsAddedIfNoImageExists() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "hasImage" )->willReturn( false );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', '123' );
		$this->assertContains( '&updateList=1', $query );
	}

	public function testUpdateListLeftOutIfImageExists() {
		$qb = new QueryBuilder();
		$this->pageInfo->method( "hasImage" )->willReturn( true );
		$query = $qb->getQuery( $this->pageInfo, 'Test Page', '123' );
		$this->assertNotContains( '&updateList=1', $query );
	}
}
