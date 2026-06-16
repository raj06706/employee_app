from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------
# Database Model
# -------------------------
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "emp_code": self.emp_code,
            "name": self.name,
            "role": self.role,
            "department": self.department
        }


# -------------------------
# UI Routes
# -------------------------
@app.route('/')
def index():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    return render_template('index.html', employees=employees)


@app.route('/add', methods=['POST'])
def add_employee():
    emp_code = request.form['emp_code'].strip()
    name = request.form['name'].strip()
    role = request.form['role'].strip()
    department = request.form['department'].strip()

    existing = Employee.query.filter_by(emp_code=emp_code).first()
    if existing:
        flash('Employee code already exists.', 'error')
        return redirect(url_for('index'))

    employee = Employee(
        emp_code=emp_code,
        name=name,
        role=role,
        department=department
    )
    db.session.add(employee)
    db.session.commit()

    flash('Employee added successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/edit/<int:id>')
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    return render_template('edit.html', employee=employee)


@app.route('/update/<int:id>', methods=['POST'])
def update_employee(id):
    employee = Employee.query.get_or_404(id)

    emp_code = request.form['emp_code'].strip()
    name = request.form['name'].strip()
    role = request.form['role'].strip()
    department = request.form['department'].strip()

    duplicate = Employee.query.filter(Employee.emp_code == emp_code, Employee.id != id).first()
    if duplicate:
        flash('Another employee already uses this code.', 'error')
        return redirect(url_for('edit_employee', id=id))

    employee.emp_code = emp_code
    employee.name = name
    employee.role = role
    employee.department = department

    db.session.commit()
    flash('Employee updated successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully.', 'success')
    return redirect(url_for('index'))


# -------------------------
# API Routes
# -------------------------
@app.route('/api/employees', methods=['GET'])
def api_get_employees():
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees])


@app.route('/api/employees/<int:id>', methods=['GET'])
def api_get_employee(id):
    employee = Employee.query.get_or_404(id)
    return jsonify(employee.to_dict())


@app.route('/api/employees', methods=['POST'])
def api_create_employee():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    emp_code = data.get('emp_code')
    name = data.get('name')
    role = data.get('role')
    department = data.get('department')

    if not emp_code or not name or not role or not department:
        return jsonify({"error": "emp_code, name, role, department are required"}), 400

    existing = Employee.query.filter_by(emp_code=emp_code).first()
    if existing:
        return jsonify({"error": "Employee code already exists"}), 409

    employee = Employee(
        emp_code=emp_code,
        name=name,
        role=role,
        department=department
    )
    db.session.add(employee)
    db.session.commit()

    return jsonify(employee.to_dict()), 201


@app.route('/api/employees/<int:id>', methods=['PUT'])
def api_update_employee(id):
    employee = Employee.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    emp_code = data.get('emp_code', employee.emp_code)
    name = data.get('name', employee.name)
    role = data.get('role', employee.role)
    department = data.get('department', employee.department)

    duplicate = Employee.query.filter(Employee.emp_code == emp_code, Employee.id != id).first()
    if duplicate:
        return jsonify({"error": "Another employee already uses this emp_code"}), 409

    employee.emp_code = emp_code
    employee.name = name
    employee.role = role
    employee.department = department

    db.session.commit()
    return jsonify(employee.to_dict())


@app.route('/api/employees/<int:id>', methods=['DELETE'])
def api_delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)