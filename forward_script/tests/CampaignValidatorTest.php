<?php

use Wikimedia\ForwardScript\CampaignValidator;

class CampaignValidatorTest extends PHPUnit_Framework_TestCase {

	public function testValidatorReturnsTrueIfPageExists() {

		$api = $this->getMockBuilder( 'Mediawiki\\Api\\MediawikiApi' )
			->disableOriginalConstructor()
			->getMock();
		$api->method( 'getRequest' )->willReturn( [
			'query' => [
				'pages' => [
					'27388743' => [
						'pageid' => 27388743,
						'ns'=> 460,
						'title' => 'Campaign:wlm-de-by'
					]
				]
			]
		] );
		$validator = new CampaignValidator( $api );
		$this->assertTrue( $validator->isValidCampaign( 'Campaign:wlm-de-by' ) );
	}

	public function testValidatorReturnsFalseIfPageIsMissing() {

		$api = $this->getMockBuilder( 'Mediawiki\\Api\\MediawikiApi' )
			->disableOriginalConstructor()
			->getMock();
		$api->method( 'getRequest' )->willReturn( [
			'query' => [
				'pages' => [
					'-1' => [
						'ns'=> 460,
						'title' => 'Campaign:foobar',
						'missing' => ''
					]
				]
			]
		] );
		$validator = new CampaignValidator( $api );
		$this->assertFalse( $validator->isValidCampaign( 'Campaign:foobar' ) );
	}

	public function testValidatorReturnsFalseIfPageIsInvalid() {

		$api = $this->getMockBuilder( 'Mediawiki\\Api\\MediawikiApi' )
			->disableOriginalConstructor()
			->getMock();
		$api->method( 'getRequest' )->willReturn( [
			'query' => [
				'pages' => [
					'-1' => [
						'ns'=> 460,
						'title' => 'Campaign:<b>foobar',
						'invalidreason' => 'The requested page title contains invalid characters: "<".',
						'invalid' => ''
					]
				]
			]
		] );
		$validator = new CampaignValidator( $api );
		$this->assertFalse( $validator->isValidCampaign( 'Campaign:<b>foobar' ) );
	}

	public function testValidatorReturnsFalseIfPageIsNotInCampaignNamespace() {

		$api = $this->getMockBuilder( 'Mediawiki\\Api\\MediawikiApi' )
			->disableOriginalConstructor()
			->getMock();
		$api->method( 'getRequest' )->willReturn( [
			'query' => [
				'pages' => [
					'27388743' => [
						'pageid' => 27388743,
						'ns'=> 1,
						'title' => 'wlm-de-by'
					]
				]
			]
		] );
		$validator = new CampaignValidator( $api );
		$this->assertFalse( $validator->isValidCampaign( 'wlm-de-by' ) );
	}

}
