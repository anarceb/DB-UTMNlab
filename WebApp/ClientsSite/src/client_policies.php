<?php 
include "db.php";

$client_id = $_GET["id"];

$q = $db->prepare("
SELECT 
    p.policy_number,
    p.start_date,
    p.end_date,
    p.cost,
    cb.brand_name,
    cm.model_name,
    p.car_reg_number,
    ps.status_name
FROM policies p
JOIN car_brands cb ON p.car_brand_id = cb.brand_id
JOIN car_models cm ON p.car_model_id = cm.model_id
JOIN policy_statuses ps ON p.status_id = ps.status_id
WHERE p.owner_client_id = ?
");

$q->execute([$client_id]);
$policies = $q->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Ваши полисы</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="index.php">Страховая компания</a>
    </div>
</nav>

<div class="container py-5">
    <h1 class="mb-4">Ваши полисы</h1>

    <div class="row g-4">

<?php foreach ($policies as $p): ?>
    <div class="col-md-6">
        <div class="card shadow-sm h-100">
            <div class="card-body">

                <h5 class="card-title"><?= $p['policy_number'] ?></h5>

                <p><strong>Статус:</strong> <?= $p['status_name'] ?></p>
                <p><strong>Автомобиль:</strong> <?= $p['brand_name'] ?> <?= $p['model_name'] ?></p>
                <p><strong>Гос. номер:</strong> <?= $p['car_reg_number'] ?></p>

                <p><strong>Начало действия:</strong> <?= $p['start_date'] ?></p>
                <p><strong>Окончание:</strong> <?= $p['end_date'] ?></p>

                <p><strong>Стоимость:</strong> <?= number_format($p['cost'], 2, ',', ' ') ?> ₽</p>

            </div>
        </div>
    </div>
<?php endforeach; ?>

    </div>

</div>

</body>
</html>
