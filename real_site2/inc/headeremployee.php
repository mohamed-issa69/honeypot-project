<!DOCTYPE html>
<html>
<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>

<title>Employee Panel</title>

<link rel="stylesheet"
href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

<link rel="stylesheet" href="css/style.css" type="text/css" />

</head>

<body>

<div class="header">

    <div class="logo">

        <div class="logo-left">

            <div class="logo-icon">
                <i class="fa fa-shield"></i>
            </div>

            <div class="logo-text">

                <div class="logo-title">
                    Cairo Transfer System
                </div>

                <div class="logo-subtitle">
                    Secure Banking Dashboard
                </div>

            </div>

        </div>

        <div class="username-on-top">

            <i class="fa fa-user-circle"></i>

            <?php echo $_SESSION['name']; ?>

        </div>

    </div>

</div>

<div class="desh-menu">

    <ul>

        <li>
            <a href="dashboard.php">
                <span class="fa fa-tachometer"></span>
                Dashboard
            </a>
        </li>

        <li>

            <a href="">
                <span class="fa fa-money"></span>
                Transfers
            </a>

            <ul>

                <li>
                    <a href="send.php">
                        <span class="fa fa-arrow-up"></span>
                        Send
                    </a>
                </li>

                <li>
                    <a href="receive.php">
                        <span class="fa fa-arrow-down"></span>
                        Receive
                    </a>
                </li>

            </ul>

        </li>

        <li>
            <a href="transection.php">
                <span class="fa fa-area-chart"></span>
                Transactions
            </a>
        </li>

        <li>
            <a href="logout.php">
                <span class="fa fa-sign-out"></span>
                Logout
            </a>
        </li>

    </ul>

</div>