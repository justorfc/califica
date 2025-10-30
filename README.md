# rubrica-streamlit
Proyecto `rubrica-streamlit`: aplicación Streamlit + SQLite para gestionar rúbricas y evaluaciones.

El código de la app vive en la carpeta `rubrica-streamlit/`. Consulta `rubrica-streamlit/rubrica-streamlit/README.md` para instrucciones detalladas.

Comandos rápidos:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r rubrica-streamlit/requirements.txt
streamlit run rubrica-streamlit/app.py --server.port 8501
```

He marcado esta versión inicial con la etiqueta `v0.1.0` en el repositorio.

## Acceso y seguridad

Esta aplicación se distribuye y ejecuta como pública por defecto (no solicita contraseña en la interfaz). Si vas a ejecutarla en un entorno compartido o accesible desde Internet, considera una de las siguientes opciones para proteger el acceso:

- Colocar la app detrás de un proxy con autenticación (nginx, Traefik, Caddy) o un gateway que requiera autenticación/SSO.
- Habilitar control de acceso a nivel de red (firewall, reglas de VPN) y exponer sólo a la red institucional.

Si aún prefieres usar un archivo de secretos local (por ejemplo en desarrollo), puedes crear un fichero local en `.streamlit/secrets.toml` con la estructura siguiente (NO lo añadas al repositorio):

```toml
[default]
EVAL_KEY = "tu_clave_local_aqui"
```

Recuerda: no comprometas claves ni credenciales en el repositorio. Si detectas que una clave fue expuesta, rótala en el servicio correspondiente.
