const express = require('express'); //express 묘듈 불러오기
const cors = require('cors'); // cors 묘듈 불러오기
const spawn = require('child_process').spawn;
const path = require('path');
const bodyParser = require('body-parser');


const PORT = '8080';

const app = express(); // express 묘듈을 사용하기 위해 app 변수에 할당한다.

app.use(cors()); //http, https 프로토콜을 사용하는 서버 간의 통신을 허용한다. (100%는 아님)
app.use(express.json()); // express 묘듈의 json() 메소드를 사용. (express를 json으로 파싱)

// req,res로 줄여도 됨
app.get('/', (request, response) => {
  response.send('Hello World! completed wow');
});

// console.log(path.join(__dirname));
app.use(bodyParser.json());


app.post("/chat", (req, res) => {
    const sendQuestion = req.body.question;
    // console.log(sendQuestion);

    //  mac
    // const pythonPath = path.join(__dirname, "chat", "bin", "python3");

    // windows
    const scriptPath = path.join(__dirname, "bizchat.py");
    const pythonPath = path.join(__dirname, "venv", "bin", "python3");


    const net = spawn(pythonPath,[scriptPath, sendQuestion ]);

    output = "";

     //파이썬 파일 수행 결과를 받아온다
     net.stdout.on('data', function (data) { 
        output += data.toString();   
    });

    net.on('close', (code) => {
        if(code === 0 ){
            res.status(200).json({ answer: output });
        } else {
            res.status(500).send("Something went Wrong");
        }
    });

    net.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
});

app.listen(port, () => {
    console.log("Server is running on port 8000");
});


app.use(require('./routes/getRoutes'));
app.use(require('./routes/postRoutes'));
app.use(require('./routes/deleteRoutes'));
app.use(require('./routes/updateRoutes'));

app.listen(PORT, () => console.log(`Server is running on ${PORT}`)); //서버 실행시 메시지
