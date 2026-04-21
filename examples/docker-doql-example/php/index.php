<?php
header('Content-Type: application/json');

$serviceName = getenv('SERVICE_NAME') ?: 'php-api';
$dbHost = getenv('DB_HOST') ?: 'database';
$phpVersion = phpversion();

function sendResponse($message) {
    global $serviceName, $dbHost, $phpVersion;
    
    $response = [
        'message' => $message,
        'service' => $serviceName,
        'language' => 'PHP',
        'version' => '8.2',
        'php_version' => $phpVersion,
        'db_host' => $dbHost
    ];
    
    echo json_encode($response, JSON_PRETTY_PRINT);
}

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if ($path === '/health') {
    sendResponse('OK');
} elseif ($path === '/api') {
    sendResponse('Hello from PHP service!');
} else {
    http_response_code(404);
    echo json_encode(['error' => 'Not found']);
}
