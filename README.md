# qlhethongtuyensinhdaihoc
from http.client import CREATED
import os
import shutil
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime

def create_file(filename, content):
    """Tạo file với nội dung cho trước"""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"✅ Đã tạo file: {filename}")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi tạo file {filename}: {e}")
        return False

def init_database():
    """Khởi tạo database với dữ liệu mẫu"""
    conn = sqlite3.connect('tuyensinh.db')
    c = conn.cursor()
    
    # Bảng người dùng
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                full_name TEXT
            )''')
    
    # Bảng thí sinh
    c.execute('''CREATE TABLE IF NOT EXISTS thisinh (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_thisinh TEXT UNIQUE,
                ho_ten TEXT NOT NULL,
                cmnd TEXT UNIQUE,
                ngay_sinh TEXT,
                gioi_tinh TEXT,
                dia_chi TEXT,
                sdt TEXT,
                email TEXT,
                trang_thai TEXT DEFAULT 'Chờ duyệt',
                created_at TEXT
            )''')
    
    # Bảng nguyện vọng
    c.execute('''CREATE TABLE IF NOT EXISTS nguyenvong (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thisinh_id INTEGER,
                ma_nganh TEXT,
                ten_nganh TEXT,
                khoi_thi TEXT,
                diem_thi REAL,
                trang_thai TEXT,
                FOREIGN KEY (thisinh_id) REFERENCES thisinh (id)
            )''')
    
    # Bảng thanh toán
    c.execute('''CREATE TABLE IF NOT EXISTS thanhtoan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thisinh_id INTEGER,
                so_tien REAL,
                ngay_thanh_toan TEXT,
                hinh_thuc TEXT,
                trang_thai TEXT DEFAULT 'Chưa thanh toán',
                FOREIGN KEY (thisinh_id) REFERENCES thisinh (id)
            )''')
    
    # Bảng kỳ thi
    c.execute('''CREATE TABLE IF NOT EXISTS kythi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_ky_thi TEXT,
                ngay_bat_dau TEXT,
                ngay_ket_thuc TEXT,
                trang_thai TEXT
            )''')
    
    # Bảng ngành học
    c.execute('''CREATE TABLE IF NOT EXISTS nganh_hoc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_nganh TEXT UNIQUE,
                ten_nganh TEXT,
                chi_tieu INTEGER,
                diem_chuan REAL
            )''')
    
    # Thêm dữ liệu mẫu
    # Người dùng mẫu
    try:
        c.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",  
                  ('admin', 'admin123', 'admin', 'Quản trị viên'))
        c.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",  
                  ('tuyensinh', 'ts123', 'staff', 'Nhân viên tuyển sinh'))
    except Exception as e:
        print(f"Lỗi khi thêm người dùng mẫu: {e}")
        pass

    # Ngành học mẫu
    nganh_hoc_data = [
        ('CNTT', 'Công nghệ Thông tin', 100, 24.5),
        ('KT', 'Kế Toán', 80, 23.0),
        ('QTKD', 'Quản trị Kinh doanh', 120, 22.0),
        ('NM', 'Ngôn ngữ Anh', 60, 21.5),
        ('XD', 'Xây dựng', 70, 20.0)
    ]

    for nganh in nganh_hoc_data:
        try:
            c.execute("INSERT OR IGNORE INTO nganh_hoc (ma_nganh, ten_nganh, chi_tieu, diem_chuan) VALUES (?, ?, ?, ?)", nganh)
        except Exception as e:
            print(f"Lỗi khi thêm ngành học: {e}")
            pass

    # Kỳ thi mẫu
    try:
        c.execute("INSERT OR IGNORE INTO kythi (ten_ky_thi, ngay_bat_dau, ngay_ket_thuc, trang_thai) VALUES (?, ?, ?, ?)",  
                  ('Kỳ thi tuyển sinh 2024', '2024-06-01', '2024-08-31', 'Đang mở'))
    except Exception as e:
        print(f"Lỗi khi thêm kỳ thi: {e}")
        pass
    
    conn.commit()  
    conn.close()   
    print("■ Đã khởi tạo database với dữ liệu mẫu")

def create_complete_system():
    """Tạo hệ thống hoàn chỉnh"""
    
    # Tạo thư mục
    project_dir = 'he_thong_tuyensinh_hoan_chinh'
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    
    os.makedirs(project_dir)
    os.chdir(project_dir)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    
    print("🚀 Đang tạo hệ thống tuyển sinh hoàn chỉnh...")

    # ========== FILE APP.PY HOÀN CHỈNH ==========
    app_content = '''from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tuyensinh_secret_key_2024'

# Hàm kết nối database
def get_db_connection():
    conn = sqlite3.connect('tuyensinh.db')
    conn.row_factory = sqlite3.Row
    return conn

# ========== ROUTES CHÍNH ==========

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            return redirect('/')
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ========== QUẢN LÝ THÍ SINH ==========

@app.route('/quanly_thisinh')
def quanly_thisinh():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('quanly_thisinh.html')

@app.route('/api/thisinh', methods=['GET', 'POST'])
def api_thisinh():
    conn = get_db_connection()

    if request.method == 'POST':
        data = request.json
        ma_thisinh = f"TS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            sql = """
            INSERT INTO thisinh 
            (ma_thisinh, ho_ten, cmnd, ngay_sinh, gioi_tinh, dia_chi, sdt, email, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                ma_thisinh, 
                data['ho_ten'], 
                data['cmnd'], 
                data['ngay_sinh'], 
                data['gioi_tinh'], 
                data['dia_chi'], 
                data['sdt'], 
                data['email'], 
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            conn.execute(sql, params)
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'ma_thisinh': ma_thisinh, 'message': 'Đăng ký thành công'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})
    
    # GET: Lấy danh sách thí sinh
    search = request.args.get('search', '')
    if search:
        sql = """
        SELECT * FROM thisinh
        WHERE ho_ten LIKE ? OR cmnd LIKE ? OR ma_thisinh LIKE ?
        ORDER BY id DESC
        """
        params = (f'%{search}%', f'%{search}%', f'%{search}%')
        thisinh = conn.execute(sql, params).fetchall()
    else:
        sql = "SELECT * FROM thisinh ORDER BY id DESC"
        thisinh = conn.execute(sql).fetchall()

    result = [dict(row) for row in thisinh]
    conn.close()
    return jsonify({'success': True, 'data': result})

@app.route('/api/thisinh/<int:thisinh_id>', methods=['PUT', 'DELETE'])
def api_thisinh_detail(thisinh_id):
    conn = get_db_connection()

    if request.method == 'PUT':
        data = request.json
        try:
            sql = """
            UPDATE thisinh 
            SET ho_ten=?, cmnd=?, ngay_sinh=?, gioi_tinh=?,
                dia_chi=?, sdt=?, email=?, trang_thai=? 
            WHERE id=?
            """
            params = (
                data['ho_ten'], 
                data['cmnd'], 
                data['ngay_sinh'], 
                data['gioi_tinh'],
                data['dia_chi'], 
                data['sdt'], 
                data['email'], 
                data['trang_thai'], 
                thisinh_id
            )
            conn.execute(sql, params)
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Cập nhật thành công!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})
    
    elif request.method == 'DELETE':
        try:
            conn.execute('DELETE FROM thisinh WHERE id=?', (thisinh_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Xóa thành công!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})

# ========== NGUYỆN VỌNG ==========

@app.route('/api/nguyenvong', methods=['GET', 'POST'])
def api_nguyenvong():
    conn = get_db_connection()

    if request.method == 'POST':
        data = request.json
        try:
            sql = """
            INSERT INTO nguyenvong
            (thisinh_id, ma_nganh, ten_nganh, khoi_thi, diem_thi, trang_thai)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                data['thisinh_id'], 
                data['ma_nganh'], 
                data['ten_nganh'],
                data['khoi_thi'], 
                data['diem_thi'], 
                'Chờ xét duyệt'
            )
            conn.execute(sql, params)
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Đăng ký nguyện vọng thành công!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})
    
    # GET: Lấy nguyện vọng theo thí sinh
    thisinh_id = request.args.get('thisinh_id')
    if thisinh_id:
        nguyenvong = conn.execute('SELECT * FROM nguyenvong WHERE thisinh_id=?', (thisinh_id,)).fetchall()
        result = [dict(row) for row in nguyenvong]
        conn.close()
        return jsonify({'success': True, 'data': result})
    
    conn.close()
    return jsonify({'success': False, 'message': 'Thiếu tham số'})

# ========== THANH TOÁN ==========

@app.route('/api/thanhtoan', methods=['POST'])
def api_thanhtoan():
    data = request.json
    conn = get_db_connection()

    try:
        sql = """
        INSERT INTO thanhtoan
        (thisinh_id, so_tien, ngay_thanh_toan, hinh_thuc, trang_thai)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            data['thisinh_id'], 
            200000, 
            datetime.now().strftime('%Y-%m-%d'),
            data['hinh_thuc'], 
            'Đã thanh toán'
        )
        conn.execute(sql, params)
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Thanh toán thành công!'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})

# ========== TRA CỨU ==========

@app.route('/tracuu')
def tracuu():
    return render_template('tracuu.html')

@app.route('/api/tracuu/<cmnd>')
def api_tracuu(cmnd):
    conn = get_db_connection()
    
    thisinh = conn.execute('SELECT * FROM thisinh WHERE cmnd=?', (cmnd,)).fetchone()
    if not thisinh:
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy thí sinh'})
    
    nguyenvong = conn.execute('SELECT * FROM nguyenvong WHERE thisinh_id=?', (thisinh['id'],)).fetchall()
    thanhtoan = conn.execute('SELECT * FROM thanhtoan WHERE thisinh_id=?', (thisinh['id'],)).fetchone()
    
    result = {
        'success': True,
        'thisinh': dict(thisinh),
        'nguyenvong': [dict(row) for row in nguyenvong],
        'thanhtoan': dict(thanhtoan) if thanhtoan else None
    }
    conn.close()
    return jsonify(result)

# ========== BÁO CÁO THỐNG KÊ ==========

@app.route('/baocao')
def baocao():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('baocao.html')

@app.route('/api/thongke')
def api_thongke():
    conn = get_db_connection()
    
    try:
        # Thống kê tổng quan
        tong_thisinh = conn.execute('SELECT COUNT(*) FROM thisinh').fetchone()[0]
        tong_da_duyet = conn.execute('SELECT COUNT(*) FROM thisinh WHERE trang_thai="Đã duyệt"').fetchone()[0]
        tong_chua_duyet = conn.execute('SELECT COUNT(*) FROM thisinh WHERE trang_thai="Chờ duyệt"').fetchone()[0]
        tong_da_thanhtoan = conn.execute('SELECT COUNT(DISTINCT thisinh_id) FROM thanhtoan WHERE trang_thai="Đã thanh toán"').fetchone()[0]
        
        # Thống kê theo trạng thái
        thongke_trangthai_rows = conn.execute('SELECT trang_thai, COUNT(*) FROM thisinh GROUP BY trang_thai').fetchall()
        thongke_trangthai = {row[0]: row[1] for row in thongke_trangthai_rows}
        
        # Thống kê theo ngành
        sql = """
        SELECT n.ten_nganh, COUNT(nv.id) as so_nguyenvong
        FROM nguyenvong nv
        JOIN nganh_hoc n ON nv.ma_nganh = n.ma_nganh
        GROUP BY n.ten_nganh
        """
        thongke_nganh = conn.execute(sql).fetchall()
        
        conn.close()
        return jsonify({
            'success': True,
            'tong_thisinh': tong_thisinh,
            'tong_da_duyet': tong_da_duyet,
            'tong_chua_duyet': tong_chua_duyet,
            'tong_da_thanhtoan': tong_da_thanhtoan,
            'thongke_trangthai': thongke_trangthai,
            'thongke_nganh': [{'ten_nganh': row[0], 'so_nguyenvong': row[1]} for row in thongke_nganh]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})

# ========== QUẢN LÝ NGÀNH HỌC ==========

@app.route('/quanly_nganh')
def quanly_nganh():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('quanly_nganh.html')

@app.route('/api/nganh_hoc', methods=['GET', 'POST'])
def api_nganh_hoc():
    conn = get_db_connection()

    if request.method == 'POST':
        data = request.json
        try:
            sql = """
            INSERT INTO nganh_hoc (ma_nganh, ten_nganh, chi_tieu, diem_chuan)
            VALUES (?, ?, ?, ?)
            """
            params = (
                data['ma_nganh'],
                data['ten_nganh'], 
                data['chi_tieu'], 
                data['diem_chuan']
            )
            conn.execute(sql, params)
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Thêm ngành học thành công!'})
        except Exception as e:
            conn.close()
            return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})

    # GET: Lấy danh sách ngành học
    try:
        sql = "SELECT * FROM nganh_hoc"
        nganh_hoc = conn.execute(sql).fetchall()
        result = [dict(row) for row in nganh_hoc]
        conn.close()
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'})

if __name__ == '__main__':
    print("🚀 Hệ thống tuyển sinh hoàn chỉnh đã khởi động!")
    print("📡 Truy cập: http://localhost:5000")
    print("🔑 Đăng nhập: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

    # ========== CÁC FILE TEMPLATE ==========

    # 1. Login page
    login_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đăng nhập - Hệ thống Tuyển sinh</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #2c3e50; margin-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #555; font-weight: 500; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        .btn { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .alert { padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
        .error { background: #ffeaa7; color: #d63031; }
        .demo-accounts { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🎓 Hệ thống Tuyển sinh</h1>
            <p>Đăng nhập để tiếp tục</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="form-group">
                <label>Tên đăng nhập:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Mật khẩu:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Đăng nhập</button>
        </form>
        
        <div class="demo-accounts">
            <strong>Tài khoản demo:</strong><br>
            👨‍💼 Admin: admin / admin123<br>
            👩‍💼 Nhân viên: tuyensinh / ts123
        </div>
    </div>
</body>
</html>'''

    # 2. Dashboard
    dashboard_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Hệ thống Tuyển sinh</title>
    <style>
        :root { --primary: #2c3e50; --secondary: #3498db; --success: #27ae60; --warning: #f39c12; --danger: #e74c3c; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; }
        .sidebar { background: var(--primary); color: white; width: 250px; height: 100vh; position: fixed; padding: 20px; }
        .main-content { margin-left: 250px; padding: 20px; }
        .logo { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #34495e; }
        .nav-item { padding: 12px 15px; margin: 5px 0; border-radius: 5px; cursor: pointer; transition: background 0.3s; }
        .nav-item:hover { background: #34495e; }
        .nav-item.active { background: var(--secondary); }
        .nav-item i { margin-right: 10px; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .stat-card h3 { color: #7f8c8d; margin-bottom: 10px; }
        .stat-number { font-size: 2em; font-weight: bold; }
        .bg-primary { background: var(--primary)!important; color: white; }
        .bg-success { background: var(--success)!important; color: white; }
        .bg-warning { background: var(--warning)!important; color: white; }
        .bg-danger { background: var(--danger)!important; color: white; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <h2>🎓 Tuyển Sinh</h2>
            <small>Hệ thống Quản lý</small>
        </div>
        <div class="nav-menu">
            <div class="nav-item active" onclick="loadPage('')"><i>📊</i> Dashboard</div>
            <div class="nav-item" onclick="loadPage('quanly_thisinh')"><i>👥</i> Quản lý Thí sinh</div>
            <div class="nav-item" onclick="loadPage('quanly_nganh')"><i>📚</i> Ngành học</div>
            <div class="nav-item" onclick="loadPage('tracuu')"><i>🔍</i> Tra cứu</div>
            <div class="nav-item" onclick="loadPage('baocao')"><i>📈</i> Báo cáo</div>
            <div class="nav-item" onclick="logout()"><i>🚪</i> Đăng xuất</div>
        </div>
    </div>

    <div class="main-content">
        <div class="header">
            <h1>Chào mừng, <span id="userName">{{ session.full_name }}</span>!</h1>
            <div>Vai trò: <strong>{{ session.role }}</strong></div>
        </div>

        <div id="pageContent">
            <div class="stats" id="dashboardStats">
                <!-- Stats will be loaded by JavaScript -->
            </div>
            
            <div class="quick-actions">
                <h2>Thao tác nhanh</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px;">
                    <button class="stat-card" onclick="loadPage('quanly_thisinh')" style="cursor: pointer;">
                        <h3>👥 Thêm thí sinh</h3>
                    </button>
                    <button class="stat-card" onclick="loadPage('tracuu')" style="cursor: pointer;">
                        <h3>🔍 Tra cứu</h3>
                    </button>
                    <button class="stat-card" onclick="loadPage('baocao')" style="cursor: pointer;">
                        <h3>📈 Báo cáo</h3>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadPage(page) {
            window.location.href = '/' + page;
        }
        
        function logout() {
            if (confirm('Bạn có chắc muốn đăng xuất?')) {
                window.location.href = '/logout';
            }
        }
        
        // Load thống kê
        fetch('/api/thongke')
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('dashboardStats').innerHTML = `
                        <div class="stat-card bg-primary">
                            <h3>Tổng thí sinh</h3>
                            <div class="stat-number">${data.tong_thisinh}</div>
                        </div>
                        <div class="stat-card bg-success">
                            <h3>Đã duyệt</h3>
                            <div class="stat-number">${data.tong_da_duyet}</div>
                        </div>
                        <div class="stat-card bg-warning">
                            <h3>Chờ duyệt</h3>
                            <div class="stat-number">${data.tong_chua_duyet}</div>
                        </div>
                        <div class="stat-card bg-danger">
                            <h3>Đã thanh toán</h3>
                            <div class="stat-number">${data.tong_da_thanhtoan}</div>
                        </div>
                    `;
                }
            });
    </script>
</body>
</html>'''

    # 3. Quản lý thí sinh
    quanly_thisinh_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quản lý Thí sinh</title>
    <style>
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #f8f9fa; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); }
        .modal-content { background: white; margin: 5% auto; padding: 20px; width: 90%; max-width: 600px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>👥 Quản lý Thí sinh</h2>
            <button class="btn btn-primary" onclick="openModal()">➕ Thêm thí sinh</button>
            <input type="text" id="searchInput" placeholder="🔍 Tìm kiếm theo tên, CMND, mã thí sinh..." style="padding: 8px; width: 300px; margin-left: 20px;">
            <button class="btn" onclick="searchThisinh()">Tìm kiếm</button>
        </div>

        <div class="card">
            <div id="danhSachThisinh"></div>
        </div>
    </div>

    <!-- Modal thêm/sửa thí sinh -->
    <div id="modalThisinh" class="modal">
        <div class="modal-content">
            <h3 id="modalTitle">Thêm thí sinh mới</h3>
            <form id="formThisinh">
                <input type="hidden" id="thisinhId">
                <div class="form-group">
                    <label>Họ và tên *</label>
                    <input type="text" id="hoTen" required>
                </div>
                <div class="form-group">
                    <label>CMND/CCCD *</label>
                    <input type="text" id="cmnd" required>
                </div>
                <div class="form-group">
                    <label>Ngày sinh *</label>
                    <input type="date" id="ngaySinh" required>
                </div>
                <div class="form-group">
                    <label>Giới tính</label>
                    <select id="gioiTinh">
                        <option value="Nam">Nam</option>
                        <option value="Nữ">Nữ</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Địa chỉ</label>
                    <input type="text" id="diaChi">
                </div>
                <div class="form-group">
                    <label>Số điện thoại</label>
                    <input type="tel" id="sdt">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="email">
                </div>
                <div class="form-group">
                    <label>Trạng thái</label>
                    <select id="trangThai">
                        <option value="Chờ duyệt">Chờ duyệt</option>
                        <option value="Đã duyệt">Đã duyệt</option>
                        <option value="Từ chối">Từ chối</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success">💾 Lưu thông tin</button>
                <button type="button" class="btn" onclick="closeModal()">❌ Hủy</button>
            </form>
        </div>
    </div>

    <script>
        let currentEditId = null;

        function loadDanhSach() {
            fetch('/api/thisinh')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        let html = `<table>
                            <thead><tr><th>Mã TS</th><th>Họ tên</th><th>CMND</th><th>Ngày sinh</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
                            <tbody>`;
                        
                        data.data.forEach(ts => {
                            let badgeColor = ts.trang_thai === 'Đã duyệt' ? 'green' : 
                                           ts.trang_thai === 'Từ chối' ? 'red' : 'orange';
                            html += `
                                <tr>
                                    <td>${ts.ma_thisinh}</td>
                                    <td>${ts.ho_ten}</td>
                                    <td>${ts.cmnd}</td>
                                    <td>${ts.ngay_sinh}</td>
                                    <td><span style="color: ${badgeColor}; font-weight: bold;">${ts.trang_thai}</span></td>
                                    <td>
                                        <button class="btn btn-primary" onclick="editThisinh(${ts.id})">✏️ Sửa</button>
                                        <button class="btn btn-danger" onclick="deleteThisinh(${ts.id})">🗑️ Xóa</button>
                                    </td>
                                </tr>
                            `;
                        });
                        
                        html += '</tbody></table>';
                        document.getElementById('danhSachThisinh').innerHTML = html;
                    }
                });
        }

        function openModal(editId = null) {
            currentEditId = editId;
            const modal = document.getElementById('modalThisinh');
            const title = document.getElementById('modalTitle');
            
            if (editId) {
                title.textContent = 'Sửa thông tin thí sinh';
                // Load data for editing
                fetch('/api/thisinh')
                    .then(r => r.json())
                    .then(data => {
                        const ts = data.data.find(t => t.id === editId);
                        if (ts) {
                            document.getElementById('thisinhId').value = ts.id;
                            document.getElementById('hoTen').value = ts.ho_ten;
                            document.getElementById('cmnd').value = ts.cmnd;
                            document.getElementById('ngaySinh').value = ts.ngay_sinh;
                            document.getElementById('gioiTinh').value = ts.gioi_tinh;
                            document.getElementById('diaChi').value = ts.dia_chi;
                            document.getElementById('sdt').value = ts.sdt;
                            document.getElementById('email').value = ts.email;
                            document.getElementById('trangThai').value = ts.trang_thai;
                        }
                    });
            } else {
                title.textContent = 'Thêm thí sinh mới';
                document.getElementById('formThisinh').reset();
            }
            modal.style.display = 'block';
        }

        function closeModal() {
            document.getElementById('modalThisinh').style.display = 'none';
            currentEditId = null;
        }

        function searchThisinh() {
            const search = document.getElementById('searchInput').value;
            fetch('/api/thisinh?search=' + encodeURIComponent(search))
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        let html = `<table><thead><tr><th>Mã TS</th><th>Họ tên</th><th>CMND</th><th>Ngày sinh</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>`;
                        data.data.forEach(ts => {
                            let badgeColor = ts.trang_thai === 'Đã duyệt' ? 'green' : 
                                           ts.trang_thai === 'Từ chối' ? 'red' : 'orange';
                            html += `
                                <tr>
                                    <td>${ts.ma_thisinh}</td>
                                    <td>${ts.ho_ten}</td>
                                    <td>${ts.cmnd}</td>
                                    <td>${ts.ngay_sinh}</td>
                                    <td><span style="color: ${badgeColor}; font-weight: bold;">${ts.trang_thai}</span></td>
                                    <td>
                                        <button class="btn btn-primary" onclick="editThisinh(${ts.id})">✏️ Sửa</button>
                                        <button class="btn btn-danger" onclick="deleteThisinh(${ts.id})">🗑️ Xóa</button>
                                    </td>
                                </tr>
                            `;
                        });
                        html += '</tbody></table>';
                        document.getElementById('danhSachThisinh').innerHTML = html;
                    }
                });
        }

        document.getElementById('formThisinh').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                ho_ten: document.getElementById('hoTen').value,
                cmnd: document.getElementById('cmnd').value,
                ngay_sinh: document.getElementById('ngaySinh').value,
                gioi_tinh: document.getElementById('gioiTinh').value,
                dia_chi: document.getElementById('diaChi').value,
                sdt: document.getElementById('sdt').value,
                email: document.getElementById('email').value,
                trang_thai: document.getElementById('trangThai').value
            };

            if (currentEditId) {
                // Update
                fetch('/api/thisinh/' + currentEditId, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                })
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        closeModal();
                        loadDanhSach();
                    }
                });
            } else {
                // Create
                fetch('/api/thisinh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                })
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) {
                        closeModal();
                        loadDanhSach();
                    }
                });
            }
        });

        function editThisinh(id) {
            openModal(id);
        }

        function deleteThisinh(id) {
            if (confirm('Bạn có chắc muốn xóa thí sinh này?')) {
                fetch('/api/thisinh/' + id, { method: 'DELETE' })
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        if (data.success) loadDanhSach();
                    });
            }
        }

        // Load danh sách khi trang được tải
        window.onload = loadDanhSach;
    </script>
</body>
</html>'''

    # 4. Tra cứu
    tracuu_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tra cứu Thí sinh</title>
    <style>
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .info-item { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>🔍 Tra cứu Thông tin Thí sinh</h2>
            <div class="form-group">
                <label>Nhập CMND/CCCD của thí sinh:</label>
                <input type="text" id="cmndInput" placeholder="Ví dụ: 001123456789">
            </div>
            <button class="btn" onclick="tracuu()">🔍 Tra cứu</button>
        </div>

        <div class="card" id="ketQuaTraCuu" style="display: none;">
            <h3>📋 Kết quả tra cứu</h3>
            <div id="thongTinThisinh"></div>
        </div>
    </div>

    <script>
        function tracuu() {
            const cmnd = document.getElementById('cmndInput').value.trim();
            if (!cmnd) {
                alert('Vui lòng nhập CMND/CCCD');
                return;
            }

            fetch('/api/tracuu/' + cmnd)
                .then(r => r.json())
                .then(data => {
                    const resultDiv = document.getElementById('ketQuaTraCuu');
                    const infoDiv = document.getElementById('thongTinThisinh');
                    
                    if (data.success) {
                        const ts = data.thisinh;
                        let html = `
                            <div class="info-item">
                                <strong>Mã thí sinh:</strong> ${ts.ma_thisinh}
                            </div>
                            <div class="info-item">
                                <strong>Họ tên:</strong> ${ts.ho_ten}
                            </div>
                            <div class="info-item">
                                <strong>CMND:</strong> ${ts.cmnd}
                            </div>
                            <div class="info-item">
                                <strong>Ngày sinh:</strong> ${ts.ngay_sinh}
                            </div>
                            <div class="info-item">
                                <strong>Giới tính:</strong> ${ts.gioi_tinh}
                            </div>
                            <div class="info-item">
                                <strong>Trạng thái:</strong> <span style="color: ${ts.trang_thai === 'Đã duyệt' ? 'green' : 'orange'}; font-weight: bold;">${ts.trang_thai}</span>
                            </div>
                        `;

                        if (data.nguyenvong && data.nguyenvong.length > 0) {
                            html += `<div class="info-item"><strong>Nguyện vọng:</strong><ul>`;
                            data.nguyenvong.forEach(nv => {
                                html += `<li>${nv.ten_nganh} - Điểm: ${nv.diem_thi || 'Chưa có'}</li>`;
                            });
                            html += `</ul></div>`;
                        }

                        if (data.thanhtoan) {
                            html += `<div class="info-item">
                                <strong>Thanh toán:</strong> ${data.thanhtoan.trang_thai} - ${data.thanhtoan.so_tien} VND
                            </div>`;
                        }

                        infoDiv.innerHTML = html;
                        resultDiv.style.display = 'block';
                    } else {
                        infoDiv.innerHTML = `<div style="color: red; text-align: center;">❌ ${data.message}</div>`;
                        resultDiv.style.display = 'block';
                    }
                });
        }

        // Cho phép nhấn Enter để tra cứu
        document.getElementById('cmndInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                tracuu();
            }
        });
    </script>
</body>
</html>'''

    # 5. Báo cáo
    baocao_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Thống kê</title>
    <style>
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-item { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .chart-container { height: 300px; margin: 20px 0; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>📈 Báo cáo Thống kê Tuyển sinh</h2>
            <button class="btn" onclick="loadThongKe()">🔄 Tải lại dữ liệu</button>
        </div>

        <div class="card">
            <h3>📊 Tổng quan</h3>
            <div class="stats-grid" id="tongQuanStats"></div>
        </div>

        <div class="card">
            <h3>📋 Thống kê theo Trạng thái</h3>
            <canvas id="chartTrangThai" class="chart-container"></canvas>
        </div>

        <div class="card">
            <h3>🎯 Thống kê theo Ngành học</h3>
            <canvas id="chartNganh" class="chart-container"></canvas>
        </div>
    </div>

    <script>
        let chartTrangThai, chartNganh;

        function loadThongKe() {
            fetch('/api/thongke')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        // Tổng quan
                        document.getElementById('tongQuanStats').innerHTML = `
                            <div class="stat-item" style="background: #3498db; color: white;">
                                <div>Tổng thí sinh</div>
                                <div class="stat-number">${data.tong_thisinh}</div>
                            </div>
                            <div class="stat-item" style="background: #27ae60; color: white;">
                                <div>Đã duyệt</div>
                                <div class="stat-number">${data.tong_da_duyet}</div>
                            </div>
                            <div class="stat-item" style="background: #f39c12; color: white;">
                                <div>Chờ duyệt</div>
                                <div class="stat-number">${data.tong_chua_duyet}</div>
                            </div>
                            <div class="stat-item" style="background: #e74c3c; color: white;">
                                <div>Đã thanh toán</div>
                                <div class="stat-number">${data.tong_da_thanhtoan}</div>
                            </div>
                        `;

                        // Biểu đồ trạng thái
                        const ctx1 = document.getElementById('chartTrangThai').getContext('2d');
                        if (chartTrangThai) chartTrangThai.destroy();
                        
                        chartTrangThai = new Chart(ctx1, {
                            type: 'pie',
                            data: {
                                labels: Object.keys(data.thongke_trangthai),
                                datasets: [{
                                    data: Object.values(data.thongke_trangthai),
                                    backgroundColor: ['#3498db', '#27ae60', '#f39c12', '#e74c3c']
                                }]
                            }
                        });

                        // Biểu đồ ngành học
                        const ctx2 = document.getElementById('chartNganh').getContext('2d');
                        if (chartNganh) chartNganh.destroy();
                        
                        const labels = data.thongke_nganh.map(n => n.ten_nganh);
                        const values = data.thongke_nganh.map(n => n.so_nguyenvong);
                        
                        chartNganh = new Chart(ctx2, {
                            type: 'bar',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: 'Số nguyện vọng',
                                    data: values,
                                    backgroundColor: '#3498db'
                                }]
                            }
                        });
                    }
                });
        }

        // Tải dữ liệu khi trang được tải
        window.onload = loadThongKe;
    </script>
</body>
</html>'''

    # 6. Quản lý ngành học
    quanly_nganh_html = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quản lý Ngành học</title>
    <style>
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn-primary { background: #3498db; color: white; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #f8f9fa; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>📚 Quản lý Ngành học</h2>
            <button class="btn btn-primary" onclick="showForm()">➕ Thêm ngành học</button>
        </div>

        <div class="card">
            <div id="danhSachNganh"></div>
        </div>

        <!-- Form thêm ngành học -->
        <div class="card" id="formNganh" style="display: none;">
            <h3>Thêm ngành học mới</h3>
            <form id="formThemNganh">
                <div class="form-group">
                    <label>Mã ngành *</label>
                    <input type="text" id="maNganh" required>
                </div>
                <div class="form-group">
                    <label>Tên ngành *</label>
                    <input type="text" id="tenNganh" required>
                </div>
                <div class="form-group">
                    <label>Chỉ tiêu *</label>
                    <input type="number" id="chiTieu" required>
                </div>
                <div class="form-group">
                    <label>Điểm chuẩn</label>
                    <input type="number" step="0.1" id="diemChuan">
                </div>
                <button type="submit" class="btn btn-primary">💾 Lưu ngành học</button>
                <button type="button" class="btn" onclick="hideForm()">❌ Hủy</button>
            </form>
        </div>
    </div>

    <script>
        function loadDanhSachNganh() {
            fetch('/api/nganh_hoc')
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        let html = `<table>
                            <thead>
                                <tr>
                                    <th>Mã ngành</th>
                                    <th>Tên ngành</th>
                                    <th>Chỉ tiêu</th>
                                    <th>Điểm chuẩn</th>
                                </tr>
                            </thead>
                            <tbody>`;
                        
                        data.data.forEach(nganh => {
                            html += `
                                <tr>
                                    <td>${nganh.ma_nganh}</td>
                                    <td>${nganh.ten_nganh}</td>
                                    <td>${nganh.chi_tieu}</td>
                                    <td>${nganh.diem_chuan || 'Chưa có'}</td>
                                </tr>
                            `;
                        });
                        
                        html += '</tbody></table>';
                        document.getElementById('danhSachNganh').innerHTML = html;
                    }
                });
        }

        function showForm() {
            document.getElementById('formNganh').style.display = 'block';
        }

        function hideForm() {
            document.getElementById('formNganh').style.display = 'none';
            document.getElementById('formThemNganh').reset();
        }

        document.getElementById('formThemNganh').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                ma_nganh: document.getElementById('maNganh').value,
                ten_nganh: document.getElementById('tenNganh').value,
                chi_tieu: parseInt(document.getElementById('chiTieu').value),
                diem_chuan: parseFloat(document.getElementById('diemChuan').value) || null
            };

            fetch('/api/nganh_hoc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(r => r.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    hideForm();
                    loadDanhSachNganh();
                }
            });
        });

        // Load danh sách khi trang được tải
        window.onload = loadDanhSachNganh;
    </script>
</body>
</html>'''

    # ========== TẠO CÁC FILE ==========
    
    create_file('app.py', app_content)
    create_file('requirements.txt', 'Flask==2.3.3\n')
    
    # Tạo các template
    create_file('templates/login.html', login_html)
    create_file('templates/dashboard.html', dashboard_html)
    create_file('templates/quanly_thisinh.html', quanly_thisinh_html)
    create_file('templates/tracuu.html', tracuu_html)
    create_file('templates/baocao.html', baocao_html)
    create_file('templates/quanly_nganh.html', quanly_nganh_html)
    
    # Khởi tạo database
    init_database()
    
    print(f"\n🎉 HỆ THỐNG HOÀN CHỈNH ĐÃ ĐƯỢC TẠO!")
    print(f"📁 Thư mục: {project_dir}")
    print(f"🔧 Các bước chạy:")
    print(f"1. cd {project_dir}")
    print(f"2. pip install -r requirements.txt")
    print(f"3. python app.py")
    print(f"4. Truy cập: http://localhost:5000")
    print(f"🔑 Tài khoản demo: admin / admin123")
    print(f"\n🌟 TÍNH NĂNG CÓ SẴN:")
    print(f"✅ Đăng nhập hệ thống")
    print(f"✅ Quản lý thí sinh (Thêm, Sửa, Xóa, Tìm kiếm)")
    print(f"✅ Tra cứu thông tin")
    print(f"✅ Báo cáo thống kê với biểu đồ")
    print(f"✅ Quản lý ngành học")
    print(f"✅ Database SQLite với dữ liệu mẫu")

def main():
    print("🚀 BẮT ĐẦU TẠO HỆ THỐNG TUYỂN SINH HOÀN CHỈNH...")
    create_complete_system()

if __name__ == "__main__":
    main()
