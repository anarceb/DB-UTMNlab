<?php

$host = getenv('PG_HOST') ?: 'postgres';
$port = getenv('PG_PORT') ?: '5432';
$dbname = getenv('PG_DB') ?: 'company';
$user = getenv('PG_USER') ?: 'postgres';
$pass = getenv('PG_PASSWORD') ?: 'postgres';

$dsn = "pgsql:host=$host;port=$port;dbname=$dbname;";

try {
    $db = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);
} catch (PDOException $e) {
    die("Ошибка подключения к БД: " . $e->getMessage());
}
