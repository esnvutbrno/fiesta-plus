const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const path = require('path');
const publicPath = process.env.PUBLIC_PATH || 'https://webpack.localhost/';
const buildDir = process.env.BUILD_DIR;

if (!buildDir) throw Error('Missing BUILD_DIR in env.');

module.exports = {
    optimization: {
        splitChunks: {
            name: 'common',
            chunks: 'all',
        },
        runtimeChunk: {
            name: 'vendor',
        },
    },
    entry: {
        main: path.join(__dirname, './src/main.css'),
        // login: path.join(__dirname, './src/js/pages/Login/login.ts'),
    },
    output: {
        publicPath,
        path: buildDir,
        filename: '[name].[chunkhash:3].js',
    },
    module: {
        rules: [
            {
                test: /\.(svg|gif|jpg|png|woff|woff2|eot|ttf)$/,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            name: 'assets/[name]-[hash:12].[ext]',
                            limit: 10 * 1024, // inline smaller files in css (than 10kB)
                            esModule: false,
                        },
                    },
                ],
            },
            {
                test: /\.(jpg|png|gif|svg)$/,
                loader: 'image-webpack-loader',
                enforce: 'pre',
                options: {
                    bypassOnDebug: true,
                },
            },
            {
                test: /\.css$/i,
                include: path.resolve(__dirname, 'src'),
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'postcss-loader',
                ],
            },
        ],
    },
    resolve: {
        modules: [
            'node_modules/',
        ],
        unsafeCache: true,
    },
    plugins: [
        new BundleTracker({
            path: buildDir,
            // https://github.com/django-webpack/webpack-bundle-tracker/issues/108
            filename: path.join(buildDir, 'webpack-stats.json'),
        }),
        new MiniCssExtractPlugin({
            filename: '[name].[hash:8].css',
            chunkFilename: '[id].[hash:8].css',
        }),
        // new MomentLocalesPlugin({
        //     localesToKeep: ['en', 'cs'],
        // }),
    ],
};
