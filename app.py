import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# ==========================================
# [중요] Lovable(Supabase) 데이터베이스 연결 설정
# ==========================================
# 1. Lovable/Supabase에서 복사한 Connection String을 아래에 입력하세요.
# 2. 'postgres://'로 시작한다면 'postgresql://'로 변경해 주는 것이 좋습니다.
# 3. 실제 배포 시에는 이 주소를 코드에 직접 적지 말고 환경변수(os.environ)를 사용하는 것이 보안상 안전합니다.

DB_USER = "postgres"
DB_PASSWORD = "여기에_비밀번호를_입력하세요"
DB_HOST = "db.xxxxxx.supabase.co" # Lovable/Supabase 호스트 주소
DB_PORT = "5432"
DB_NAME = "postgres"

# SQLAlchemy용 연결 문자열 조합
# 예시: postgresql://postgres:password@db.ref.supabase.co:5432/postgres
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 데이터베이스 모델 (테이블 정의) - 기존과 동일
# ==========================================
class StudentHealth(db.Model):
    __tablename__ = 'student_health'
    
    id = db.Column(db.Integer, primary_key=True)              
    school = db.Column(db.Text, nullable=False)               # 학교 (TEXT) - Postgres에서는 Text 권장
    record_date = db.Column(db.DateTime, nullable=False)      
    age = db.Column(db.Integer, nullable=False)               
    height = db.Column(db.Integer, nullable=False)            
    weight = db.Column(db.Integer, nullable=False)            
    gender = db.Column(db.String(2), nullable=False)          

    def to_dict(self):
        return {
            'id': self.id,
            'school': self.school,
            'record_date': self.record_date.strftime('%Y-%m-%d %H:%M:%S'),
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'gender': self.gender
        }

# ==========================================
# 서버 시작 시 테이블 생성
# ==========================================
with app.app_context():
    # 클라우드 DB에 테이블이 없으면 자동으로 생성합니다.
    db.create_all()
    print("Connected to Cloud Database successfully.")

# ==========================================
# API 구현 (POST) - 저장
# ==========================================
@app.route('/api/health', methods=['POST'])
def add_health_record():
    try:
        data = request.get_json()

        if data.get('gender') not in ['남성', '여성']:
            return jsonify({'error': '성별은 "남성" 또는 "여성"이어야 합니다.'}), 400

        try:
            date_obj = datetime.strptime(data['record_date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': '날짜 형식이 올바르지 않습니다. (YYYY-MM-DD HH:MM:SS)'}), 400

        new_record = StudentHealth(
            school=data['school'],
            record_date=date_obj,
            age=data['age'],
            height=data['height'],
            weight=data['weight'],
            gender=data['gender']
        )

        db.session.add(new_record)
        db.session.commit()

        return jsonify({
            'message': '클라우드 DB에 데이터가 저장되었습니다.',
            'data': new_record.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# API 구현 (GET) - 조회
# ==========================================
@app.route('/api/health', methods=['GET'])
def get_health_records():
    try:
        records = StudentHealth.query.all()
        return jsonify([record.to_dict() for record in records]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)