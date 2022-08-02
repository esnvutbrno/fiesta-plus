import Alpine from "alpinejs";

Alpine.store('darkMode', {
    on: Alpine.$persist(true).as('darkMode_on'),

    init() {
        Alpine.effect(() => {
            document.documentElement.dataset.theme = ['light', 'dark'][this.on ? 1 : 0];
        });
    },
});
