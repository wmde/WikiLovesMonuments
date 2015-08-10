<?php

use Silex\WebTestCase;

class ApplicationTest extends WebTestCase {

    /**
     * Creates the application.
     *
     * @return \Symfony\Component\HttpKernel\HttpKernelInterface
     */
    public function createApplication()
    {
        $app = require __DIR__.'/../app.php';
        $app['debug'] = true;
        unset($app['exception_handler']);

        return $app;
    }

    public function testIndexPage(){
        $client = $this->createClient();
        $client->request('GET', '/');

        $this->assertTrue($client->getResponse()->isOk());
        
    }

}