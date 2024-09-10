const { Pool } = require('pg'); //postgres 모듈 불러오기
require('dotenv').config(); //.env 파일ㅑ 사용 설정

const pool = new Pool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,

  // ssl: {
  //   rejectUnauthorized: false,
  // SSL 인증서 검증을 비활성화하여 서버 인증서가 신뢰할 수 없는 경우에도 연결을 허용합니다.},
});

module.exports = pool; //{} 로 감쌀 경우 pool 변수를 적어서 사용해야함
// ex) data => pool.data 이런식으로
// 변수가 하나라 {}로 감싸진 않았음
