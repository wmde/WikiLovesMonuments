<?php

require __DIR__.'/vendor/autoload.php';

$app = new Silex\Application();

$app->get("/", function() {
    return "WLM redirect script";
});

return $app;