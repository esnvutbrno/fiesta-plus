import Alpine from "alpinejs";
import Select from 'tom-select'

Alpine.data('modelSelect', (selectEl) => ({
    choices: null,
    init() {
        const url = selectEl.dataset['ajax-Url']
        const field_id = selectEl.dataset.field_id
        const minimumInputLength = selectEl.dataset.minimumInputLength

        this.choices = new Select(
            selectEl,
            {
                // plugins: ['dropdown_input'],
                valueField: 'id',
                labelField: 'text',
                searchField: 'text',
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
