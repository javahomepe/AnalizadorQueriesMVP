const form = document.querySelector("#analysis-form");
const output = document.querySelector("#output");
const statusBadge = document.querySelector("#status");
const button = form.querySelector("button");
const accessKey = document.querySelector("#access-key");

accessKey.value = sessionStorage.getItem("analizador-access-key") || "";

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const key = accessKey.value.trim();
  if (!key) {
    output.textContent = "Ingrese la clave de acceso de la demostración.";
    statusBadge.textContent = "Protegido";
    accessKey.focus();
    return;
  }
  sessionStorage.setItem("analizador-access-key", key);
  const pregunta = [
    "Analiza el riesgo de esta consulta SQL de producción.",
    `Usuario: ${document.querySelector("#usuario").value}.`,
    `Perfil: ${document.querySelector("#perfil").value}.`,
    `Hora de ejecución: ${document.querySelector("#hora").value}.`,
    `Intención: ${document.querySelector("#intencion").value}.`,
    `Esquema autorizado: ${document.querySelector("#schema").value}.`,
    "SQL:",
    document.querySelector("#query").value,
  ].join("\n");

  button.disabled = true;
  statusBadge.textContent = "Analizando";
  output.textContent = "Consultando al agente y al servidor MCP…";
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json", "X-API-Key": key},
      body: JSON.stringify({pregunta}),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload?.error?.message || "No fue posible completar el análisis.");
    output.textContent = payload.respuesta;
    statusBadge.textContent = "Completado";
  } catch (error) {
    output.textContent = `Error: ${error.message}`;
    statusBadge.textContent = "Error";
  } finally {
    button.disabled = false;
  }
});
