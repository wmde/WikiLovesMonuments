<?php


class PageInformationTest extends PHPUnit_Framework_TestCase {

	public function testMissingIdCanBeQueried() {
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( (object)[
			"id_not_found" => true
		] );
		$this->assertFalse( $pageInformation->hasUsableId() );
	}

	public function testDuplicateIdsCanBeQueried() {
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( (object)[
			"duplicate_ids" => true
		] );
		$this->assertFalse( $pageInformation->hasUsableId() );
	}

	public function testIdIsUsableWhenNoSpecialFlagsAreSet() {
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( new stdClass() );
		$this->assertTrue( $pageInformation->hasUsableId() );
	}

	public function testValidIdCanBeSet() {
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( new stdClass() );
		$this->assertFalse( $pageInformation->hasValidId() );
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( (object)[
			"valid_id" => true
		] );
		$this->assertTrue( $pageInformation->hasValidId() );
	}

	public function testCategoryNameIsNormalized() {
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( (object)[
			"category" => "Kategorie:Test"
		] );
		$this->assertEquals( "Test", $pageInformation->getCategory() );
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( (object)[
			"category" => "Category:Test"
		] );
		$this->assertEquals( "Test", $pageInformation->getCategory() );
		$pageInformation = new \Wikimedia\ForwardScript\PageInformation( (object)[
			"category" => "Test"
		] );
		$this->assertEquals( "Test", $pageInformation->getCategory() );
	}

}
