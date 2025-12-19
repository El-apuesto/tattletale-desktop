const rules = require('./webpack.rules');
const plugins = require('./webpack.plugins');

module.exports = {
  module: {
    rules,
  },
  plugins,
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx', '.css'],
    fallback: {
      "fs": false,
      "path": false,
      "crypto": false,
    }
  },
  target: 'electron-renderer',
  mode: 'development',
};