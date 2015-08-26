<?php

namespace Wikimedia\ForwardScript;

use Symfony\Component\HttpFoundation\Response;

/**
 * This is a special response for errors that can be handled well and should
 * display an informative message to the user.
 *
 * It creates a '200 OK' response because otherwise the user would
 * see the default Tool Labs error page.
 * See https://wikitech.wikimedia.org/wiki/Help:Tool_Labs/Web#Error_pages
 *
 * The status code must be generated via the "X-Status-Code" header because the Silex error
 * handler overrides the code by default.
 * See http://silex.sensiolabs.org/doc/usage.html#error-handlers
 *
 * @package Wikimedia\ForwardScript
 */
class ErrorResponse extends Response {
	public function __construct( $content = '', $status = 200, $headers = array() ) {
		$headers = array_merge(
			[
				'X-Status-Code' => 200
			],
			$headers
		);
		parent::__construct( $content, $status, $headers );
	}
}
