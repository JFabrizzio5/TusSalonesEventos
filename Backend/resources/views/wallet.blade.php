<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wallet</title>
</head>
<body>
    <div class="page">
        <div class="ticket">
            <section class="ticket-cover">
                <div class="brand">
                    EVENT PASS
                </div>
                <div class="event-title">
                    <h1>
                        Concierto Rock 2026
                    </h1>
                    <p>
                        Experiencia en vivo
                    </p>
                </div>
            </section>
            <section class="ticket-body">
                <div class="ticket-info">
                    <div>
                        <label>Fecha</label>
                        <strong>20 JUN 2026</strong>
                    </div>
                    <div>
                        <label>Hora</label>
                        <strong>20:00 PM</strong>
                    </div>
                    <div>
                        <label>Lugar</label>
                        <strong>Auditorio Principal</strong>
                    </div>
                    <div>
                        <label>Zona</label>
                        <strong>Preferente A</strong>
                    </div>
                </div>

                <div class="separator"></div>

                <div class="ticket-bottom">
                    <div class="seat">
                        <div>
                            <span>
                                ASIENTO
                            </span>

                            <strong>
                                A-15
                            </strong>

                        </div>
                        <div>
                            <span>
                                TICKET
                            </span>

                            <strong>
                                #000154
                            </strong>
                        </div>
                    </div>
                    <div class="qr-section">
                        <div class="qr">
                            QR
                        </div>
                        <p>
                            Código válido para acceso
                        </p>
                    </div>
                </div>
                <button id="walletButton">
                    Agregar a Wallet
                </button>
            </section>
        </div>
    </div>
</body>
</html>
<style>
    *{
        box-sizing:border-box;
        font-family:'Inter',Arial,sans-serif;
    }

    body{
        margin:0;
        min-height:100vh;
        background:
        linear-gradient(
            120deg,
            #141e30,
            #243b55
        );
        display:flex;
        justify-content:center;
        align-items:center;
    }

    /*
    Contenedor principal
    */

    .page{
        width:100%;
        max-width:1100px;
        padding:40px;
    }

    /*
    Ticket horizontal
    */

    .ticket{
        display:grid;
        grid-template-columns: 40% 60%;
        background:white;
        border-radius:30px;
        overflow:hidden;
        box-shadow: 0 30px 70px rgba(0,0,0,.35);
    }

    /*
    Parte izquierda
    */

    .ticket-cover{
        padding:45px;
        color:white;
        background:
        linear-gradient(
            145deg,
            #6a11cb,
            #2575fc
        );
        display:flex;
        flex-direction:column;
        justify-content:space-between;
    }

    .brand{
        font-size:14px;
        letter-spacing:5px;
        opacity:.8;
    }

    .event-title h1{
        font-size:42px;
        margin:0;
    }

    .event-title p{
        font-size:18px;
        opacity:.8;
    }

    /*
    Información derecha
    */

    .ticket-body{
        padding:45px;
    }

    .ticket-info{
        display:grid;
        grid-template-columns:repeat(2,1fr);
        gap:30px;
    }

    .ticket-info div{
        display:flex;
        flex-direction:column;
    }

    label{
        color:#777;
        font-size:13px;
    }

    .ticket-info strong{
        font-size:20px;
        margin-top:8px;
    }

    .separator{
        height:1px;
        background:#ddd;
        margin:35px 0;
    }

    .ticket-bottom{
        display:flex;
        justify-content:space-between;
        align-items:center;
    }

    .seat{
        display:flex;
        gap:60px;
    }

    .seat span{
        color:#888;
        font-size:12px;
    }

    .seat strong{
        display:block;
        font-size:35px;
    }

    /*
    QR
    */

    .qr-section{
        text-align:center;
    }

    .qr{
        width:150px;
        height:150px;
        background:
        repeating-linear-gradient(
            45deg,
            #111,
            #111 6px,
            white 6px,
            white 12px
        );
        display:flex;
        justify-content:center;
        align-items:center;
        color:white;
    }
    .qr-section p{
        font-size:13px;
        color:#777;
    }

    #walletButton{
        margin-top:40px;
        width:100%;
        padding:18px;
        border:none;
        border-radius:12px;
        background:#111;
        color:white;
        font-size:18px;
        cursor:pointer;
    }

    #walletButton:hover{
        background:#333;
    }
</style>