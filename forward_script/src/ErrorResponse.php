<?php

namespace Wikimedia\ForwardScript;

use Symfony\Component\HttpFoundation\Response;

/**
 * This is a special response for errors that can be handled well and should
 * display an informative message to the user.
 *
 * It creates a 'X-Wikimedia-Debug' header because otherwise the user would
 * see the default Tool Labs error page.
 * See https://wikitech.wikimedia.org/wiki/Help:Tool_Labs/Web#Error_pages
 *
 * It uses text/plain content type to avoid the need for HTML escaping.
 *
 * @package Wikimedia\ForwardScript
 */
class ErrorResponse extends Response {
	public function __construct( $content = '', $status = 200, $headers = array() ) {
		$headers = array_merge(
			[
				'Content-Type' => 'text/plain',
				' X-Wikimedia-Debug' => '1'
			],
			$headers
		);
		parent::__construct( $content, $status, $headers );
	}
}
