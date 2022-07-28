import Alpine from "alpinejs";
import Select from 'tom-select'

Alpine.data('modelSelect', (selectEl) => ({
    choices: null,
    init() {
        const url = selectEl.dataset['ajax-Url']
        const field_id = selectEl.dataset['field_id']

        this.choices = new Select(
            selectEl,
            {
                valueField: 'id',
                labelField: 'text',
                searchField: 'term',
                async load(term, callback) {
                    const builtUrl = url + '?' + new URLSearchParams({
                        term, field_id
                    })
                    try {
                        const json = await (await fetch(builtUrl)).json();

                        callback(json.results)
                    } catch (e) {
                        console.warn(e)
                        callback()
                    }
                },
            }
        )
    }
}))