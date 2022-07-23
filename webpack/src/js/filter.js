import Alpine from "alpinejs";
import persist from "@alpinejs/persist";

Alpine.plugin(persist)
Alpine.store('tableFilter', {
    shown: Alpine.$persist(true).as('tableFilter_shown'),
    toggle() {
        this.shown = !this.shown
    },

    /**
     * Resets
     */
    reset(resetEl) {
        const form = resetEl.form;
        if (!form) return;

        for (const el of form.elements) {
            if (
                ['input', 'select'].includes(el.tagName.toLowerCase()) &&
                el.value
            ) {
                el.value = ''
            }
        }
    }
});
