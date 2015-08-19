<?php
/**
 * Created by PhpStorm.
 * User: gabi
 * Date: 19.08.15
 * Time: 12:55
 */

namespace Wikimedia\ForwardScript;


use Symfony\Component\HttpFoundation\Response;

/**
 * This is a special response for errors that can be handled well and should
 * display an informative message to the user.
 *
 * It creates a 200 OK HTTP status code because otherwise the user would
 * see the default Tool Labs error page.
 *
 * It uses text/plain content type to avoid the need for HTML escaping.
 *
 * @package Wikimedia\ForwardScript
 */
class ErrorResponse extends Response {
	public function __construct( $content = '', $status = 200, $headers = array() ) {
		$headers = array_merge(
			[
				// The normal status code will be overwritten by the Silex handler,
				// see http://silex.sensiolabs.org/doc/usage.html#error-handlers
				'X-Status-Code' => Response::HTTP_OK,
				'Content-Type' => 'text/plain'
			],
			$headers
		);
		parent::__construct( $content, $status, $headers );
	}


}