const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const path = require('path');

const publicPath = process.env.PUBLIC_PATH;
const buildDir = process.env.BUILD_DIR;

if (!publicPath) throw Error('Missing PUBLIC_PATH in env.');
if (!buildDir) throw Error('Missing BUILD_DIR in env.');

console.log(`BUILD_DIR=${buildDir}`)
console.log(`PUBLIC_PATH=${publicPath}`)

module.exports = {
    mode: 'production',
    entry: {
        main: [
            path.join(__dirname, './src/main.js')
        ],
    },
    output: {
        publicPath,
        path: buildDir,
        filename: '[name].[chunkhash:8].js',
    },
    module: {
        rules: [
            {
                test: /\.(svg|gif|jpg|png|woff|woff2|eot|ttf)$/,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            name: 'assets/[name]-[hash:6].[ext]',
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
                    {
                        loader: 'postcss-loader',
                        options: {
                            sourceMap: true,
                        },
                    },
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
            filename: '[name].[chunkhash:8].css',
            chunkFilename: '[id].[chunkhash:8].css',
        }),
        // new MomentLocalesPlugin({
        //     localesToKeep: ['en', 'cs'],
        // }),
    ],
};
