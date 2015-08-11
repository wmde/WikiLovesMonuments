<?php

use Mediawiki\Api\MediawikiApi;
use Symfony\Component\Process\Process;

use Wikimedia\ForwardScript\PageInformationCollector;

class PageInformationCollectorTest extends PHPUnit_Framework_TestCase {

	/**
	 * @var MediawikiApi
	 */
	protected $api;

	/**
	 * @var Process
	 */
	protected $process;

	protected function setUp() {
		$this->api = $this->getMockBuilder( "Mediawiki\\Api\\MediawikiApi" )
			->disableOriginalConstructor()
			->getMock();

		$this->process = $this->getMockBuilder( "Symfony\\Component\\Process\\Process" )
			->disableOriginalConstructor()
			->getMock();
	}


	/**
	 * @expectedException \RuntimeException
	 */
	public function testMissingPageThrowsException() {

		$pageInfo = new PageInformationCollector( $this->api, $this->process );
		$this->api->method( "getRequest" )->willReturn( [
			"query" => [
				"pages" => [
					"-1" => [
						"ns"=> 460,
						"title" => "Denkmale in Nimmerland",
						"missing" => ""
					]
				]
			]
		] );
		$this->process->method( "isSuccessful" )->willReturn( true );
		$pageInfo->getInformation( "Denkmale in Nimmerland", 123 );
	}

	public function testProcessInputIsSetToPageData() {
		$pageInfo = new PageInformationCollector( $this->api, $this->process );
		$this->api->method( "getRequest" )->willReturn( [
			"query" => [
				"pages" => [
					"123" => [
						"ns"=> 460,
						"revisions" => [
							["*" => "Page Text", "contentformat" => "text/x-wiki"]
						],
						"categories" => [["title" => "Kategorie:Liste (Baudenkmäler in Bayern)"]]
					]
				]
			]
		] );
		$this->process->method( "getCommandLine" )->willReturn( "pythonscript" );
		$this->process->expects( $this->once() )->method( "setInput" )->with(
			$this->equalTo( "Page Text" )
		);
		$this->process->expects( $this->once() )->method( "setCommandLine" )->with(
			$this->equalTo( "pythonscript 'D-6-75-111-7'" )
		);
		$this->process->method( "isSuccessful" )->willReturn( true );
		$this->process->method( "getOutput" )->willReturn( '{"category":"test"}' );
		$pageInfo->getInformation( "Liste der Baudenkmäler in Abtswind", "D-6-75-111-7" );
	}

	/**
	 * @expectedException \RuntimeException
	 */
	public function testWrongContentTypeLeadsToError() {
		$pageInfo = new PageInformationCollector( $this->api, $this->process );
		$this->api->method( "getRequest" )->willReturn( [
			"query" => [
				"pages" => [
					"123" => [
						"ns"=> 460,
						"revisions" => [
							["*" => "Page Text", "contentformat" => "text/plain"]
						]
					]
				]
			]
		] );
		$this->process->method( "isSuccessful" )->willReturn( true );
		$this->process->method( "getOutput" )->willReturn( '{"category":"test"}' );
		$pageInfo->getInformation( "Liste der Baudenkmäler in Abtswind", "D-6-75-111-7" );
	}

	public function testProcessOutputIsReturnedAsJSONDecodedData() {
		$pageInfo = new PageInformationCollector( $this->api, $this->process );
		$this->api->method( "getRequest" )->willReturn( [
			"query" => [
				"pages" => [
					"123" => [
						"ns"=> 460,
						"revisions" => [
							["*" => "Page Text", "contentformat" => "text/x-wiki"]
						],
						"categories" => [["title" => "Kategorie:Liste (Baudenkmäler in Bayern)"]]
					]
				]
			]
		] );
		$this->process->method( "isSuccessful" )->willReturn( true );
		$this->process->method( "getOutput" )->willReturn( '{"id_not_found":true}' );
		$result = $pageInfo->getInformation( "Liste der Baudenkmäler in Abtswind", "D-6-75-111-7" );
		$this->assertEquals( (object)["id_not_found" => true], $result );
	}

	/**
	 * @expectedException \RuntimeException
	 */
	public function testProcessErrorCausesException() {
		$pageInfo = new PageInformationCollector( $this->api, $this->process );
		$this->api->method( "getRequest" )->willReturn( [
			"query" => [
				"pages" => [
					"123" => [
						"ns"=> 460,
						"revisions" => [
							["*" => "Page Text", "contentformat" => "text/x-wiki"]
						],
						"categories" => [["title" => "Kategorie:Liste (Baudenkmäler in Bayern)"]]
					]
				]
			]
		] );

		$this->process->method( "isSuccessful" )->willReturn( false );
		$pageInfo->getInformation( "Liste der Baudenkmäler in Abtswind", "D-6-75-111-7" );
	}

	public function testIfTemplateIsValidAndCategoryEmptyDefaultCategoryIsUsed() {
		$defaultCategories = [
			"Kategorie:Liste (Baudenkmäler in Bayern)" => "Category:Cultural heritage monuments in Bavaria"
		];
		$pageInfo = new PageInformationCollector( $this->api, $this->process, $defaultCategories );
		$this->api->method( "getRequest" )->willReturn( [
			"query" => [
				"pages" => [
					"123" => [
						"ns"=> 460,
						"revisions" => [
							["*" => "Page Text", "contentformat" => "text/x-wiki"]
						],
						"categories" => [
							["title" => "Kategorie:Liste (Baudenkmäler in Bayern)"],
							["title" => "Kategorie:Wikipedia:Liste"]
						]
					]
				]
			]
		] );
		$this->process->method( "isSuccessful" )->willReturn( true );
		$this->process->method( "getOutput" )->willReturn( '{"category":""}' );
		$result = $pageInfo->getInformation( "Liste der Baudenkmäler in Abtswind", "D-6-75-111-7" );
		$this->assertEquals(
			(object) ["category" => "Category:Cultural heritage monuments in Bavaria"],
			$result
		);
	}

}
