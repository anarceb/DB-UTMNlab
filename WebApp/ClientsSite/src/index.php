<?php include "db.php"; ?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Страховая компания</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="index.php">Страховая компания</a>
        <div>
            <a class="btn btn-light me-2" href="employees.php">Сотрудники</a>
            <a class="btn btn-outline-light" href="login.php">Личный кабинет</a>
        </div>
    </div>
</nav>

<header class="py-5 bg-primary text-white text-center">
    <div class="container">
        <h1 class="fw-bold">Добро пожаловать!</h1>
        <p class="lead">Мы помогаем клиентам быстро и удобно получить доступ к информации о полисах и сотрудниках компании.</p>
    </div>
</header>

<div class="container py-5">
    <h2 class="text-center mb-4">Наши услуги</h2>

    <div class="row g-4">
        <div class="col-md-4">
            <div class="card shadow-sm h-100">
                <div class="card-body">
                    <h5 class="card-title">Оформление ОСАГО</h5>
                    <p class="card-text">Быстрое оформление страховки с подбором выгодных условий.</p>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card shadow-sm h-100">
                <div class="card-body">
                    <h5 class="card-title">Оформление КАСКО</h5>
                    <p class="card-text">Надёжная защита автомобиля от любых рисков.</p>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card shadow-sm h-100">
                <div class="card-body">
                    <h5 class="card-title">Онлайн доступ к полисам</h5>
                    <p class="card-text">Просматривайте свои полисы в личном кабинете.</p>
                </div>
            </div>
        </div>
    </div>
</div>

<footer class="bg-dark text-white text-center py-3 mt-4">
    © <?= date("Y") ?> Страховая компания
</footer>

</body>
</html>
