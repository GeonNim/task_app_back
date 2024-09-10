const database = require('../database/database'); //database 묘듈 불러오기

exports.deleteTask = async (req, res) => {
  const itemId = req.params.itemId;

  try {
    const result = await database.query(
      'DELETE FROM task WHERE _id = $1',
      [itemId] //인젝션 공격방지용으로 ``에 ${}로 직접넣지않고 위와 같이 사용
    );
    return res.status(200).json({ message: 'Task Deleted Successfully' });
  } catch (error) {
    // return res.status(500).json({ error: error.message });
    return res.status(500).json({ message: 'Delete Item Fail + ' + error });
  }
};
