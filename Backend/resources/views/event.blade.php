<!DOCTYPE html>
<html lang="es">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Gestión de Eventos</title>

</head>
<body>
    <div class="dashboard-grid">
        <div class="card">
            <h2>
                Consultar Eventos
            </h2>

            <label>
                App ID
            </label>

            <input
            type="text"
            id="search_app_id"
            placeholder="Ejemplo: 1">
            <label>
                Userauth ID
            </label>

            <input
            type="text"
            id="search_userauth_id"
            placeholder="Ejemplo: 1">

            <label>
            ID Evento (opcional)
            </label>

            <input
            type="number"
            id="search_event_id"
            placeholder="Ejemplo: 5">

            <button 
            type="button"
            onclick="searchEvents()">

                Buscar
            </button>

            <button 
            type="button"
            onclick="getEventDetail()">
                Ver detalle
            </button>

            <button 
            type="button"
            onclick="exportEventsCSV()">
                Exportar CSV
            </button>
        </div>
        <div class="card">
            <h2>
            Crear Evento
            </h2>
        <div id="message"></div>
            <form id="eventForm">

                <input 
                type="hidden"
                id="event_id">

                <label>
                App ID
                </label>

                <input
                type="text"
                id="app_id"
                value="1"
                required>

                <label>
                Usuario ID
                </label>

                <input
                type="text"
                id="userauth_id"
                value="1"
                required>

                <label>
                Tipo de evento ID
                </label>

                <input
                type="number"
                id="event_type_id"
                placeholder="Ejemplo: 1"
                required>

                <label>
                Título
                </label>

                <input
                type="text"
                id="title"
                required>

                <label>
                Descripción
                </label>

                <textarea
                id="description"></textarea>

                <label>
                Fecha inicio
                </label>

                <input
                type="datetime-local"
                id="start_time"
                required>

                <label>
                Fecha fin
                </label>

                <input
                type="datetime-local"
                id="end_time"
                required>

                <button>
                Guardar Evento
                </button>
            </form>
        </div>

        <div class="card">
            <h2>
            Eventos registrados
            </h2>
            <table>
                <thead>
                    <tr>
                        <th>
                        Título
                        </th>

                        <th>
                        Inicio
                        </th>

                        <th>
                        Fin
                        </th>

                        <th>
                        Acciones
                        </th>
                    </tr>
                </thead>
                <tbody id="eventsTable">

                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
<script>
    const API="/api/events";
    const form = document.getElementById("eventForm");
    const table = document.getElementById("eventsTable");
    const message = document.getElementById("message");

    function showError(text){
        message.innerHTML=`

        <div class="alert">
            ${text}
        </div>
        `;
    }

    function clearMessage(){
        message.innerHTML="";
    }
    //Esta función carga los eventos registrados en la tabla
    async function loadEvents(app_id, userauth_id){

        const response = await fetch(
            `${API}?app_id=${app_id}&userauth_id=${userauth_id}`
        );

        const result = await response.json();

        table.innerHTML="";

        if(!result.data || result.data.length===0){
            table.innerHTML=`

            <tr>
                <td colspan="4">
                    No existen eventos registrados
                </td>
            </tr>
            `;
            return;
        }

        result.data.forEach(event=>{
            table.innerHTML +=`

            <tr>
                <td>
                    ${event.title}
                </td>

                <td>
                    ${event.start_time}
                </td>

                <td>
                    ${event.end_time}
                </td>

                <td>
                    <button 
                    class="edit"
                    onclick="editEvent(${event.id})">
                        Editar
                    </button>

                    <button
                    class="delete"
                    onclick="deleteEvent(${event.id})">
                        Eliminar
                    </button>
                </td>
            </tr>
        `;
        });
    }
    //Esta función se ejecuta al enviar el formulario de creación de evento y envía los datos al backend para crear un nuevo evento
    form.addEventListener(
        "submit",
        async(e)=>{
            e.preventDefault();

            clearMessage();

            const data={
                app_id: document.getElementById("app_id").value,
                userauth_id: document.getElementById("userauth_id").value,
                event_type_id: document.getElementById("event_type_id").value,
                title: document.getElementById("title").value,
                description: document.getElementById("description").value,
                start_time: document.getElementById("start_time").value,
                end_time: document.getElementById("end_time").value
            };

            const response = await fetch(API,{
                method:"POST",
                headers:{
                "Content-Type":"application/json",
                "Accept":"application/json"
            },
                body:JSON.stringify(data)
            });

            const result = await response.json();

            if(!response.ok){
                if(result.errors?.event_type_id){
                    showError(
                        "El tipo de evento seleccionado no existe. Primero debes crear un tipo de evento."
                    );
                }
                else{
                    showError(
                        result.message ?? "Error al crear evento"
                    );
                }
                return;
            }

            form.reset();
            loadEvents();
        }
    );
    //Esta función se ejecuta al hacer click en el botón "Buscar" y obtiene los eventos registrados para el App ID y Userauth ID ingresados
    async function searchEvents(){

        const app_id = document.getElementById("search_app_id").value;
        const userauth_id = document.getElementById("search_userauth_id").value;

        if(!app_id || !userauth_id){

            showError(
                "Debes ingresar App ID y Userauth ID"
            );
            return;
        }

        loadEvents(
        app_id,
        userauth_id
        );
    }
    //Esta funcion se encarga de buscar un evento detallado por id
    async function getEventDetail(){
        const event_id = document.getElementById("search_event_id").value;
        const app_id = document.getElementById("search_app_id").value;
        const userauth_id = document.getElementById("search_userauth_id").value;

        if(!event_id){
            showError(
                "Debes ingresar el ID del evento"
            );
            return;
        }

        const response = await fetch(
            `${API}/${event_id}?app_id=${app_id}&userauth_id=${userauth_id}`
        );

        const result = await response.json();

        if(!response.ok){
            showError(
                result.message ?? "Evento no encontrado"
            );
                return;
        }

        alert(
            `Evento: ${result.data.title}`
        );
    }
    async function exportEventsCSV(){
        const app_id = document.getElementById("search_app_id").value;
        const userauth_id = document.getElementById("search_userauth_id").value;

        if(!app_id || !userauth_id){
            showError(
                "Debes ingresar App ID y Userauth ID para exportar"
            );

            return;
        }

        const url = `${API}/export?app_id=${app_id}&userauth_id=${userauth_id}&format=csv`;

        window.open(url,"_blank");
    }
</script>
<style>
    body{
        font-family:Arial,sans-serif;
        background:#f1f5f9;
        margin:0;
        padding:30px;
        }

    .container{
        max-width:1200px;
        margin:auto;
    }

    h1{
        margin-bottom:30px;
    }

    .dashboard-grid{
        display:grid;
        grid-template-columns:300px 350px 1fr;
        gap:20px;
        align-items:start;
    }

    .card{
        background:white;
        padding:25px;
        border-radius:12px;
        box-shadow:0 4px 10px rgba(0,0,0,.08);
    }

    label{
        display:block;
        font-weight:bold;
        margin-top:15px;
    }

    input,
    textarea{
        width:100%;
        padding:10px;
        margin-top:5px;
        border:1px solid #ddd;
        border-radius:6px;
        box-sizing:border-box;
    }

    textarea{
        height:100px;
    }

    button{
        margin-top:20px;
        width:100%;
        padding:12px;
        background:#2563eb;
        color:white;
        border:0;
        border-radius:8px;
        cursor:pointer;
    }

    button:hover{
        background:#1d4ed8;
    }

    table{
        width:100%;
        border-collapse:collapse;
    }

    th{
        background:#f8fafc;
    }

    td,
    th{
        padding:12px;
        border-bottom:1px solid #ddd;
    }

    .actions button{
        width:auto;
        margin:0 5px;
        padding:8px 12px;
    }

    .edit{
        background:#16a34a;
    }

    .delete{
        background:#dc2626;
    }

    .alert{
        padding:12px;
        border-radius:8px;
        margin-bottom:15px;
        background:#fee2e2;
        color:#991b1b;
    }
</style>