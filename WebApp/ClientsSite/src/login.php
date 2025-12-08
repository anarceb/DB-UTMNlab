<?php
include "db.php";

if ($_POST) {
    $login = $_POST["login"];
    $pass = $_POST["password"];

    $stmt = $db->prepare("
        SELECT client_id, full_name, password 
        FROM clients 
        WHERE phone = ? OR email = ?
    ");
    $stmt->execute([$login, $login]);

    $client = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$client) {
        $error = "Клиент не найден";
    } 
    else if ($client["password"] !== $pass) {
        $error = "Неверный пароль";
    } 
    else {
        header("Location: client_policies.php?id=" . $client["client_id"]);
        exit;
    }
}
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Вход</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">
<div class="container py-5" style="max-width: 400px;">
    <h3 class="text-center mb-4">Личный кабинет</h3>

    <?php if (!empty($error)) echo "<div class='alert alert-danger'>$error</div>"; ?>

    <form method="POST" class="card p-4 shadow-sm">
        <label class="form-label">Телефон или Email</label>
        <input type="text" name="login" class="form-control" required>

        <label class="form-label mt-3">Пароль</label>
        <input type="password" name="password" class="form-control" required>

        <button class="btn btn-primary w-100 mt-4">Войти</button>
    </form>
</div>
</body>
</html>
