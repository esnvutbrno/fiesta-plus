import Alpine from "alpinejs";
import Select from 'tom-select'

Alpine.data('modelSelect', (el) => ({
    select: null,
    async init() {
        /*
         * One big WTF, spent three hours on this:
         * In situations, where HTMX is used and just made the swap,
         * Alpine inits the component again with TomSelect constructor.
         * Somehow, for the second time of init, the given element in TomSelect
         * is directed to NEW element (which is kept shown), not the SELECT itself.
         * So the wrong result is two shown elements on page (the should-be-masked one
         * and the new inserted input by tomselect)
         *
         * I've tried Alpine.nextTick, alpine-moph, promise initialization, and nope :-(
         */
        setTimeout(() => {
            if (this.select) {
                this.select.destroy()
            }
            if (el.tomselect) {
                el.tomselect.destroy()
            }

            this.select = this.initSelect(el)
        }, 100)
    },
    initSelect(el) {
        const url = el.dataset['ajax-Url']
        const field_id = el.dataset.field_id
        const minimumInputLength = el.dataset.minimumInputLength

        return new Select(
            el,
            {
                // plugins: ['dropdown_input'],
                valueField: 'id',
                labelField: 'text',
                searchField: 'text',
                // overwrite default ".loading" since it has conflict with DaisyUI loading component
                loadingClass: 'ts-loading',
                shouldLoad(term) {
                    return term.trim().length >= minimumInputLength
                },
                load(term, callback) {
                    const builtUrl = url + '?' + new URLSearchParams({
                        term, field_id
                    })

                    try {
                        return fetch(builtUrl)
                            .then(res => res.json())
                            .then(json => callback(json.results))
                    } catch (e) {
                        return callback()
                    }
                },
                render: {
                    item(item, escape) {
                        return `<div>${escape(item.text)}</div>`
                    },
                    option(item, escape) {
                        return `<div>${escape(item.text)}</div>`
                    },
                    not_loading: function (data, escape) {
                        const missing = minimumInputLength - data.input.trim().length
                        return `<div class="option">Type ${missing} more chars...</div>`;
                    },
                }
            }
        )
    }
}))
