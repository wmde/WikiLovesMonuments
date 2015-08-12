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

	/**
	 * @var array
	 */
	protected $defaultCategories;

	protected function setUp() {
		$this->api = $this->getMockBuilder( "Mediawiki\\Api\\MediawikiApi" )
			->disableOriginalConstructor()
			->getMock();

		$this->process = $this->getMockBuilder( "Symfony\\Component\\Process\\Process" )
			->disableOriginalConstructor()
			->getMock();

		$this->defaultCategories = [
			"Kategorie:Liste (Baudenkmäler in Bayern)" => "Category:Cultural heritage monuments in Bavaria"
		];
	}


	/**
	 * @expectedException \Wikimedia\ForwardScript\ApplicationException
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

	/**
	 * @expectedException \Wikimedia\ForwardScript\ApplicationException
	 */
	public function testInvalidPageThrowsException() {

		$pageInfo = new PageInformationCollector( $this->api, $this->process );
		$this->api->method( "getRequest" )->willReturn( [
			"query" => [
				"pages" => [
					"-1" => [
						"ns"=> 460,
						"title" => "Denkmale in <b>Nimmerland",
						"invalidreason" => "The requested page title contains invalid characters: \"<\".",
						"invalid" => ""
					]
				]
			]
		] );
		$this->process->method( "isSuccessful" )->willReturn( true );
		$pageInfo->getInformation( "Denkmale in <b>Nimmerland", 123 );
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
	 * @expectedException \Wikimedia\ForwardScript\ApplicationException
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
		$pageInfo = new PageInformationCollector( $this->api, $this->process, $this->defaultCategories );
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
		$this->assertEquals( (object)[
				"id_not_found" => true,
				"category" => "Category:Cultural heritage monuments in Bavaria"
			],
			$result
		);
	}

	/**
	 * @expectedException \Symfony\Component\Process\Exception\RuntimeException
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

	public function testIfCategoryIsEmptyDefaultCategoryIsUsed() {
		$pageInfo = new PageInformationCollector( $this->api, $this->process, $this->defaultCategories );
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
		$this->process->method( "getOutput" )->willReturn( '{}' );
		$result = $pageInfo->getInformation( "Liste der Baudenkmäler in Abtswind", "D-6-75-111-7" );
		$this->assertEquals(
			(object) ["category" => "Category:Cultural heritage monuments in Bavaria"],
			$result
		);
	}

}
