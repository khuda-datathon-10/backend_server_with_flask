from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS  # [중요] Lovable과 통신하기 위해 추가

app = Flask(__name__)

# [중요] 모든 곳(Lovable 포함)에서 이 서버로 접속을 허용함
CORS(app) 

# --- [이 부분을 추가하세요] ---
@app.route('/')
def home():
    return "서버가 정상적으로 실행 중입니다. 데이터는 /api/health 에서 확인하세요."
# ---------------------------

# 데이터베이스 설정 (내 컴퓨터에 students.db 파일로 저장)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 모델 정의
class StudentHealth(db.Model):
    __tablename__ = 'student_health'
    id = db.Column(db.Integer, primary_key=True)
    school = db.Column(db.String(100), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    breakfast = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'school': self.school,
            'record_date': self.record_date.strftime('%Y-%m-%d %H:%M:%S'),
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'gender': self.gender,
            'breakfast': self.breakfast
        }

with app.app_context():
    db.create_all()

# API: 데이터 저장
@app.route('/api/health', methods=['POST'])
def add_health_record():
    try:
        data = request.get_json()
        if data.get('gender') not in ['남성', '여성']:
            return jsonify({'error': '성별은 "남성" 또는 "여성"이어야 합니다.'}), 400
        
        try:
            date_obj = datetime.strptime(data['record_date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': '날짜 형식 오류'}), 400

        new_record = StudentHealth(
            school=data['school'],
            record_date=date_obj,
            age=data['age'],
            height=data['height'],
            weight=data['weight'],
            gender=data['gender'],
            breakfast=data['breakfast']
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'message': '저장 성공', 'data': new_record.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 조회
@app.route('/api/health', methods=['GET'])
def get_health_records():
    records = StudentHealth.query.all()
    return jsonify([r.to_dict() for r in records]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)