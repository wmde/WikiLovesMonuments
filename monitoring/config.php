<?php

// Notification settings
$notifyMail = 'gabriel.birke@wikimedia.de';
$subjectPrefix = '[WLM-Monitor]';

// Forward script settings
$checkURL = 'https://tools.wmflabs.org/wlm-de-utils/redirect/Benutzer%3AGabriel+Birke+%28WMDE%29%2FDemo+Liste+Baudenkmale+Bad+Wiessee/wlm-de-by?id=D-1-82-111-30&lat=11.70699&lon=47.73638';
$expectedLocation = 'https://commons.wikimedia.org/wiki/Special:UploadWizard';

// Bot check settings
$checkPatterns = [
	'/\s+commonsbot\s+/' => 'Commons Bot'
];
