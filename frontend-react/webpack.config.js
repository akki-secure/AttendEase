const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = (env, argv) => {
  const isDev = argv.mode === 'development'

  return {
    entry: './src/main.jsx',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'bundle.[contenthash].js',
      publicPath: '/',
      clean: true,
    },
    resolve: {
      extensions: ['.js', '.jsx'],
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: 'babel-loader',
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
      ],
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: './public/index.html',
      }),
    ],
    devServer: {
      port: 5174,
      historyApiFallback: true,
      proxy: [
        {
          context: ['/api'],
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      ],
    },
    devtool: isDev ? 'eval-source-map' : false,
  }
}
