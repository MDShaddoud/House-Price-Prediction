from market import app
from flask import render_template,url_for,redirect,flash,request
from market.models import User
from market.forms import Registerform,loginform
from market import db
from flask_login import login_user,logout_user,login_required
from flask import Flask, request


from flask_cors import CORS, cross_origin
import pandas as pd
import numpy as np
import pickle


#Decorators
@app.route('/')

@app.route('/home')
def home_page():
    return render_template("home.html")

@app.route('/register',methods=['GET','POST'])
def Register_page():
#now will create instance from registerform class
    form=Registerform()
    if form.validate_on_submit():
        #this username =form.username which is recive vlaue from user field
        user_to_create=User(username=form.username.data,
                            email=form.email.data,
                            password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user:{err_msg}',category='danger')

    return render_template('register.html',form=form)

@app.route('/logot')
def logout_page():
    logout_user()
    flash('you have been logged out',category='info')
    return redirect (url_for('home_page'))


@app.route('/login',methods=['GET','POST'])
def login_page():
    form=loginform()
    if form.validate_on_submit():
        attemped_user=User.query.filter_by(username=form.username.data).first()
        if attemped_user and attemped_user.check_password_correction(attemped_password=form.password.data):
            login_user(attemped_user)
            flash(f'Success! you are logged in as:{attemped_user.username}',category='success')
            return redirect(url_for('home_page'))
        else:
            flash("username and password are not match!please try again",category='danger')


    return render_template('login.html',form=form)


# app = Flask(__name__)
House_df = pd.read_csv('C:\\Users\\jhbvjhv\\Desktop\\test\\test\\market\\Clean_data.csv')
cors = CORS(app)

model = pickle.load(open('C:\\Users\\jhbvjhv\\Desktop\\test\\test\\market\\XGRB.pkl', 'rb'))


@app.route('/predict_page')
@login_required
def predict_page():
    Cetnral_Air = sorted(House_df['CentralAir'].unique())
    Heating = sorted(House_df['Heating'].unique())
    Neighborhood = sorted(House_df['Neighborhood'].unique())
    GarageType = sorted(House_df['GarageType'].unique())
    GarageCar = sorted(House_df['GarageCars'].unique())
    KitchenAbvGr = sorted(House_df['KitchenAbvGr'].unique())
    YearBuilt = sorted(House_df['YearBuilt'].unique(), reverse=True)
    FullBath = sorted(House_df['FullBath'].unique())
    
    print(Cetnral_Air)
    return render_template("predict.html", Cetnral_Air=Cetnral_Air, Heating=Heating, Neighborhood=Neighborhood,
                           GarageType=GarageType, GarageCar=GarageCar, KitchenAbvGr=KitchenAbvGr, YearBuilt=YearBuilt,
                           FullBath=FullBath)




@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    user_input = ['CentralAir', 'Heating', 'Neighborhood', 'GarageType', 'GarageCars', 'KitchenAbvGr', 'YearBuilt', 'FullBath']
    CentralAir = request.form.get('CentralAir')
    Heating = request.form.get('Heating')
    Neighborhood = request.form.get('Neighborhood')
    GarageType = request.form.get('GarageType')
    GarageCar = request.form.get('GarageCar')
    KitchenAbvGr = request.form.get('KitchenAbvGr')
    YearBuilt = request.form.get('YearBuilt')
    FullBath = request.form.get('FullBath')

    random_cols = ['Id', 'MSSubClass', 'MSZoning', 'LotArea', 'Street', 'LotShape', 'LandContour', 'Utilities',
                   'LotConfig',
                   'LandSlope', 'Condition1', 'Condition2', 'BldgType', 'HouseStyle', 'OverallCond', 'YearRemodAdd',
                   'RoofStyle',
                   'RoofMatl', 'Exterior1st', 'Exterior2nd', 'MasVnrType', 'MasVnrArea', 'ExterQual', 'ExterCond',
                   'Foundation',
                   'BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinSF1', 'BsmtFinType2', 'BsmtFinSF2',
                   'BsmtUnfSF',
                   'TotalBsmtSF', 'HeatingQC', 'Electrical', '1stFlrSF', '2ndFlrSF', 'LowQualFinSF', 'GrLivArea',
                   'BsmtFullBath',
                   'BsmtHalfBath', 'BedroomAbvGr', 'KitchenQual', 'TotRmsAbvGrd', 'Functional', 'Fireplaces',
                   'GarageYrBlt',
                   'GarageFinish', 'GarageArea', 'GarageQual', 'GarageCond', 'PavedDrive', 'WoodDeckSF', 'OpenPorchSF',
                   'EnclosedPorch', '3SsnPorch', 'ScreenPorch', 'PoolArea', 'MiscVal', 'MoSold', 'YrSold', 'SaleType',
                   'SaleCondition']
    data = {}
    for col in House_df.columns:
        if col in user_input:
            data[col] = [request.form.get(col)]
        elif House_df[col].dtype.kind in 'inf':
            data[col] = [np.random.uniform(House_df[col].min(), House_df[col].max())]
        else:
            values = House_df[col].dropna().unique()
            probabilities = House_df[col].dropna().value_counts(normalize=True)
            data[col] = [np.random.choice(values, p=probabilities)]
    df = pd.DataFrame(data)

    for col in random_cols:
        if col not in df.columns:
            df[col] = np.random.uniform(House_df[col].min(), House_df[col].max())

    price = model.predict(df)
    response = {
        'prediction': price
     }

    return json.dumps(response)










