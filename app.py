from flask import Flask, request, jsonify
# [삭제됨] SQLAlchemy 관련 임포트 삭제
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# [삭제됨] DB 설정 및 모델 클래스(StudentHealth) 삭제

# [신규] 데이터를 저장할 임시 저장소 (리스트)
health_records = []

@app.route('/')  # 여기가 바로 '앤드포인트 /'를 정의하는 부분입니다.
def home():      # 함수 이름은 home, index 등 아무거나 상관없습니다.
    return "서버가 정상 작동 중입니다!"  # 여기에 출력하고 싶은 텍스트를 넣으면 됩니다.

# API: 데이터 저장
@app.route('/api/health', methods=['POST'])
def add_health_record():
    try:
        data = request.get_json()
        
        # 유효성 검사 (성별)
        if data.get('gender') not in ['남성', '여성']:
            return jsonify({'error': '성별은 "남성" 또는 "여성"이어야 합니다.'}), 400
        
        # 유효성 검사 (날짜 형식 확인만 하고, 저장은 문자열 그대로 하거나 변환)
        try:
            # 날짜 형식이 맞는지 확인하는 용도
            datetime.strptime(data['record_date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': '날짜 형식 오류'}), 400

        # [변경] DB 객체 대신 일반 딕셔너리(Dictionary) 생성
        new_record = {
            'id': len(health_records) + 1,  # ID는 현재 개수 + 1로 간단히 생성
            'school': data['school'],
            'record_date': data['record_date'], # 문자열 그대로 저장
            'age': data['age'],
            'height': data['height'],
            'weight': data['weight'],
            'gender': data['gender'],
            'breakfast': data['breakfast']
        }

        # [변경] 리스트에 추가 (DB commit 불필요)
        health_records.append(new_record)
        
        return jsonify({'message': '저장 성공', 'data': new_record}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: 조회
@app.route('/api/health', methods=['GET'])
def get_health_records():
    # [변경] 리스트 전체를 반환
    return jsonify(health_records), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)