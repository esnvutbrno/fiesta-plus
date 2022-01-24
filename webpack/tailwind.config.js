const colors = require('tailwindcss/colors');

module.exports = {
    content: [
        // docker placement of Django application
        '/usr/src/fiesta/**/*.html',
    ],
    theme: {
        colors: {
            primary: colors.rose['500'],
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
};
