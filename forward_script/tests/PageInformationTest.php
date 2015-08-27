<?php

use Wikimedia\ForwardScript\PageInformation;

class PageInformationTest extends PHPUnit_Framework_TestCase {

	public function testMissingIdCanBeQueried() {
		$pageInformation = new PageInformation( (object)[
			"id_not_found" => true
		] );
		$this->assertFalse( $pageInformation->hasUsableId() );
	}

	public function testDuplicateIdsCanBeQueried() {
		$pageInformation = new PageInformation( (object)[
			"duplicate_ids" => true
		] );
		$this->assertFalse( $pageInformation->hasUsableId() );
	}

	public function testIdIsUsableWhenNoSpecialFlagsAreSet() {
		$pageInformation = new PageInformation( new stdClass() );
		$this->assertTrue( $pageInformation->hasUsableId() );
	}

	public function testValidIdCanBeSet() {
		$pageInformation = new PageInformation( new stdClass() );
		$this->assertFalse( $pageInformation->hasValidId() );
		$pageInformation = new PageInformation( (object)[
			"valid_id" => true
		] );
		$this->assertTrue( $pageInformation->hasValidId() );
	}

	public function testImageExistsCanBeSet() {
		$pageInformation = new PageInformation( new stdClass() );
		$this->assertFalse( $pageInformation->hasImage() );
		$pageInformation = new PageInformation( (object)[
			"image_exists" => false
		] );
		$this->assertFalse( $pageInformation->hasImage() );
		$pageInformation = new PageInformation( (object)[
			"image_exists" => true
		] );
		$this->assertTrue( $pageInformation->hasImage() );
	}

	public function testCategoryNameIsNormalized() {
		$pageInformation = new PageInformation( (object)[
			"category" => "Kategorie:Test"
		] );
		$this->assertEquals( "Test", $pageInformation->getCategory() );
		$pageInformation = new PageInformation( (object)[
			"category" => "Category:Test"
		] );
		$this->assertEquals( "Test", $pageInformation->getCategory() );
		$pageInformation = new PageInformation( (object)[
			"category" => "Test"
		] );
		$this->assertEquals( "Test", $pageInformation->getCategory() );
	}

}
