const config = require('./webpack.base.config.js');
const webpack = require('webpack');

config.plugins.push(
    new webpack.DefinePlugin({
        // '__SENTRY_DSN__': '\'' + process.env.SENTRY_DSN + '\'',
        '__DEVELOPMENT__': 'false',
    }),
);

Object.assign(
    config.plugins[0].options,
    {
        // doesn't work with dev server :-|
        // https://github.com/esnvutbrno/buena-fiesta/issues/37
        integrity: true,
        integrityHashes: ['sha384'],
    }
)


module.exports = config;
