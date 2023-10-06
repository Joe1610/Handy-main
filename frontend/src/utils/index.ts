// you need to install tensorflowjs
// pip install tensorflowjs
//this is use to convert keras model.h5 to tensorflowjs model
// tensorflowjs_converter --input_format=keras model.h5 .

import * as Holistic from "@mediapipe/holistic";
import * as drawing from "@mediapipe/drawing_utils";
export interface Pose {
  faceLandmarks: PoseLandmark[];
  poseLandmarks: PoseLandmark[];
  rightHandLandmarks: PoseLandmark[];
  leftHandLandmarks: PoseLandmark[];
  image: HTMLCanvasElement;
}

export interface PoseLandmark {
  x: number;
  y: number;
  z: number;
  visibility?: number;
}

export const FRAMES_FOR_PREDICTION = 30;
const SERVER_URL = "http://141.145.193.132:4444";

export const labelMap = {
  "0": "more",
  "1": "any",
  "2": "worry",
  "3": "not know",
  "4": "meat",
  "5": "milk",
  "6": "dessert",
  "7": "forget",
  "8": "gone",
  "9": "visit",
  "10": "tiger",
  "11": "bake",
  "12": "jump",
  "13": "eight",
  "14": "hat",
  "15": "lunch",
  "16": "backpack",
  "17": "japan",
  "18": "measure",
  "19": "internet",
  "20": "doctor",
  "21": "lousy",
  "22": "hurt",
  "23": "two",
  "24": "student",
  "25": "think",
  "26": "fast",
  "27": "young",
  "28": "birthday",
  "29": "hamburger",
  "30": "you",
  "31": "stay",
  "32": "beard",
  "33": "today",
  "34": "niece",
  "35": "baseball",
  "36": "people",
  "37": "turtle",
  "38": "aunt",
  "39": "moon",
  "40": "first",
  "41": "paper",
  "42": "microwave",
  "43": "why",
  "44": "bacon",
  "45": "beer",
  "46": "thin",
  "47": "good",
  "48": "dry",
  "49": "face",
  "50": "pink",
  "51": "mad",
  "52": "far",
  "53": "china",
  "54": "monkey",
  "55": "we",
  "56": "chat",
  "57": "alone",
  "58": "before",
  "59": "corn",
  "60": "newspaper",
  "61": "learn",
  "62": "cool",
  "63": "blanket",
  "64": "wood",
  "65": "how_many",
  "66": "pig",
  "67": "girl",
  "68": "eat",
  "69": "nervous",
  "70": "strawberry",
  "71": "center",
  "72": "write",
  "73": "color",
  "74": "potato",
  "75": "hurry",
  "76": "vacation",
  "77": "hot",
  "78": "ball",
  "79": "weak",
  "80": "warm",
  "81": "africa",
  "82": "history",
  "83": "game",
  "84": "country",
  "85": "remember",
  "86": "husband",
  "87": "mother",
  "88": "appointment",
  "89": "dirty",
  "90": "hospital",
  "91": "grapes",
  "92": "friendly",
  "93": "cheap",
  "94": "favorite",
  "95": "party",
  "96": "sleep",
  "97": "hard",
  "98": "christmas",
  "99": "medicine",
  "100": "meet",
  "101": "business",
  "102": "gossip",
  "103": "deer",
  "104": "my",
  "105": "dress",
  "106": "bowling",
  "107": "money",
  "108": "win",
  "109": "give",
  "110": "bread",
  "111": "tea",
  "112": "go",
  "113": "pull",
  "114": "thanksgiving",
  "115": "man",
  "116": "restaurant",
  "117": "easy",
  "118": "uncle",
  "119": "cereal",
  "120": "dog",
  "121": "children",
  "122": "fine",
  "123": "dark",
  "124": "cook",
  "125": "run",
  "126": "right",
  "127": "sit",
  "128": "same",
  "129": "how",
  "130": "horse",
  "131": "television",
  "132": "stop",
  "133": "match",
  "134": "snake",
  "135": "sorry",
  "136": "police",
  "137": "leave",
  "138": "city",
  "139": "cup",
  "140": "orange",
  "141": "travel",
  "142": "knife",
  "143": "flower",
  "144": "your",
  "145": "headache",
  "146": "also",
  "147": "sick",
  "148": "pizza",
  "149": "thursday",
  "150": "peach",
  "151": "pencil",
  "152": "morning",
  "153": "salt",
  "154": "garage",
  "155": "new",
  "156": "ugly",
  "157": "greece",
  "158": "canada",
  "159": "save",
  "160": "store",
  "161": "since",
  "162": "soccer",
  "163": "basketball",
  "164": "clock",
  "165": "past",
  "166": "bicycle",
  "167": "blue",
  "168": "dollar",
  "169": "excited",
  "170": "bar",
  "171": "some",
  "172": "animal",
  "173": "boat",
  "174": "table",
  "175": "glass",
  "176": "english",
  "177": "son",
  "178": "wrong",
  "179": "copy",
  "180": "window",
  "181": "change",
  "182": "speech",
  "183": "their",
  "184": "four",
  "185": "language",
  "186": "thirsty",
  "187": "start",
  "188": "meeting",
  "189": "feel",
  "190": "gold",
  "191": "america",
  "192": "one",
  "193": "family",
  "194": "now",
  "195": "different",
  "196": "week",
  "197": "enjoy",
  "198": "hello",
  "199": "socks",
  "200": "ready",
  "201": "where",
  "202": "see",
  "203": "marry",
  "204": "tomato",
  "205": "cat",
  "206": "nineteen",
  "207": "fat",
  "208": "pay",
  "209": "decide",
  "210": "have",
  "211": "sometimes",
  "212": "soon",
  "213": "arrogant",
  "214": "butter",
  "215": "everyday",
  "216": "close",
  "217": "boyfriend",
  "218": "clothes",
  "219": "boy",
  "220": "banana",
  "221": "day",
  "222": "east",
  "223": "thank you",
  "224": "kitchen",
  "225": "many",
  "226": "cafeteria",
  "227": "white",
  "228": "humble",
  "229": "need",
  "230": "woman",
  "231": "half",
  "232": "drop",
  "233": "live",
  "234": "polite",
  "235": "mustache",
  "236": "yes",
  "237": "all",
  "238": "watch",
  "239": "father",
  "240": "never",
  "241": "star",
  "242": "near",
  "243": "read",
  "244": "spring",
  "245": "no",
  "246": "principal",
  "247": "time",
  "248": "sweet",
  "249": "bored",
  "250": "early",
  "251": "phone",
  "252": "glasses",
  "253": "later",
  "254": "france",
  "255": "cow",
  "256": "black",
  "257": "awkward",
  "258": "six",
  "259": "always",
  "260": "fish",
  "261": "weekend",
  "262": "europe",
  "263": "kiss",
  "264": "teach",
  "265": "turkey",
  "266": "key",
  "267": "brother",
  "268": "fruit",
  "269": "picture",
  "270": "vomit",
  "271": "grandmother",
  "272": "arrive",
  "273": "pepper",
  "274": "smart",
  "275": "what",
  "276": "nice",
  "277": "who",
  "278": "teacher",
  "279": "water",
  "280": "russia",
  "281": "book",
  "282": "dance",
  "283": "green",
  "284": "tuesday",
  "285": "mexico",
  "286": "basement",
  "287": "big",
  "288": "discuss",
  "289": "jacket",
  "290": "soda",
  "291": "computer",
  "292": "class",
  "293": "government",
  "294": "outside",
  "295": "with",
  "296": "bad",
  "297": "cookie",
  "298": "red",
  "299": "inform",
  "300": "beautiful",
  "301": "but",
  "302": "seven",
  "303": "lost",
  "304": "not",
  "305": "bathroom",
  "306": "soup",
  "307": "late",
  "308": "purple",
  "309": "down",
  "310": "home",
  "311": "shoes",
  "312": "movie",
  "313": "deaf",
  "314": "wife",
  "315": "expensive",
  "316": "show",
  "317": "candy",
  "318": "drink",
  "319": "list",
  "320": "know",
  "321": "can",
  "322": "office",
  "323": "vegetable",
  "324": "sandwich",
  "325": "music",
  "326": "strange",
  "327": "cheese",
  "328": "grass",
  "329": "three",
  "330": "library",
  "331": "last",
  "332": "divorce",
  "333": "ten",
  "334": "university",
  "335": "pants",
  "336": "chicken",
  "337": "rude",
  "338": "small",
  "339": "chocolate",
  "340": "slow",
  "341": "yellow",
  "342": "train",
  "343": "sunday",
  "344": "happen",
  "345": "hungry",
  "346": "most",
  "347": "silly",
  "348": "apple",
  "349": "germany",
  "350": "giraffe",
  "351": "mean",
  "352": "tell",
  "353": "graduate",
  "354": "noon",
  "355": "mirror",
  "356": "hearing",
  "357": "rain",
  "358": "old",
  "359": "paint",
  "360": "exercise",
  "361": "nothing",
  "362": "research",
  "363": "snow",
  "364": "study",
  "365": "rabbit",
  "366": "number",
  "367": "awful",
  "368": "secretary",
  "369": "pregnant",
  "370": "bird",
  "371": "laugh",
  "372": "cousin",
  "373": "parents",
  "374": "floor",
  "375": "cold",
  "376": "from",
  "377": "eighteen",
  "378": "friend",
  "379": "few",
  "380": "bye",
  "381": "science",
  "382": "explain",
  "383": "tennis",
  "384": "tree",
  "385": "elephant",
  "386": "afternoon",
  "387": "short",
  "388": "argue",
  "389": "cute",
  "390": "shirt",
  "391": "walk",
  "392": "tired",
  "393": "wednesday",
  "394": "night",
  "395": "answer",
  "396": "shower",
  "397": "take",
  "398": "die",
  "399": "happy",
  "400": "quiet",
  "401": "year",
  "402": "lion",
  "403": "sign",
  "404": "homework",
  "405": "interesting",
  "406": "coffee",
  "407": "afraid",
  "408": "lettuce",
  "409": "school",
  "410": "dentist",
  "411": "understand",
  "412": "girlfriend",
  "413": "buy",
  "414": "cry",
  "415": "college",
  "416": "here",
  "417": "accident",
  "418": "yesterday",
  "419": "house",
  "420": "want",
  "421": "chair",
  "422": "letter",
  "423": "saturday",
  "424": "mouth",
  "425": "like",
  "426": "light",
  "427": "bear",
  "428": "sister",
  "429": "daughter",
  "430": "when",
  "431": "bed",
  "432": "practice",
  "433": "busy",
  "434": "work",
  "435": "me",
  "436": "nephew",
  "437": "strong",
  "438": "grandfather",
  "439": "church",
  "440": "future",
  "441": "monday",
  "442": "popcorn",
  "443": "fail",
  "444": "hour",
  "445": "love",
  "446": "tomorrow",
  "447": "wow",
  "448": "toast",
  "449": "finish",
  "450": "cough",
  "451": "please",
  "452": "airplane",
  "453": "carrot",
  "454": "head",
  "455": "hard of hearing",
  "456": "month",
  "457": "better",
  "458": "brown",
  "459": "wait",
  "460": "talk",
  "461": "help",
  "462": "which",
  "463": "halloween",
  "464": "australia",
  "465": "hair",
  "466": "room",
  "467": "boss",
  "468": "bus",
  "469": "nurse",
  "470": "again",
  "471": "sixteen",
  "472": "sad",
  "473": "car",
  "474": "important",
  "475": "alarm",
  "476": "egg",
  "477": "salad",
  "478": "friday",
  "479": "in",
  "480": "asia",
  "481": "baby",
  "482": "freeze",
  "483": "onion",
  "484": "play",
  "485": "tall",
  "486": "funny",
  "487": "draw",
  "488": "full",
  "489": "door",
  "490": "india",
  "491": "football",
  "492": "lazy",
  "493": "make",
  "494": "name",
  "495": "summer",
  "496": "soap",
  "497": "lie",
  "498": "after",
  "499": "shop",
};

export const connect = (
  ctx: CanvasRenderingContext2D,
  connectors: Array<[Holistic.NormalizedLandmark, Holistic.NormalizedLandmark]>
): void => {
  const canvas = ctx.canvas;
  for (const connector of connectors) {
    const from = connector[0];
    const to = connector[1];
    if (from && to) {
      if (
        from.visibility &&
        to.visibility &&
        (from.visibility < 0.1 || to.visibility < 0.1)
      ) {
        continue;
      }
      ctx.beginPath();
      ctx.moveTo(from.x * canvas.width, from.y * canvas.height);
      ctx.lineTo(to.x * canvas.width, to.y * canvas.height);
      ctx.stroke();
    }
  }
};
const IGNORED_BODY_LANDMARKS = [
  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 16, 17, 18, 19, 20, 21, 22,
];

function drawBody(
  landmarks: PoseLandmark[],
  ctx: CanvasRenderingContext2D
): void {
  const filteredLandmarks = Array.from(landmarks);
  for (const l of IGNORED_BODY_LANDMARKS) {
    delete filteredLandmarks[l];
  }

  drawing.drawConnectors(ctx, filteredLandmarks, Holistic.POSE_CONNECTIONS, {
    color: "#CC0000",
  });
  drawing.drawLandmarks(ctx, filteredLandmarks, {
    color: "#CC0000",
    fillColor: "#FF0000",
  });
}
function drawNeck(
  landmarks: PoseLandmark[],
  ctx: CanvasRenderingContext2D,
  lineColor: string
) {
  // get the left and right shoulder landmarks
  const leftShoulder = landmarks[Holistic.POSE_LANDMARKS.LEFT_SHOULDER];
  const rightShoulder = landmarks[Holistic.POSE_LANDMARKS.RIGHT_SHOULDER];
  const nose = landmarks[Holistic.POSE_LANDMARKS.NOSE];
  //lower the nose by a percentage to react to the chin
  nose.y = nose.y + 0.1;

  // draw a vertical line between the two shoulders to the head
  ctx.beginPath();
  const x = (leftShoulder.x + rightShoulder.x) / 2;
  const y = (leftShoulder.y + rightShoulder.y) / 2;
  ctx.moveTo(x * ctx.canvas.width, y * ctx.canvas.height);
  ctx.lineTo(nose.x * ctx.canvas.width, nose.y * ctx.canvas.height);
  ctx.strokeStyle = lineColor;
  ctx.stroke();
}

function drawHand(
  landmarks: PoseLandmark[],
  ctx: CanvasRenderingContext2D,
  lineColor: string,
  dotColor: string,
  dotFillColor: string
): void {
  const fingerColors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF"];
  drawConnect([[landmarks[0], landmarks[9]]], ctx, fingerColors[2]); //middle finger
  drawConnect([[landmarks[0], landmarks[13]]], ctx, fingerColors[3]); //ring finger

  drawing.drawConnectors(ctx, landmarks, Holistic.HAND_CONNECTIONS, {
    color: (info) => {
      const ignore = [8, 12, 16];
      if (ignore.includes(info.index ?? 0)) return "transparent";
      return fingerColors[Math.floor((info.index ?? 0) / 4)];
    },
  });

  //   for (let i = 0; i < 5; i++) {
  //     const fingerLandmarks = landmarks.slice(i * 4 + 1, i * 4 + 5); // get landmarks for current finger
  //     drawing.drawLandmarks(ctx, fingerLandmarks, {
  //       color: fingerColors[i], // set color to color of current finger
  //       fillColor: dotFillColor,
  //       lineWidth: 2,
  //       radius: (landmark) => {
  //         return drawing.lerp(1, -0.15, 0.01, 10, 1);
  //       },
  //     });
  //   }
}

function drawFace(
  landmarks: PoseLandmark[],
  ctx: CanvasRenderingContext2D
): void {
  //   drawing.drawConnectors(ctx, landmarks, Holistic.FACEMESH_TESSELATION, {
  //     color: "#C0C0C070",
  //     lineWidth: 1,
  //   });
  drawing.drawConnectors(ctx, landmarks, Holistic.FACEMESH_RIGHT_EYE, {
    color: "#FF3030",
  });
  drawing.drawConnectors(ctx, landmarks, Holistic.FACEMESH_RIGHT_EYEBROW, {
    color: "#FF3030",
  });
  drawing.drawConnectors(ctx, landmarks, Holistic.FACEMESH_LEFT_EYE, {
    color: "#30FF30",
  });
  drawing.drawConnectors(ctx, landmarks, Holistic.FACEMESH_LEFT_EYEBROW, {
    color: "#30FF30",
  });
  drawing.drawConnectors(ctx, landmarks, Holistic.FACEMESH_FACE_OVAL, {
    color: "#E0E0E0",
  });
  drawing.drawConnectors(ctx, landmarks, Holistic.FACEMESH_LIPS, {
    color: "#E0E0E0",
  });
}

function drawConnect(
  connectors: PoseLandmark[][],
  ctx: CanvasRenderingContext2D,
  color = "#CC0000"
): void {
  for (const connector of connectors) {
    const from = connector[0];
    const to = connector[1];
    if (from && to) {
      if (
        from.visibility &&
        to.visibility &&
        (from.visibility < 0.1 || to.visibility < 0.1)
      ) {
        continue;
      }
      ctx.beginPath();
      ctx.moveTo(from.x * ctx.canvas.width, from.y * ctx.canvas.height);
      ctx.lineTo(to.x * ctx.canvas.width, to.y * ctx.canvas.height);
      ctx.strokeStyle = color;
      ctx.stroke();
    }
  }
}

function drawElbowHandsConnection(
  pose: Pose,
  ctx: CanvasRenderingContext2D
): void {
  ctx.lineWidth = 5;

  if (pose.rightHandLandmarks) {
    ctx.strokeStyle = "#CC0000";
    drawConnect(
      [
        [
          pose.poseLandmarks[Holistic.POSE_LANDMARKS.RIGHT_ELBOW],
          pose.rightHandLandmarks[0],
        ],
      ],
      ctx
    );
  }

  if (pose.leftHandLandmarks) {
    ctx.strokeStyle = "#FF0000";
    drawConnect(
      [
        [
          pose.poseLandmarks[Holistic.POSE_LANDMARKS.LEFT_ELBOW],
          pose.leftHandLandmarks[0],
        ],
      ],
      ctx
    );
  }
}

export function draw(
  ctx: CanvasRenderingContext2D,
  pose: Holistic.Results,
  drawImage = true
) {
  if (!ctx) return;
  ctx.save();
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  ctx.fillStyle = "black";
  ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  if (drawImage && pose.image) {
    ctx.drawImage(pose.image, 0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  if (pose.poseLandmarks) {
    drawBody(pose.poseLandmarks, ctx);
    drawElbowHandsConnection(pose as Pose, ctx);
    drawNeck(pose.poseLandmarks, ctx, "#CC0000");
  }

  if (pose.leftHandLandmarks) {
    drawHand(pose.leftHandLandmarks, ctx, "#CC0000", "#FF0000", "#CC0000");
  }

  if (pose.rightHandLandmarks) {
    drawHand(pose.rightHandLandmarks, ctx, "#CC0000", "#CC0000", "#FF0000");
  }

  if (pose.faceLandmarks) {
    drawFace(pose.faceLandmarks, ctx);
  }

  ctx.restore();
}

export const getActionFrames = async (word: string) => {
  //load json file from public folder in react app

  const json = await fetch(`${SERVER_URL}/keypoints/${word}.json`);
  const data = await json.json();
  return data;
};

export async function drawFramesAndCreateVideo(
  sentence: string[],
  speed: number,
  fps = 30
) {
  return new Promise<string>(async (resolve, reject) => {
    const canvas = document.createElement("canvas");
    //canvas aspect ratio is 16:9
    canvas.width = 1280;
    canvas.height = 720;
    //canvas background color
    canvas.style.backgroundColor = "red";
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Get the frames from getActionFrames function
    const promises = sentence.map((text) => getActionFrames(text));
    const frames = await Promise.all(promises);
    //merge frames
    const mergedFrames = frames.reduce((acc, cur) => {
      return acc.concat(cur);
    }, []);

    // Create a new MediaRecorder instance
    const stream = canvas.captureStream();
    const chunks: Blob[] = [];
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e) => {
      chunks.push(e.data);
    };
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: "video/mp4" });
      const videoURL = URL.createObjectURL(blob);
      resolve(videoURL);
    };

    // Start recording
    mediaRecorder.start();

    // Draw the frames
    for (let i = 0; i < mergedFrames.length; i++) {
      draw(ctx, mergedFrames[i], false);
      await new Promise((resolve) => setTimeout(resolve, 1000 / fps / speed));
    }

    // Stop recording
    mediaRecorder.stop();
  });
}
