from streamlit.components.v1 import declare_component


def register_panel(directory):
    return declare_component("hedef_panel", path=directory)
