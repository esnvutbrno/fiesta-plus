const colors = require('tailwindcss/colors');

const content = (process.env.TAILWIND_CONTENT_PATH || '').split(/:/);

module.exports = {
    content,
    theme: {
        extend: {
            colors: {
                primary: colors.rose['500'],
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/forms')({
            strategy: 'class',
        }),
    ],
};
