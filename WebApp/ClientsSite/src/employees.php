<?php 
include "db.php"; 
include "employees_data.php";

$stmt = $db->query("SELECT full_name FROM employees;");
$employees = $stmt->fetchAll(PDO::FETCH_COLUMN);
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Сотрудники</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="index.php">Страховая компания</a>
    </div>
</nav>

<div class="container py-5">
    <h1 class="text-center mb-4">Наши сотрудники</h1>

    <div class="row g-4">

<?php foreach ($employees as $name): ?>
    <?php if (!isset($EMP_DATA[$name])) continue; ?>
    <?php $e = $EMP_DATA[$name]; ?>

    <div class="col-md-4">
        <div class="card shadow-sm h-100">
            <img src="<?= $e['photo'] ?>" class="card-img-top" alt="Фото сотрудника">
            <div class="card-body">
                <h5 class="card-title"><?= $name ?></h5>
                <p class="card-text"><?= $e['desc'] ?></p>
                <p><strong>Телефон:</strong> <?= $e['phone'] ?></p>

                <form onsubmit="event.preventDefault(); showMsg(this);">
                    <input class="form-control mb-2" type="text" placeholder="Ваш телефон" required>
                    <button class="btn btn-primary w-100">Оставить заявку</button>
                </form>

                <div class="alert alert-success mt-3 d-none">
                    Заявка отправлена! В ближайшее время с вами свяжутся.
                </div>
            </div>
        </div>
    </div>

<?php endforeach; ?>

    </div>
</div>

<script>
function showMsg(form) {
    form.reset();
    let alert = form.parentElement.querySelector(".alert");
    alert.classList.remove("d-none");
}
</script>

</body>
</html>
