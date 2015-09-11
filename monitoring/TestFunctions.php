<?php

require_once __DIR__ . '/functions.php';

class TestFunctions extends PHPUnit_Framework_TestCase {

	public function testResultHasErrorsIfReturnCodeIsNotARedirect() {
		$expectedErrors = [true, "Wrong HTTP response code: 404"];
		$this->assertEquals( $expectedErrors, resultHasErrors( 404, "", "" ) );
	}

	public function testResultHasErrorsIfResponseIsFalse() {
		$expectedErrors = [true, "CURL encountered an error."];
		$this->assertEquals( $expectedErrors, resultHasErrors( 301, false, "" ) );
	}

	public function testResultHasErrorsIfResponseDoesNotContainLocationPattern() {
		$response = "X-Test: Foo\r\nContent-Type: text/plain\r\n";
		$expectedErrors = [true, "Location header is missing."];
		$resultHasErrors = resultHasErrors( 301, $response, "http://example.com/bar/foo" );
		$this->assertEquals( $expectedErrors, $resultHasErrors );
	}

	public function testResultHasErrorsIfResponseHasDifferentProtocolAndPath() {
		$response = "X-Test: Foo\r\nLocation: http://example.com/bar/foo\r\n";
		$resultHasErrors = resultHasErrors( 301, $response, "https://example.com/foo/bar" );
		$this->assertTrue( $resultHasErrors[0] );
		$this->assertContains( "scheme", $resultHasErrors[1] );
		$this->assertContains( "path", $resultHasErrors[1] );
	}

	public function testResultHasErrorsIfResponseMatchesLocationPattern() {
		$response = "X-Test: Foo\r\nLocation: http://example.com/foo/bar\r\n";
		$expectedErrors = [false, ""];
		$resultHasErrors = resultHasErrors( 301, $response, "http://example.com/foo/bar" );
		$this->assertEquals( $expectedErrors, $resultHasErrors );
	}

	public function testResultHasErrorsIfResponseMatchesLocationPatternWithDifferentParamOrder() {
		$response = "X-Test: Foo\r\nLocation: http://example.com/?foo=1&bar=2\r\n";
		$expectedErrors = [false, ""];
		$resultHasErrors = resultHasErrors( 301, $response, "http://example.com/?bar=2&foo=1" );
		$this->assertEquals( $expectedErrors, $resultHasErrors );
	}

	public function testResultHasErrorsHandlesFieldArrayParamWithCorrectId() {
		$response = "X-Test: Foo\r\nLocation: http://example.com/?fields[]=1\r\n";
		$expectedErrors = [false, ""];
		$resultHasErrors = resultHasErrors( 301, $response, "http://example.com/?fields[]=1" );
		$this->assertEquals( $expectedErrors, $resultHasErrors );
	}

	public function testResultHasErrorsHandlesFieldArrayParamWithWrongId() {
		$response = "X-Test: Foo\r\nLocation: http://example.com/?fields[]=1\r\n";
		$resultHasErrors = resultHasErrors( 301, $response, "http://example.com/?fields[]=7" );
		$this->assertTrue( $resultHasErrors[0] );
		$this->assertContains( "field", $resultHasErrors[1] );
	}
}
