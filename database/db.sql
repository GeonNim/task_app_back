-- 테이블 생성

CREATE TABLE task (
    _id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    isCompleted BOOLEAN NOT NULL DEFAULT false,
    isImportant BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    userId TEXT NOT NULL
);

-- 데이터 추가
INSERT INTO task (_id, title, description, date, isCompleted,isImportant,created_at,updated_at,userId) 
VALUES('1234','할일1','할일1 설명','2021-08-01',false,false,'geonnim');


-- 데이터 조회
SELECT * FROM task were USERiD = 'geonNim  ' ORDER BY created_at DESC --(ASC)

-- 특정 사용자 데이터 필터 조회
SELECT * FROM task WHERE userId = 'geon'


-- 데이터 초기화 문제가 생기면 초기화하자.
DROP TABLE TEST_DB 

-- 데이터 삭제
DELETE FROM task WHERE _id = '1234'

UPDATE	task SET iscompleted = false WHERE _id = '6bb49cf9-6ab1-4653-9095-b8fb462f90eb'





-- 나는 rds 파라미터그룹에서 timezone을 설정했기에 아래는 pgadmin에서 실행하지 않음 다만 설명과 같은 차이점은 존재

ALTER DATABASE postgres SET timezone = 'Asia/Seoul';
-- ALTER DATABASE 설명
-- 적용 범위: 특정 데이터베이스에 대해 timezone 설정을 적용합니다. 이 설정은 해당 데이터베이스에 연결된 세션에서만 적용됩니다.
-- 영향: 데이터베이스 postgres의 모든 새로운 세션에 대해 기본 timezone이 'Asia/Seoul'로 설정됩니다. 그러나 다른 데이터베이스에는 영향을 미치지 않습니다.
-- 지속성: ALTER DATABASE 명령어로 설정된 timezone은 데이터베이스와 함께 저장되며, 데이터베이스가 재시작되더라도 이 설정이 유지됩니다.

-- 즉 postgres라는 DB에서만 timezon을 설정을 적용함 postgres의 모든 세션에 영향을 주며 DB와 저장되 재시작되도 초기화 안됨




-- 트리거 함수 생성: updated_at 필드를 현재 시간으로 설정
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- 트리거 생성: task 테이블에서 UPDATE가 발생할 때마다 update_updated_at_column 함수를 호출
CREATE TRIGGER update_task_updated_at
BEFORE UPDATE ON task
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- task 테이블의 created_at 필드는 행이 처음 삽입될 때만 설정.
-- updated_at 필드는 행이 업데이트될 때마다 트리거를 통해 현재 시간으로 자동 갱신.
-- BEFORE UPDATE 트리거는 레코드가 업데이트되기 직전에 updated_at 필드를 현재 시간으로 변경.
