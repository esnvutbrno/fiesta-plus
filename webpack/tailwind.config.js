const content = (process.env.TAILWIND_CONTENT_PATH || '').split(/:/);

module.exports = {
    darkMode: ['class', '[data-theme="dark"]'],
    content,
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/typography'),
        require('@tailwindcss/forms')({
            strategy: 'class',
        }),
        require('daisyui'),
    ],
    daisyui: {
        themes: [
            {
                light: {
                    "primary": "#f43f5e",
                    "secondary": "#7b3ff4",
                    "accent": "#FFBC0A",
                    "neutral": "#3D4451",
                    "base-100": "#FFFFFF",
                    "info": "#45c0f5",
                    "success": "#69DC9E",
                    "warning": "#FBBD23",
                    "error": "#F87272",

                    "primary-content": "#FFFFFF",
                    "secondary-content": "#FFFFFF",
                },
            },
            {
                dark: {
                    "primary": "#f43f5e",
                    "secondary": "#7b3ff4",
                    "accent": "#FFBC0A",
                    "neutral": "#3D4451",
                    "base-100": "#1A1423",
                    "info": "#45c0f5",
                    "success": "#69DC9E",
                    "warning": "#FBBD23",
                    "error": "#F87272",

                    "primary-content": "#FFFFFF",
                    "secondary-content": "#FFFFFF",
                },
            },
        ],
    },
};
