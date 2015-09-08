<?php

require_once __DIR__ . '/functions.php';

class TestFunctions extends PHPUnit_Framework_TestCase {

	public function testResultHasErrorsIfReturnCodeIsNotARedirect() {
		$this->assertTrue( resultHasErrors( 404, "", "" ) );
	}

	public function testResultHasErrorsIfResponseIsFalse() {
		$this->assertTrue( resultHasErrors( 301, false, "" ) );
	}

	public function testResultHasErrorsIfResponseDoesNotContainLocationPattern() {
		$response = "X-Test: Foo\nLocation: http://example.com/foo/bar\n";
		$this->assertTrue( resultHasErrors( 301, $response, "http://example.com/bar/foo" ) );
	}

	public function testResultHasErrorsIfResponseMatchesLocationPattern() {
		$response = "X-Test: Foo\nLocation: http://example.com/foo/bar\n";
		$this->assertFalse( resultHasErrors( 301, $response, "http://example.com/foo/bar" ) );
	}

	public function testResultHasErrorsIfResponseMatchesLocationPatternWithDifferentParamOrder() {
		$response = "X-Test: Foo\nLocation: http://example.com/?foo=1&bar=2\n";
		$this->assertFalse( resultHasErrors( 301, $response, "http://example.com/?bar=2&foo=1" ) );
	}
}
