const postcssPresetEnv = require('postcss-preset-env');

module.exports = {
    plugins: [
        require('postcss-import'),
        // require('postcss-url'),
        require('tailwindcss/nesting'),
        require('tailwindcss'),
        require('autoprefixer'),
        postcssPresetEnv({
            features: {
                'is-pseudo-class': false,  // not compatible with tailwind utilities currently
            },
        }),

    ],
};
