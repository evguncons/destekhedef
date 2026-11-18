from pathlib import Path

import requests
import streamlit as st
from streamlit.components.v1 import declare_component

ROOT = Path(__file__).resolve().parent
ENDPOINT = (ROOT / "endpoint.txt").read_text(encoding="utf-8").strip()
ERROR = {"ok": False, "error": {"code": "UPSTREAM", "message": "Apps Script bağlantısı kurulamadı. Web uygulaması dağıtımını kontrol edin."}}
panel = declare_component("hedef_panel", path=str(ROOT / "panel"))

st.set_page_config(page_title="Hedef AVM Şikayet Paneli", layout="wide")
st.html("<style>.block-container{max-width:100%;padding:0!important}header[data-testid=stHeader]{display:none}</style>")
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
