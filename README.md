# WhatsApp CRM Flask Backend

Este backend:

1. Recibe un número de teléfono y un mensaje desde una extensión de Chrome.
2. Usa OpenAI para extraer nombre, apellido, carrera y estado del contacto.
3. Envía los datos a una Google Sheet mediante un Google Apps Script Web App.

## Cómo usarlo

1. Renombrá `.env.example` a `.env` y completá tu API Key y URL del Web App.
2. Subí este proyecto a GitHub y conectalo a Render.
3. Usá la extensión de Chrome para enviar mensajes a `/procesar-mensaje`.

## Formato esperado del JSON

```json
{
  "telefono": "+5491122334455",
  "mensaje": "Hola, soy Ana Pérez y me interesa Ingeniería en Informática"
}
```