import './css/main.css';
import 'flowbite';
import Htmx from "htmx.org"
import Alpine from 'alpinejs'
import "./js/filter"

window.htmx = Htmx
window.Alpine = Alpine


document.body.addEventListener('htmx:configRequest', function (evt) {
    // removes all empty parameters from request
    for (const key in evt.detail.parameters) {
        if (!evt.detail.parameters[key]) delete evt.detail.parameters[key]
    }
});


Alpine.start()
