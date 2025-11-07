from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
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
