import Alpine from "alpinejs";
import htmx from "htmx.org"

Alpine.data('modal', (href = null) => ({
    href,
    bind: {
        ['@click.stop'](e) {
            // to in another tab? keep the modal magic disabled
            if (e.ctrlKey) return;

            e.preventDefault()
            Alpine.store('modal').open(this.href)
        }
    }
}));


Alpine.store('modal', {
    backdropShown: false,
    contentShown: false,
    loadingShown: false,

    elementId: 'alpine-modal',
    close() {
        this.backdropShown = this.contentShown = false;
    },
    async open(url) {
        const preloaderTimeout = setTimeout(() => {
            this.backdropShown = true;
            this.loadingShown = true;
        }, 200)

        await htmx.ajax('GET', url, '#' + this.elementId)

        clearTimeout(preloaderTimeout)

        this.backdropShown = true;
        this.loadingShown = false;
        // wait for the content to be rendered and loading to be hidden
        setTimeout(() => this.contentShown = true, 100)
    }
})
