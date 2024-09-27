const express = require('express'); //express 묘듈 불러오기
const cors = require('cors'); // cors 묘듈 불러오기

const PORT = '8080';

const app = express(); // express 묘듈을 사용하기 위해 app 변수에 할당한다.

// const corsOptions = {
//   origin: 'http://localhost:3000', // 허용할 주소
//   credentials: true, // 인증 정보 허용
// };

// const corsOption2 = ['http://localhost:3000', 'http://localhost:3001'];
// app.use(cors(corsOption2)); <= 위처럼 지정할경우 이렇게 넣어서 사용함

app.use(cors()); //http, https 프로토콜을 사용하는 서버 간의 통신을 허용한다. (100%는 아님)
app.use(express.json()); // express 묘듈의 json() 메소드를 사용. (express를 json으로 파싱)

// req,res로 줄여도 됨
app.get('/', (request, response) => {
  response.send('Hello World! completed wow');
});

app.post('/chat', (req, res) => {
  try {
    // console.log(req.body);
    // Extract the question from the request body (assuming it's sent as JSON)
    const sendedQuestion = req.body.question;
    // console.log(sendedQuestion);


    // EC2 서버에서 현재 실행 중인 Node.js 파일의 절대 경로를 기준으로 설정합니다.
    const scriptPath = path.join(__dirname, 'bizchat.py');
    const pythonPath = path.join(__dirname, 'venv', 'bin', 'python3');


    // Spawn the Python process with the correct argument
    const result = spawn(pythonPath, [scriptPath, sendedQuestion]);


    // result.stdout.on('data', (data) => {
    //   console.log(data.toString());
    //   // return res.status(200).json(data.toString());
    // });


    let responseData = '';


    // Listen for data from the Python script
    result.stdout.on('data', (data) => {
      // console.log(data.toString());
      // res.status(200).json({ answer: data.toString() });
      responseData += data.toString();
    });


    // Listen for errors from the Python script
    result.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
   
   res.status(500).json({ error: data.toString() });
    });


    // Handle the close event of the child process
    result.on('close', (code) => {
      if (code === 0) {
        res.status(200).json({ answer: responseData });
      } else {
        res
          .status(500)
          .json({ error: `Child process exited with code ${code}` });
      }
    });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
});


// app.get('/get_tasks', async (req, res) => {
//   try {
//     const result = await database.query('SELECT * FROM task');
//     return res.status(200).json(result.rows);
//   } catch (error) {
//     return res.status(500).json({ error: error.message });
//   }
// });
// getTasks와 getRoutes를 만들어 아래 app.use로 사용하기에 위는 안씀

app.use(require('./routes/getRoutes'));
app.use(require('./routes/postRoutes'));
app.use(require('./routes/deleteRoutes'));
app.use(require('./routes/updateRoutes'));

app.listen(PORT, () => console.log(`Server is running on ${PORT}`)); //서버 실행시 메시지
