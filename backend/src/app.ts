import express from "express";
const zlib = require("zlib");
const compression = require("compression");
const cors = require("cors");
const path = require("path");
const app = express();
const port = 4444;
app.use(cors());
app.use(
  compression({
    level: 9, // Maximum compression level
    strategy: zlib.constants.Z_FILTERED, // Compression strategy
  })
);

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.listen(port, () => {
  return console.log(`Express is listening at http://localhost:${port}`);
});

const videosFolderPath = path.join(__dirname, "videos");
const keypointsFolderPath = path.join(__dirname, "keypoints");

app.use("/videos", express.static(videosFolderPath));
app.use("/keypoints", express.static(keypointsFolderPath));
