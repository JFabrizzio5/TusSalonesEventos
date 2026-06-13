<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calendar</title>
</head>
<body>
    <div class="calendar-container">
        <h2>
            Calendario de eventos
        </h2>
        <div class="calendar-form">
            <div class="form-group">
                <label>
                    App ID
                </label>

                <input 
                    type="number" 
                    id="app_id"
                    value="1"
                >
            </div>
            <div class="form-group">
                <label>
                    Usuario ID
                </label>
                <input 
                    type="number" 
                    id="userauth_id"
                    value="1"
                >
            </div>

            <div id="month-fields" class="dynamic-fields">
                <div class="form-group">
                    <label>
                        Año
                    </label>
                    <input 
                        type="number" 
                        id="year"
                        value="2026"
                    >
                </div>
                <div class="form-group">
                    <label>
                        Mes
                    </label>
                    <input 
                        type="number"
                        id="month"
                        min="1"
                        max="12"
                        value="6"
                    >
                </div>
            </div>

            <div id="week-fields" class="dynamic-fields" style="display:none">
                <div class="form-group">
                    <label>
                        Inicio de semana
                    </label>

                    <input
                        type="date"
                        id="week_start"
                    >
                </div>
            </div>
        </div>

        <div class="controls">
            <div class="form-group">
                <label>
                    Vista
                </label>

                <select 
                    id="calendar_view"
                    onchange="changeCalendarView()"
                >

                    <option value="">
                        Seleccionar
                    </option>


                    <option value="month">
                        Mes
                    </option>


                    <option value="week">
                        Semana
                    </option>
                </select>
            </div>

            <button onclick="loadCalendar()">
                Consultar
            </button>
        </div>

        <div id="calendar" class="events">
            <div class="empty-state">
                Seleccione una vista para el calendario
            </div>
        </div>
    </div>
</body>
</html>
<script>
    function changeCalendarView(){
        const type = document.getElementById('calendar_view').value;
        const monthFields = document.getElementById('month-fields');
        const weekFields = document.getElementById('week-fields');

            if(type === 'month'){
                monthFields.style.display = "block";
                weekFields.style.display = "none";
            }

            if(type === 'week'){
                monthFields.style.display = "none";
                weekFields.style.display = "block";
            }

            if(type === ""){
                monthFields.style.display = "block";
                weekFields.style.display = "none";
            }
    }
    async function loadCalendar(){
        const container = document.getElementById('calendar');

        container.innerHTML = `
            <div>
                Cargando calendario...
            </div>
        `;

        const type = document.getElementById('calendar_view').value;

        if(!type){
            container.innerHTML = `
                <div>
                    Por favor, seleccione una vista para el calendario
                </div>
            `;
            return;
        }

        const date = new Date();
        const app_id = document.getElementById('app_id').value;
        const userauth_id = document.getElementById('userauth_id').value;
        const year = document.getElementById('year')?.value;
        const month = document.getElementById('month')?.value;

        const params = new URLSearchParams({
            app_id: app_id,
            userauth_id: userauth_id,
        });

        if(type === 'month'){
            params.append(
                'year',
                year
            );
            params.append(
                'month',
                month
            );
        }

        if(type === 'week'){
            const week_start = document.getElementById('week_start').value;

            if(!week_start){
                container.innerHTML = `
                    <div>
                        Por favor, seleccione la fecha de inicio de semana
                    </div>
                `;
                return;
            }

            params.append('week_start', week_start);
        }
        const response = await fetch(
            `/api/calendar/${type}?${params}`
        );

        const result = await response.json();
            console.log(result);
        renderCalendar(result.data);
    }

    function renderCalendar(calendar){
        const container = document.getElementById('calendar');

        container.innerHTML="";

        /*
            Datos que vienen del API:
            calendar.events
        */

        if(calendar.events.length === 0){

            container.innerHTML = `
                <div>
                    No existen eventos registrados
                </div>

            `;
            return;
        }

        calendar.events.forEach(event => {

            const div = document.createElement('div');

            div.className="day";

            div.innerHTML=`
                <strong>
                    ${event.title ?? 'Evento'}
                </strong>

                <div class="event">
                    ${event.start_time ?? ''}
                </div>
            `;
            container.appendChild(div);
        });
    }
</script>
<style>
    body {
        font-family: "Inter", Arial, sans-serif;
        padding:40px;
        background:#f1f5f9;
    }

    .calendar-container {
        max-width:1000px;
        margin:auto;
        background:white;
        padding:30px;
        border-radius:18px;
        box-shadow:0 10px 30px rgba(0,0,0,.08);
    }

    .calendar-container h2 {
        margin-bottom:25px;
        color:#1e293b;
    }

    .calendar-form {
        display:flex;
        flex-wrap:wrap;
        gap:20px;
        padding:20px;
        background:#f8fafc;
        border-radius:12px;
    }

    .form-group {
        display:flex;
        flex-direction:column;
        gap:8px;
    }

    .form-group label {
        font-size:14px;
        font-weight:600;
        color:#475569;
    }

    input,
    select {
        height:40px;
        padding:0 12px;
        border-radius:8px;
        border:1px solid #cbd5e1;
        background:white;
        font-size:14px;
    }

    input:focus,
    select:focus {
        outline:none;
        border-color:#2563eb;
        box-shadow:0 0 0 3px rgba(37,99,235,.15);
    }
    .dynamic-fields {
        display:flex;
        gap:20px;
    }

    .controls {
        display:flex;
        align-items:end;
        gap:20px;
        margin-top:25px;
    }

    button {
        height:40px;
        padding:0 25px;
        border:none;
        border-radius:8px;
        background:#2563eb;
        color:white;
        font-weight:600;
        cursor:pointer;
        transition:.2s;
    }

    button:hover {
        background:#1d4ed8;
    }

    .events {
        margin-top:30px;
        display:grid;
        grid-template-columns:repeat(7,1fr);
        gap:12px;
    }

    .day {
        min-height:120px;
        background:#f8fafc;
        border:1px solid #e2e8f0;
        padding:12px;
        border-radius:12px;
    }

    .event {
        margin-top:10px;
        padding:8px;
        border-radius:8px;
        background:#2563eb;
        color:white;
        font-size:13px;
    }

    .empty-state {
        grid-column:1 / -1;
        text-align:center;
        padding:40px;
        color:#64748b;
    }
</style>