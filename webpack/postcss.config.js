module.exports = {
    plugins: [
        require('postcss-import'),
        // require('postcss-url'),
        require('tailwindcss/nesting'),
        require('tailwindcss'),
        require('autoprefixer'),
        require('postcss-preset-env')({
            features: {'nesting-rules': false},
        }),

    ],
};
