const path = require("path");

module.exports = {
	entry: "./static/ts/index.ts",
	output: {
	filename: "main.js",
		path: path.resolve(__dirname, "static", "js"),
	},
};
