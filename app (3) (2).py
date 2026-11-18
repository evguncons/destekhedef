from pathlib import Path

import requests
import streamlit as st
from streamlit.components.v1 import declare_component

ROOT = Path(__file__).resolve().parent
ENDPOINT = 'https://script.google.com/macros/s/AKfycbyii3UgQxR3Y3DUdPO6RO3S8Y8GS3DwIlx267txMHHnWNKE_WO6XOOG_D3mS5vtn91G/exec'
ERROR = {"ok": False, "error": {"code": "UPSTREAM", "message": "Apps Script bağlantısı kurulamadı. Web uygulaması dağıtımını kontrol edin."}}
panel = declare_component("hedef_panel", path=str(ROOT / "panel"))

st.set_page_config(page_title="HEDEF AVM DESTEK", page_icon="🏆", layout="wide")
st.html('''
<style>
header[data-testid="stHeader"], footer, #MainMenu, .stDeployButton { display:none; }
body, [data-testid="stMain"] { overflow:hidden; margin:0; }
.block-container { padding:0!important; margin:0!important; max-width:100%!important; }
iframe[title$=".hedef_panel"] { position:fixed; inset:0; width:100vw; height:100dvh!important; border:0; z-index:999999; }
</style>
''')
if not (ROOT / "panel" / "index.html").is_file():
    st.error("Panel HTML dosyasını panel/index.html yoluna ekleyin.")
    st.stop()
response = st.session_state.get("panel_response")
event = panel(response=response, key="hedef_panel", default=None)
if isinstance(event, dict) and isinstance(event.get("id"), str):
    event_id = event["id"]
    if not response or response["id"] != event_id:
        body = event.get("request")
        result = ERROR
        if isinstance(body, str) and len(body.encode("utf-8")) <= 256000:
            try:
                upstream = requests.post(ENDPOINT, data=body.encode("utf-8"),
                                         headers={"Content-Type": "application/json"},
                                         timeout=(10, 370))
                upstream.raise_for_status()
                value = upstream.json()
                if isinstance(value, dict) and isinstance(value.get("ok"), bool):
                    result = value
            except requests.Timeout:
                result = {"ok": False, "error": {"code": "BACKEND_TIMEOUT", "message": "Apps Script zamanında yanıt vermedi. Aynı dosyayla kaldığınız yerden devam edebilirsiniz."}}
            except (requests.RequestException, ValueError):
                pass
        st.session_state.panel_response = {"id": event_id, "result": result}
        st.rerun()
