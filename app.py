#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
from models import db, Doctor, Patient, Appointment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.get("/")
def index():
    return "doctor/patient"


@app.get("/doctors")
def get_doctors():
    doctors = Doctor.query.all()
    return [d.to_dict(rules=["-appointments"]) for d in doctors], 200


@app.get("/doctors/<int:id>")
def get_doctor_by_id(id):
    doctor = db.session.get(Doctor, id)
    if not doctor:
        return {"error": "not found"}, 404
    return (
        doctor.to_dict(rules=["-appointments.patient_id", "-appointments.doctor_id"]),
        200,
    )


@app.get("/patients/<int:id>")
def get_patient_by_id(id):
    patient = db.session.get(Patient, id)
    if not patient:
        return {"error": "not found"}, 404
    patient_dict = patient.to_dict(rules=['-appointments'])
    doctor_dicts = [d.to_dict(rules=['-appointments']) for d in patient.doctors]
    patient_dict["doctors"] = doctor_dicts
    return patient_dict, 200

@app.patch('/patients/<int:id>')
def patch_patient(id):
    try:
        data = request.json
        patient = db.session.get(Patient, id)
        if not patient:
            return {"error": "not found"}, 404
        for key in data:
            setattr(patient, key, data[key])
        db.session.add(patient)
        db.session.commit()
        return patient.to_dict(rules=['-appointments'])
    except Exception as e:
        return {"error": str(e)}, 404

@app.post('/appointments')
def post_appointments():
    try:
        data = request.json
        appointment = Appointment(day=data.get('day'), patient_id=data.get('patient_id'), doctor_id=data.get('doctor_id'))
        db.session.add(appointment)
        db.session.commit()
        return appointment.to_dict(rules=['-doctor_id', '-patient_id'])
    except Exception as e:
        return {"error": str(e)}, 404
        

@app.post("/doctors")
def post_doctor():
    try:
        data = request.json
        doctor = Doctor(name=data.get("name"), specialty=data.get("specialty"))
        db.session.add(doctor)
        db.session.commit()
        return doctor.to_dict(), 201
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(port=5555, debug=True)
