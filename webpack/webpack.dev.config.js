const config = require('./webpack.base.config.js');
const webpack = require('webpack');

const PORT = process.env.HOST_PORT || 8003;

config.mode = 'development';

config.devtool = 'eval-source-map';

config.plugins.push(
    new webpack.DefinePlugin({
        '__SENTRY_DSN__': '""',
        '__DEVELOPMENT__': 'true',
    }),
);


// use sourcemaps for sass-loader and css-loader
config.module.rules.forEach(rule => {
    rule.use &&
    rule.use.forEach(use => {
        use.options &&
        'sourceMap' in use.options &&
        (use.options.sourceMap = true);
    });
});

config.devServer = {
    host: '0.0.0.0',
    port: PORT,
    allowedHosts: ['.localhost'],
    client: {
        webSocketURL: 'wss://webpack.local/ws',
    },
    hot: true,
    historyApiFallback: true,
    headers: {'Access-Control-Allow-Origin': '*'},
};

module.exports = config;
