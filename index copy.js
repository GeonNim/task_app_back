const express = require("express");
const { spawn } = require("child_process");
const path = require("path");

console.log(path.join(__dirname));

const app = express();
const PORT = 8000;

// 최신 Express는 body-parser 내장
app.use(express.json());

app.post('/chat', (req, res) => {
  
    const sendQuestion = req.body.question;

    // Python 경로 및 스크립트 경로 설정
    const execPython = path.join(__dirname, "chat", "bizchat.py");
    const pythonPath = path.join(__dirname, "chat", "Scripts", "python.exe");
    
    const net = spawn(pythonPath, [execPython, sendQuestion]);

    let output = "";  // 변경 가능한 변수로 선언

    // Python 스크립트로부터 데이터를 수신
    net.stdout.on('data', function (data) {
        console.log(`Python output: ${data}`);
        output += data.toString();  // 출력 결과 누적
    });

    // Python 스크립트 종료 시 응답 처리
    net.on('close', function (code) {
        if (code === 0) {
            console.log(`Python script finished with code ${code}`);
            res.status(200).json({ answer: output });  // 누적된 결과를 반환
        } else {
            res.status(500).send('Something went wrong');
        }
    });

    // 에러 처리
    net.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        res.status(500).send(`Error occurred: ${data}`);
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on PORT ${PORT}`);
});


// app.post('/chat', (req, res) => {
//   try {
//     // console.log(req.body);
//     // Extract the question from the request body (assuming it's sent as JSON)
//     const sendedQuestion = req.body.question;
//     // console.log(sendedQuestion);


//     // EC2 서버에서 현재 실행 중인 Node.js 파일의 절대 경로를 기준으로 설정합니다.
//     const scriptPath = path.join(__dirname, 'bizchat.py');
//     const pythonPath = path.join(__dirname, 'venv', 'bin', 'python3');


//     // Spawn the Python process with the correct argument
//     const result = spawn(pythonPath, [scriptPath, sendedQuestion]);


//     // result.stdout.on('data', (data) => {
//     //   console.log(data.toString());
//     //   // return res.status(200).json(data.toString());
//     // });


//     let responseData = '';


//     // Listen for data from the Python script
//     result.stdout.on('data', (data) => {
//       // console.log(data.toString());
//       // res.status(200).json({ answer: data.toString() });
//       responseData += data.toString();
//     });


//     // Listen for errors from the Python script
//     result.stderr.on('data', (data) => {
//       console.error(`stderr: ${data}`);
   
//    res.status(500).json({ error: data.toString() });
//     });


//     // Handle the close event of the child process
//     result.on('close', (code) => {
//       if (code === 0) {
//         res.status(200).json({ answer: responseData });
//       } else {
//         res
//           .status(500)
//           .json({ error: `Child process exited with code ${code}` });
//       }
//     });
//   } catch (error) {
//     return res.status(500).json({ error: error.message });
//   }
// });
