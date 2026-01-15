from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLLACHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Model definition
class Plant(db.Model):
    __tablename__ = "plants"

    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(100), nullable=False)
    bloom_seasons = db.Column(ARRAY(String), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "common_name": self.common_name,
            "bloom_seasons": self.bloom_seasons,
        }


# Routes


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/json-plants")
def get_json_plants():
    """Return all plants as JSON"""
    plants = Plant.query.all()
    return jsonify([plant.to_dict() for plant in plants])


@app.get("/api/plants")
def get_plants():
    """Return plants template plants-results"""
    print("=" * 50)
    print("Request args:", request.args)
    print("Season param:", request.args.get('bloom_season'))
    print("=" * 50)
    if request.args:
        season = request.args.get('bloom_season')
        plants = Plant.query.filter(Plant.bloom_seasons.any(season))
    else:
        plants = db.session.execute(db.select(Plant).order_by(Plant.common_name)).scalars()
    print(plants)
    return render_template("plant-results.html", plants=plants)


@app.post("/init-db")
def init_db():
    """Create tables - visit this route once to setup database"""
    db.create_all()
    return "Database tables created!"


@app.post("/seed-data")
def seed_data():
    """Add test data - visit this route once to populate database"""

    # Clear existing data
    Plant.query.delete()

    # Add 5 test plants
    plants = [
        Plant(common_name="bee balm", bloom_seasons=["mid_summer", "late_summer"]),
        Plant(
            common_name="black-eyed susan",
            bloom_seasons=["mid_summer", "late_summer", "early_autumn"],
        ),
        Plant(
            common_name="purple coneflower", bloom_seasons=["mid_summer", "late_summer"]
        ),
        Plant(common_name="blue flag iris", bloom_seasons=["spring", "early_summer"]),
        Plant(
            common_name="cardinal flower",
            bloom_seasons=["mid_summer", "late_summer", "early_autumn"],
        ),
    ]

    db.session.add_all(plants)
    db.session.commit()

    return "Test data added!"


if __name__ == "__main__":
    app.run(debug=True)
