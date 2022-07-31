import './css/main.css';
import htmx from "htmx.org"

import Alpine from 'alpinejs'
import "./js/filter"
import "./js/model-select"
import "./js/modal"
import AlpineCollapse from '@alpinejs/collapse'

Alpine.plugin(AlpineCollapse)

window.htmx = htmx
htmx.config.defaultFocusScroll = false;

window.Alpine = Alpine


document.body.addEventListener('htmx:configRequest', function (evt) {
    // removes all empty parameters from request
    for (const key in evt.detail.parameters) {
        if (!evt.detail.parameters[key]) delete evt.detail.parameters[key]
    }
});


Alpine.start()
