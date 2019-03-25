const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');

const frontEndStaticDir = path.resolve(__dirname, 'critiquebrainz/frontend/static');

module.exports = {
  entry: {
    'main': path.resolve(frontEndStaticDir, 'scripts/main.js'),
    'common': path.resolve(frontEndStaticDir, 'scripts/common.js'),
    'leaflet': path.resolve(frontEndStaticDir, 'scripts/leaflet.js'),
    'rating': path.resolve(frontEndStaticDir, 'scripts/rating.js'),
    'spotify': path.resolve(frontEndStaticDir, 'scripts/spotify.js'),
    'wysiwyg-editor': path.resolve(frontEndStaticDir, 'scripts/wysiwyg-editor.js'),
  },
  output: {
    path: path.resolve(__dirname, 'critiquebrainz/frontend/static/build/'),
    filename: '[name].[contenthash].js',
  },
  module: {
    rules: [
    {
      test: /\.(js)$/,
      exclude: /node_modules/,
      use: [
        {
          loader: 'babel-loader'
        }
      ]
    },
    {
      test: /\.less$/,
      use: [
        {
          loader: "style-loader"
        },
        {
          loader: MiniCssExtractPlugin.loader
        }, 
        {
          loader: "css-loader",
          options: {
            url: false 
          }
        },
        {
          loader: "less-loader",
          options: {
            relativeUrls: false
          }
        }
      ]
    }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
      chunkFilename: '[name].[contenthash].css'
    }),
    new CleanWebpackPlugin(),
    new ManifestPlugin()
  ]
};
