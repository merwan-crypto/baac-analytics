import streamlit as st
import base64
from streamlit.components.v1 import html

from PATHS import NAVBAR_PATHS, SETTINGS


def inject_custom_css():
    with open('src/assets/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def navbar_component():
    with open("src/assets/images/settings.png", "rb") as image_file:
        image_as_base64 = base64.b64encode(image_file.read())

    navbar_items = ''
    for key, value in NAVBAR_PATHS.items():
        navbar_items += (f'<li><a class="navitem" href="/?nav=%2F{value}"><span class="nav-label">{key}</span></a></li>')

    settings_items = ''
    for key, value in SETTINGS.items():
        settings_items += (
            f'<a href="/?nav={value}" class="settingsNav">{key}</a>')

    component = rf'''
            <div class="navbar-wrap">
                <nav class="navbar" id="navbar">
                    <div class="nav-container">
                        <div class="brand">
                            <a href="/?nav=%2Fhome" class="brand-link">🚀 DataRockstars</a>
                        </div>
                        <ul class="navlist">
                            {navbar_items}
                        </ul>
                        <div class="dropdown" id="settingsDropDown">
                            <img class="dropbtn" alt="settings" src="data:image/png;base64, {image_as_base64.decode("utf-8")}"/>
                            <div id="myDropdown" class="dropdown-content">
                                {settings_items}
                            </div>
                        </div>
                    </div>
                </nav>
            </div>
            '''
    st.markdown(component, unsafe_allow_html=True)
    js = '''
    <script>
        // navbar elements
        var navigationTabs = window.parent.document.getElementsByClassName("navitem");
        var cleanNavbar = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < navigationTabs.length; i++) {
            cleanNavbar(navigationTabs[i]);
        }
        
        // Dropdown hide / show
        var dropdown = window.parent.document.getElementById("settingsDropDown");
        dropdown.onclick = function() {
            var dropWindow = window.parent.document.getElementById("myDropdown");
            if (dropWindow.style.opacity == "1"){
                dropWindow.style.opacity = "0";
                dropWindow.style.pointerEvents = "none";
            } else {
                dropWindow.style.opacity = "1";
                dropWindow.style.pointerEvents = "auto";
            }
        };
        
        var settingsNavs = window.parent.document.getElementsByClassName("settingsNav");
        var cleanSettings = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < settingsNavs.length; i++) {
            cleanSettings(settingsNavs[i]);
        }
    </script>
    '''
    html(js)
