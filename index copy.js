const express = require('express'); // express 모듈 불러오기
const cors = require('cors'); // cors 모듈 불러오기
const { spawn } = require('child_process');
const path = require('path');

const PORT = 8080;
const app = express(); // express 모듈을 사용하기 위해 app 변수에 할당

app.use(cors()); // HTTP, HTTPS 프로토콜을 사용하는 서버 간의 통신을 허용
app.use(express.json()); // express 모듈의 json() 메소드를 사용 (json으로 파싱)

// 기본 라우트: "Hello World!" 응답
app.get('/', (req, res) => {
  res.send('Hello World! completed wow');
});

// /chat POST 요청 처리
app.post('/chat', (req, res) => {
  try {
    const sendQuestion = req.body.question; // 요청으로 받은 question 데이터

    // Python 스크립트 경로와 Python 실행 경로 설정
    const scriptPath = path.join(__dirname, 'chat', 'bizchat.py'); // 실행할 Python 스크립트 경로
    const pythonPath = path.join(__dirname, 'chat', 'Scripts', 'python.exe'); // Python 실행 경로 (Windows 환경)

    // Python 스크립트를 실행하며, 사용자가 보낸 질문을 인자로 전달
    const pythonProcess = spawn(pythonPath, [scriptPath, sendQuestion]);

    let output = ''; // Python 스크립트의 출력을 저장할 변수

    // Python 스크립트에서 stdout으로 데이터를 받을 때마다 실행
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString(); // Python 출력 데이터를 누적
    });

    // Python 스크립트가 종료될 때 처리
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        res.status(200).json({ answer: output }); // 성공 시 누적된 출력을 반환
      } else {
        res.status(500).json({ error: `Python script exited with code ${code}` }); // 에러 시 코드 반환
      }
    });

    // Python 스크립트에서 에러 발생 시 처리
    pythonProcess.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
      res.status(500).json({ error: data.toString() }); // 에러 발생 시 클라이언트에 에러 반환
    });
  } catch (error) {
    res.status(500).json({ error: error.message }); // 예외 처리
  }
});

// 추가 라우터 파일 연결 (CRUD 작업 등을 위한 라우터)
app.use(require('./routes/getRoutes'));
app.use(require('./routes/postRoutes'));
app.use(require('./routes/deleteRoutes'));
app.use(require('./routes/updateRoutes'));

// 서버 시작
app.listen(PORT, () => {
  console.log(`Server is running on PORT ${PORT}`);
});

