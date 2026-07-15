# Autor: Castillo Casado, Ana Chenyu
# 2026
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import subprocess
import webbrowser
import threading
import time
import urllib.parse
import sys
import os
import json
import signal
from cli import obtener_repo_root


# ============================================================
# CONFIGURACIÓN
# ============================================================

#PUERTO = 8000 
# se pasa como parametro

# Si este programa se ejecuta desde ejecutar_analizador.bat, déjalo en True.
# Si lo ejecutas desde PyCharm, VSCode o una consola que NO quieras cerrar,
# ponlo en False.
CERRAR_CMD_PADRE_AL_CERRAR = True

PID_PADRE = os.getppid()


# ============================================================
# UTF-8
# ============================================================

# Fuerza UTF-8 también en este lanzador.
# Esto evita errores de codificación en Windows cuando aparecen caracteres
# que no existen en cp1252/charmap.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


os.environ["PYTHONPATH"] = "src"
os.environ["PYTHONIOENCODING"] = "utf-8:replace"
os.environ["PYTHONUTF8"] = "1"

sys.path.insert(0, "src")


# ============================================================
# RUTAS
# ============================================================

repo_root = Path(obtener_repo_root()).resolve()
os.chdir(repo_root)

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# ESTADO GLOBAL
# ============================================================

proceso_actual = None
historial_salida = []
proceso_finalizado = True
condicion_salida = threading.Condition()
servidor_http = None


# ============================================================
# SALIDA DEL PROCESO
# ============================================================

def agregar_salida(texto):
    global historial_salida

    if texto is None:
        return

    with condicion_salida:
        historial_salida.append(str(texto))
        condicion_salida.notify_all()


def leer_salida_proceso(proceso):
    """
    Lee la salida del proceso como texto UTF-8.

    No decodifica byte a byte, porque eso puede generar caracteres corruptos
    como � y provocar errores UnicodeEncodeError en Windows.
    Además, agrupa la salida para no saturar el navegador.
    """
    global proceso_actual
    global proceso_finalizado

    buffer = []
    ultimo_envio = time.monotonic()

    def volcar_buffer():
        nonlocal buffer
        nonlocal ultimo_envio

        if buffer:
            agregar_salida("".join(buffer))
            buffer = []
            ultimo_envio = time.monotonic()

    try:
        while True:
            caracter = proceso.stdout.read(1)

            if not caracter:
                break

            buffer.append(caracter)

            ahora = time.monotonic()

            if (
                caracter in ("\n", "\r")
                or len(buffer) >= 200
                or ahora - ultimo_envio >= 0.05
            ):
                volcar_buffer()

        volcar_buffer()

    except Exception as error:
        agregar_salida(f"\n[ERROR leyendo salida del proceso: {error}]\n")

    codigo = proceso.wait()

    agregar_salida(f"\n[Script finalizado con código {codigo}]\n")

    with condicion_salida:
        if proceso_actual is proceso:
            proceso_actual = None

        proceso_finalizado = True
        condicion_salida.notify_all()


# ============================================================
# EJECUCIÓN DEL SCRIPT
# ============================================================

def iniciar_script():
    global proceso_actual
    global historial_salida
    global proceso_finalizado

    script = repo_root / "src" / "analizador_calidad_software" / "__main__.py"

    print("script:", script)

    if not script.exists():
        return False, "No se encontró __main__.py"

    with condicion_salida:
        if proceso_actual is not None and proceso_actual.poll() is None:
            return False, "El script ya está en ejecución."

        historial_salida = []
        proceso_finalizado = False

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8:replace"
    env["PYTHONUTF8"] = "1"

    popen_kwargs = {}

    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    try:
        proceso = subprocess.Popen(
            [sys.executable, "-u", str(script)],
            cwd=str(repo_root),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            **popen_kwargs
        )

    except Exception as error:
        with condicion_salida:
            proceso_finalizado = True
            condicion_salida.notify_all()

        return False, f"No se pudo iniciar el script: {error}"

    with condicion_salida:
        proceso_actual = proceso
        historial_salida.append("[Script iniciado]\n")
        condicion_salida.notify_all()

    threading.Thread(
        target=leer_salida_proceso,
        args=(proceso,),
        daemon=True
    ).start()

    return True, "Script iniciado correctamente."


def enviar_entrada_a_script(texto):
    global proceso_actual

    with condicion_salida:
        proceso = proceso_actual

    if proceso is None or proceso.poll() is not None:
        return False, "No hay ningún script en ejecución."

    try:
        proceso.stdin.write(texto + "\n")
        proceso.stdin.flush()
        return True, "Entrada enviada."

    except Exception as error:
        return False, f"No se pudo enviar la entrada: {error}"


# ============================================================
# CIERRE DE PROCESOS
# ============================================================

def terminar_proceso_actual():
    """
    Cierra el script __main__.py si está ejecutándose.

    En Windows usa taskkill para cerrar también posibles procesos hijos.
    """
    global proceso_actual
    global proceso_finalizado

    with condicion_salida:
        proceso = proceso_actual

    if proceso is None:
        with condicion_salida:
            proceso_finalizado = True
            condicion_salida.notify_all()
        return

    if proceso.poll() is not None:
        with condicion_salida:
            if proceso_actual is proceso:
                proceso_actual = None

            proceso_finalizado = True
            condicion_salida.notify_all()
        return

    try:
        agregar_salida("\n[Cerrando proceso solicitado por el usuario]\n")

        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(proceso.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            os.killpg(os.getpgid(proceso.pid), signal.SIGTERM)

    except Exception as error:
        agregar_salida(f"\n[ERROR cerrando el proceso: {error}]\n")

        try:
            proceso.terminate()
        except Exception:
            pass

    with condicion_salida:
        if proceso_actual is proceso:
            proceso_actual = None

        proceso_finalizado = True
        condicion_salida.notify_all()


def cerrar_cmd_padre_windows():
    """
    Intenta cerrar la ventana CMD que ejecutó el .bat.

    Ojo:
    - Si el programa se lanzó desde ejecutar_analizador.bat, esto es útil.
    - Si se lanzó desde un IDE o una terminal que no quieres cerrar, pon
      CERRAR_CMD_PADRE_AL_CERRAR = False.
    """
    if os.name != "nt":
        return

    if not CERRAR_CMD_PADRE_AL_CERRAR:
        return

    if PID_PADRE <= 0:
        return

    try:
        comando = (
            f'timeout /t 1 /nobreak >nul '
            f'& taskkill /PID {PID_PADRE} /T /F >nul 2>&1'
        )

        subprocess.Popen(
            ["cmd", "/c", comando],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    except Exception:
        pass


def apagar_servidor():
    """
    Apaga el servidor HTTP.
    """
    global servidor_http

    time.sleep(0.5)

    if servidor_http is not None:
        try:
            servidor_http.shutdown()
        except Exception:
            pass


# ============================================================
# SERVIDOR HTTP
# ============================================================

class LanzadorHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        """
        Hace que el servidor sirva archivos desde BASE_DIR.
        """
        path = urllib.parse.urlparse(path).path
        path = path.lstrip("/")
        return str(BASE_DIR / path)

    def do_GET(self):
        ruta = urllib.parse.urlparse(self.path).path

        if ruta == "/" or ruta == "/index.html":
            self.servir_index()
            return

        if ruta == "/ejecutar":
            self.ejecutar_main()
            return

        if ruta == "/stream":
            self.stream_salida()
            return

        super().do_GET()

    def do_POST(self):
        ruta = urllib.parse.urlparse(self.path).path

        if ruta == "/stdin":
            self.recibir_entrada()
            return

        if ruta == "/cerrar_aplicacion":
            self.cerrar_aplicacion()
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        """
        Evita llenar la consola del .bat con peticiones HTTP.
        """
        pass

    def servir_index(self):
        html = generar_html()

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8", errors="replace"))

    def responder_json(self, codigo, datos):
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        respuesta = json.dumps(datos, ensure_ascii=False)
        self.wfile.write(respuesta.encode("utf-8", errors="replace"))

    def ejecutar_main(self):
        ok, mensaje = iniciar_script()

        if ok:
            self.responder_json(200, {
                "ok": True,
                "mensaje": mensaje
            })
        else:
            self.responder_json(409, {
                "ok": False,
                "mensaje": mensaje
            })

    def recibir_entrada(self):
        longitud = int(self.headers.get("Content-Length", 0))
        cuerpo = self.rfile.read(longitud).decode("utf-8", errors="replace")

        try:
            datos = json.loads(cuerpo)
            texto = datos.get("texto", "")
        except Exception:
            self.responder_json(400, {
                "ok": False,
                "mensaje": "Petición JSON no válida."
            })
            return

        ok, mensaje = enviar_entrada_a_script(texto)

        if ok:
            self.responder_json(200, {
                "ok": True,
                "mensaje": mensaje
            })
        else:
            self.responder_json(409, {
                "ok": False,
                "mensaje": mensaje
            })

    def cerrar_aplicacion(self):
        terminar_proceso_actual()

        self.responder_json(200, {
            "ok": True,
            "mensaje": "Aplicación cerrándose."
        })

        threading.Thread(
            target=apagar_servidor,
            daemon=True
        ).start()

    def enviar_evento_sse(self, datos):
        payload = "data: " + json.dumps(datos, ensure_ascii=False) + "\n\n"
        self.wfile.write(payload.encode("utf-8", errors="replace"))
        self.wfile.flush()

    def stream_salida(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        indice = 0

        try:
            while True:
                with condicion_salida:
                    while indice >= len(historial_salida) and not proceso_finalizado:
                        condicion_salida.wait(timeout=10)

                    nuevos_mensajes = historial_salida[indice:]
                    indice = len(historial_salida)

                    fin = proceso_finalizado and indice >= len(historial_salida)

                for texto in nuevos_mensajes:
                    self.enviar_evento_sse({
                        "texto": texto,
                        "fin": False
                    })

                if fin:
                    self.enviar_evento_sse({
                        "texto": "",
                        "fin": True
                    })
                    break

        except BrokenPipeError:
            pass

        except ConnectionResetError:
            pass


# ============================================================
# HTML
# ============================================================

def generar_html():
    return r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Analizador de Calidad Software</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f8;
            margin: 0;
            padding: 0 0 340px 0;
            text-align: center;
        }

        .cabeceraIzquierda {
            position: fixed;
            top: 8px;
            left: 8px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 6px;
            text-align: left;
        }

        .logoCabecera {
            width: 130px;
            height: 130px;
            object-fit: contain;
            border: none;
            border-radius: 0;
            margin: 0;
        }

        .textosCabecera {
            font-size: 12px;
            color: #1f4e79;
            font-weight: bold;
            line-height: 1.3;
        }

        #btnCerrarAplicacion {
            position: fixed;
            top: 12px;
            right: 12px;
            z-index: 10000;
            background-color: #8b0000;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 9px 14px;
            font-weight: bold;
            cursor: pointer;
        }

        #btnCerrarAplicacion:hover {
            background-color: #5f0000;
        }

        .contenedor {
            width: 70%;
            max-width: 950px;
            margin: 25px auto;
            background-color: white;
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 0 12px rgba(0, 0, 0, 0.15);
        }

        h1 {
            color: #1f4e79;
            margin-bottom: 10px;
            font-size: 34px;
        }

        .descripcion {
            color: #555;
            font-size: 17px;
            margin-bottom: 30px;
        }

        img {
            width: 60%;
            max-width: 500px;
            border-radius: 8px;
            border: 1px solid #ddd;
            margin-bottom: 30px;
        }

        .boton {
            display: inline-block;
            padding: 14px 32px;
            background-color: #1f4e79;
            color: white;
            text-decoration: none;
            font-size: 18px;
            border-radius: 8px;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }

        .boton:hover {
            background-color: #F87C63; 
        }

        .boton:disabled {
            background-color: #FEF2F2;
            cursor: not-allowed;
        }

        .nota {
            margin-top: 22px;
            font-size: 14px;
            color: #666;
        }
        .lineaBlanca {
            height: 8px;
        }

        #consola {
            display: none;
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            height: 300px;
            background-color: #111;
            color: #00ff66;
            border-top: 4px solid #1f4e79;
            font-family: Consolas, monospace;
            z-index: 9999;
            text-align: left;
        }

        #cabeceraConsola {
            height: 34px;
            line-height: 34px;
            background-color: #1f4e79;
            color: white;
            padding: 0 12px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-sizing: border-box;
        }

        #btnCerrarConsola {
            display: none;
            background-color: white;
            color: #1f4e79;
            border: none;
            border-radius: 5px;
            padding: 5px 12px;
            font-weight: bold;
            cursor: pointer;
        }

        #btnCerrarConsola:hover {
            background-color: #e6e6e6;
        }

        #salida {
            height: 215px;
            overflow-y: auto;
            padding: 12px;
            white-space: pre-wrap;
            box-sizing: border-box;
            font-size: 14px;
        }

        #zonaEntrada {
            display: flex;
            height: 51px;
            border-top: 1px solid #333;
        }

        #entrada {
            flex: 1;
            background-color: #222;
            color: white;
            border: none;
            padding: 0 12px;
            font-family: Consolas, monospace;
            font-size: 15px;
            outline: none;
        }

        #entrada:disabled {
            background-color: #333;
            color: #aaa;
        }

        #btnEnviar {
            width: 110px;
            background-color: #1f4e79;
            color: white;
            border: none;
            font-weight: bold;
            cursor: pointer;
        }

        #btnEnviar:hover {
            background-color: #163a59;
        }

        #btnEnviar:disabled {
            background-color: #555;
            cursor: not-allowed;
        }
    </style>
</head>

<body>
    <div class="cabeceraIzquierda">
        <img class="logoCabecera" src="/logoUAH.png" alt="Logo">

        <div class="textosCabecera">
            <div>TFG GISI</div>
            <div class="lineaBlanca"></div>
            <div>Autor: Castillo Casado, Ana Chenyu</div>
            <div>Tutor: Bueno Guillén, Francisco Javier</div>
            <div class="lineaBlanca"></div>
            <div>Curso: 2025/2026</div>
        </div>
    </div>

    <button id="btnCerrarAplicacion" title="Cerrar aplicación">
        ✕ Cerrar aplicación
    </button>

    <div class="contenedor">
        <h1>Analizador de Calidad Software</h1>

        <p class="descripcion">
            Aplicación para analizar proyectos software mediante métricas de calidad y generar un informe de resultados.
        </p>

        <img src="/imagen_inicio.png" alt="Imagen inicial del programa">

        <br>

        <button id="btnIniciar" class="boton">
            Iniciar programa
        </button>

        
    </div>

    <div id="consola">
        <div id="cabeceraConsola">
            <span>Proceso metricas y grafos</span>
            <button id="btnCerrarConsola">Cerrar</button>
        </div>

        <div id="salida"></div>

        <div id="zonaEntrada">
            <input id="entrada" type="text" placeholder="Escribe aquí si el programa pide datos por teclado...">
            <button id="btnEnviar">Enviar</button>
        </div>
    </div>

    <script>
        const btnCerrarAplicacion = document.getElementById("btnCerrarAplicacion");
        const btnIniciar = document.getElementById("btnIniciar");
        const consola = document.getElementById("consola");
        const salida = document.getElementById("salida");
        const entrada = document.getElementById("entrada");
        const btnEnviar = document.getElementById("btnEnviar");
        const btnCerrarConsola = document.getElementById("btnCerrarConsola");

        let stream = null;
        let bufferSalida = "";
        let refrescoPendiente = false;
        let textoSalida = document.createTextNode("");

        salida.appendChild(textoSalida);

        function escribir(texto) {
            bufferSalida += texto;

            if (!refrescoPendiente) {
                refrescoPendiente = true;

                requestAnimationFrame(function() {
                    textoSalida.nodeValue += bufferSalida;
                    bufferSalida = "";
                    salida.scrollTop = salida.scrollHeight;
                    refrescoPendiente = false;
                });
            }
        }

        function limpiarSalida() {
            bufferSalida = "";
            textoSalida.nodeValue = "";
            salida.scrollTop = 0;
        }

        function prepararConsolaParaEjecucion() {
            consola.style.display = "block";
            limpiarSalida();

            entrada.disabled = false;
            btnEnviar.disabled = false;
            entrada.placeholder = "Escribe aquí si el programa pide datos por teclado...";
            entrada.value = "";

            btnCerrarConsola.style.display = "none";

            btnIniciar.disabled = true;
            btnIniciar.style.color = "Black";
            btnIniciar.textContent = "Programa en ejecución...";

            entrada.focus();
        }

        function finalizarConsola() {
            escribir("\nEl proceso ha terminado.\n");

            entrada.disabled = true;
            btnEnviar.disabled = true;
            entrada.placeholder = "Proceso terminado.";

            btnCerrarConsola.style.display = "inline-block";

            btnIniciar.disabled = false;
            btnIniciar.textContent = "Iniciar programa";

            if (stream !== null) {
                stream.close();
                stream = null;
            }
        }

        function finalizarConsolaConError() {
            entrada.disabled = true;
            btnEnviar.disabled = true;
            entrada.placeholder = "Proceso detenido.";

            btnCerrarConsola.style.display = "inline-block";

            btnIniciar.disabled = false;
            btnIniciar.textContent = "Iniciar programa";

            if (stream !== null) {
                stream.close();
                stream = null;
            }
        }

        function cerrarConsola() {
            consola.style.display = "none";
        }

        function abrirStream() {
            if (stream !== null) {
                stream.close();
            }

            stream = new EventSource("/stream");

            stream.onmessage = function(evento) {
                const datos = JSON.parse(evento.data);

                if (datos.texto) {
                    escribir(datos.texto);
                }

                if (datos.fin) {
                    finalizarConsola();
                }
            };

            stream.onerror = function() {
                if (stream !== null) {
                    escribir("\n[Se perdió la conexión con la salida del programa]\n");
                    stream.close();
                    stream = null;
                }

                finalizarConsolaConError();
            };
        }

        btnIniciar.addEventListener("click", async function() {
            prepararConsolaParaEjecucion();

            try {
                const respuesta = await fetch("/ejecutar");
                const datos = await respuesta.json();

                if (!respuesta.ok || !datos.ok) {
                    escribir("[ERROR: " + datos.mensaje + "]\n");
                    finalizarConsolaConError();
                    return;
                }

                escribir(datos.mensaje + "\n");
                abrirStream();

            } catch (error) {
                escribir("[ERROR al iniciar el programa: " + error + "]\n");
                finalizarConsolaConError();
            }
        });

        async function enviarEntrada() {
            const texto = entrada.value;

            if (texto.trim() === "") {
                entrada.focus();
                return;
            }

            escribir("> " + texto + "\n");
            entrada.value = "";

            try {
                const respuesta = await fetch("/stdin", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        texto: texto
                    })
                });

                const datos = await respuesta.json();

                if (!respuesta.ok) {
                    escribir("[ERROR: " + datos.mensaje + "]\n");
                }

            } catch (error) {
                escribir("[ERROR enviando entrada: " + error + "]\n");
            }

            entrada.focus();
        }

        btnEnviar.addEventListener("click", enviarEntrada);

        btnCerrarConsola.addEventListener("click", cerrarConsola);

        entrada.addEventListener("keydown", function(evento) {
            if (evento.key === "Enter") {
                enviarEntrada();
            }
        });

        btnCerrarAplicacion.addEventListener("click", async function() {
            const confirmar = confirm(
                "¿Seguro que quieres cerrar la aplicación?\n\n" +
                "Se cerrará el proceso en ejecución, el servidor local y la ventana del .bat "
            );

            if (!confirmar) {
                return;
            }

            try {
                if (stream !== null) {
                    stream.close();
                    stream = null;
                }

                await fetch("/cerrar_aplicacion", {
                    method: "POST"
                });

                document.body.innerHTML = `
                    <div style="
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin-top: 120px;
                    ">
                        <h1>Aplicación cerrada</h1>
                        <p>El servidor y el proceso se han detenido.</p>
                        <p>Si esta pestaña no se cierra automáticamente, puedes cerrarla manualmente.</p>
                    </div>
                `;

                setTimeout(function() {
                    window.close();
                }, 300);

            } catch (error) {
                alert("No se pudo cerrar correctamente la aplicación: " + error);
                setTimeout(function() {
                    window.close();
                }, 300);
            }
        });
    </script>
</body>
</html>
"""


# ============================================================
# ARRANQUE
# ============================================================

def abrir_navegador():
    time.sleep(1)
    webbrowser.open(f"http://127.0.0.1:{PUERTO}")


def main():
    global servidor_http
    global PUERTO
    # sys.argv[0] es el nombre del script
    # sys.argv[1] sería el primer parámetro pasado
    try:
        if len(sys.argv) < 2:
            raise ValueError("Debes pasar al menos un parámetro al ejecutar el programa.")

        # Asignar el primer parámetro a una variable
        PUERTO = int(sys.argv[1])

        # Ejemplo de uso
        print(f"Puerto recibido: {PUERTO}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Uso: python script.py <parametro>")
        sys.exit(1)

    servidor_http = ThreadingHTTPServer(("127.0.0.1", PUERTO), LanzadorHandler)

    print(f"Servidor iniciado en http://127.0.0.1:{PUERTO}")
    print("Para detenerlo cierralo desde la pagina del navegador 'Cerrar aplicación' o Pulsa 2 veces Ctrl+C ")
    threading.Thread(target=abrir_navegador, daemon=True).start()

    try:
        servidor_http.serve_forever()

    except KeyboardInterrupt:
        print("\nServidor detenido.")

    finally:
        terminar_proceso_actual()

        try:
            servidor_http.server_close()
        except Exception:
            pass

        cerrar_cmd_padre_windows()


if __name__ == "__main__":
    main()
