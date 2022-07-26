import Alpine from "alpinejs";
import persist from "@alpinejs/persist";

Alpine.plugin(persist)
Alpine.store('tableControls', {
    shown: Alpine.$persist(true).as('tableControls_shown'),
    isFilterActive: false,
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
