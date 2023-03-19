const { AngularWebpackPlugin } = require("@ngtools/webpack");
const path = require("path");

module.exports = {
	entry: "./static/ts/index.ts",
	externals: {
		bootstrap: "bootstrap",
	},

	output: {
	filename: "index.js",
		path: path.resolve(__dirname, "static", "js"),
	},

	module: {
		rules: [
			{
				test: /\.[cm]?js$/,
				use: {
					loader: "babel-loader",
					options: {
						cacheDirectory: true,
						compact: true,
						plugins: ["@angular/compiler-cli/linker/babel"],
					},
				},
			},

			{
				test: /\.scss$/,
				type: "asset/source",
				loader: "sass-loader"
			},

			{
				test: /\.ts$/,
				loader: "@ngtools/webpack"
			}
		]
	},

	plugins: [
		new AngularWebpackPlugin({
			jitMode: false
		})
	],

	resolve: {
		extensions: [".js", ".ts"]
	}
};
