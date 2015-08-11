<?php

use Silex\WebTestCase;

class ApplicationTest extends WebTestCase {

	/**
	 * Creates the application.
	 *
	 * @return \Symfony\Component\HttpKernel\HttpKernelInterface
	 */
	public function createApplication() {

		$app = require __DIR__.'/../app.php';
		$app['debug'] = true;
		unset( $app[ 'exception_handler' ] );

		return $app;
	}

	public function testIndexPage() {
		$client = $this->createClient();
		$client->request( 'GET', '/' );
		$this->assertTrue( $client->getResponse()->isOk() );
	}

	/**
	 * @expectedException        \Symfony\Component\HttpKernel\Exception\NotFoundHttpException
	 */
	public function testRedirectRequiresPageAndCampaignName() {
		$client = $this->createClient();
		$client->request( 'GET', '/redirect' );
	}

	public function testRedirectReturnsRedirectResponse() {
		$client = $this->createClient();
		$this->app["campaign_validator"] = $this->getMockBuilder(
				"Wikimedia\\ForwardScript\\CampaignValidator"
			)
			->disableOriginalConstructor()
			->getMock();
		$this->app["campaign_validator"]->method( 'isValidCampaign' )->willReturn( true );
		$this->app["cache"] = $this->getMock( "Doctrine\\Common\\Cache\\Cache" );
		$this->app["cache"]->method( "contains" )->willReturn( false );
		$this->app["pageinfo"] = $this->getMockBuilder(
				"Wikimedia\\ForwardScript\\PageInformationCollector"
			)
			->disableOriginalConstructor()
			->getMock();
		$this->app["pageinfo"]->method( "getInformation" )->willReturn( new stdClass() );
		$client->request( 'GET', '/redirect/Liste_der_Baudenkmäler_in_Abtswind/wlm-de-by/123' );
		$this->assertTrue( $client->getResponse()->isRedirection(), "Response is not a redirect" );
	}

	/**
	 * @expectedException        \Symfony\Component\HttpKernel\Exception\NotFoundHttpException
	 */
	public function testRedirectRejectsInvalidCampaignNames() {
		$client = $this->createClient();
		$client->request( 'GET', '/redirect/Liste_der_Baudenkmäler_in_Abtswind/foo.bar/123§' );
	}

}
