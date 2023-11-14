const content = (process.env.TAILWIND_CONTENT_PATH || '').split(/:/);
console.info(`Using content=${content}.`)

module.exports = {
    darkMode: ['class', '[data-theme="dark"]'],
    content,
    safelist: [
        {
            // hack to allow also classes used from Django forms definitions
            pattern: /Forms__.+/,
        },
        {
            // TODO: till the https://github.com/esnvutbrno/fiesta-plus/issues/188 is fixed
            pattern: /(btn-.+)|(badge-.+)/,
            variants: ["checked"],
        },
        {
            pattern: /(SocialButton)/,
        },
        {
            pattern: /ring|ring-primary|ring-secondary|ring-gray-400/,
        },
    ],
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
                    "success": "#5df43f",
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
                    "success": "#5df43f",
                    "warning": "#FBBD23",
                    "error": "#F87272",

                    "primary-content": "#FFFFFF",
                    "secondary-content": "#FFFFFF",
                },
            },
        ],
    },
};
