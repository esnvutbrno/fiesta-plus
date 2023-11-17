const config = require('./webpack.base.config.js');
const webpack = require('webpack');
const {
    sentryWebpackPlugin
} = require("@sentry/webpack-plugin");

config.plugins.push(
    new webpack.DefinePlugin({
        '__DEVELOPMENT__': 'false',
    }),
    sentryWebpackPlugin({
        authToken: process.env.SENTRY_WEBPACK_AUTH_TOKEN,
        org: process.env.SENTRY_ORG,
        project: process.env.SENTRY_PROJECT,
    })
);

Object.assign(
    config.plugins[0].options,
    {
        // doesn't work with dev server :-|
        // https://github.com/esnvutbrno/fiesta-plus/issues/37
        integrity: true,
        integrityHashes: ['sha384'],
        // to NOT include full url from PUBLIC_PATH (because of SRI on subdomains)
        // TODO:for cache purpose would be better to tweak CORS to allow serving from topdomain on subdomains with SRI
        publicPath: '',
    }
)


module.exports = config;
