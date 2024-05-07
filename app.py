from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

app = Flask(__name__)

# 配置 MySQL 連接信息
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '0000'
app.config['MYSQL_DB'] = 'testdb2'  # 資料庫名稱

# 初始化 MySQL
mysql = MySQL(app)

# 设置会话密钥
app.secret_key = 'your_secret_key'

# 登录页面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE UserId = %s", [userid])
        user = cursor.fetchone()    

        if user and check_password_hash(user[2], password):  # 假設 Password 存儲在 user[3]
            session['user_id'] = user[0]
            flash('登录成功', 'success')
            return redirect(url_for('user'))
        else:
            flash('登录失败，请检查用户名与密码', 'danger')
    return render_template('login.html')


# 用户页面
@app.route('/user', methods=['GET'])
def user():
    return render_template('user.html')


# 注册页面
# 注册页面
@app.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        username = request.form['username']
        app.config['MYSQL_PASSWORD'] = '0000'
        userid = request.form['userid']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE UserId = %s", [userid])
        existing_user = cursor.fetchone()

        if existing_user:
            flash('此帳號已註冊過請重新註冊', 'danger')
            return redirect(url_for('regist'))  # 重定向回注册页面
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (UserName, UserId, Password) VALUES (%s, %s, %s)", (username, userid, hashed_password))
            mysql.connection.commit()

            flash('註冊成功', 'success')
            return redirect(url_for('login'))
    return render_template('regist.html')


# 病患資料頁面
@app.route('/patient_data.html', methods=['GET'])
def patient_data():
    # 在此處提供病患資料頁面的相關處理
    return render_template('patient_data.html')

# 病患資料輸入及存儲
@app.route('/save_patient_data', methods=['POST'])
def save_patient_data():
    if request.method == 'POST':
        year = request.form['year']
        patient_id = request.form['patient_id']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        esrd = request.form['esrd']
        pre_op_ef_percentage = request.form['pre_op_ef_percentage']
        post_op_ef_percentage = request.form['post_op_ef_percentage']

        # 將性別轉換為布林值
        gender_boolean = True if gender == '男' else False

        # 將ESRD轉換為布林值
        esrd_boolean = True if esrd == '是' else False
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO medata (資料年度, 病歷號, 性別, 身高, 體重, ESRD, 術前EF_Percentage, 術後EF_Percentage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (year, patient_id, gender_boolean, height, weight, esrd_boolean, pre_op_ef_percentage, post_op_ef_percentage))
        mysql.connection.commit()
        cursor.close()

        flash('病患資料已成功儲存', 'success')
        return redirect(url_for('patient_data'))
    
@app.route('/get_data_from_database', methods=['GET'])
def get_data_from_database():
    column_name = request.args.get('columnName')
    cursor = mysql.connection.cursor()
    cursor.execute("SHOW COLUMNS FROM medata")
    columns = [column[0] for column in cursor.fetchall()]

    if column_name in columns:
        cursor.execute(f"SELECT {column_name} FROM medata")
        data = cursor.fetchall()
        values = [row[0] for row in data]
        return jsonify({'success': True, 'values': values})
    else:
        return jsonify({'success': False, 'message': '輸入的欄位名稱不存在或輸入有誤'})

    
@app.route('/graph.html', methods=['GET'])
def graph():
    # 在此處提供病患資料頁面的相關處理
    return render_template('graph.html')

# 用户页面
@app.route('/tree.html', methods=['GET'])
def tree():
    return render_template('tree.html') 

# 用户页面
@app.route('/treeplot.html', methods=['GET'])
def decision_tree():
    return render_template('treeplot.html')

 
if __name__ == '__main__':
    app.run(debug=True)
