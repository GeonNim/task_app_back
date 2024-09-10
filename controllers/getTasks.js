const database = require('../database/database'); //database 묘듈 불러오기

exports.getTasks = async (req, res) => {
  const userId = req.params.userId;
  try {
    const result = await database.query(
      'SELECT * FROM task WHERE userId = $1 ORDER BY created_at DESC',
      [userId] //인젝션 공격방지용으로 ``에 ${}로 직접넣지않고 위와 같이 사용
    );
    return res.status(200).json(result.rows);
  } catch (error) {
    // return res.status(500).json({ error: error.message });
    return res.status(500).json({ msg: 'Get Item Fail + ' + error });
  }
};
