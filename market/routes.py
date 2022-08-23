from re import purge
from sre_constants import SUCCESS
from unicodedata import category
from market import app
from flask import render_template, redirect, url_for, flash,request
from market.models import Item,User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET','POST' ])
@login_required
def market_page():
    purchase_form=PurchaseItemForm()
    selliing_form=SellItemForm()
    if request.method=="POST":
        #purchase item logic
        purchased_item = request.form.get('purchased_item')
        purchased_item_object = Item.query.filter_by(name=purchased_item).first()
        if purchased_item_object: 
            if current_user.can_purchase(purchased_item_object):
                purchased_item_object.buy(current_user)
                flash(f'congratulations you have purchased an item')
            else:
                flash(f'you dont have enought funds to buy {purchased_item_object}', category='danger ')
               #Sell Item Logic
        sold_item = request.form.get('sold_item')
        sell_item_object = Item.query.filter_by(name=sold_item).first()
        if sell_item_object:
            if current_user.can_sell(sell_item_object):
                sell_item_object.sell(current_user)
                flash(f"{sell_item_object.name} has been removed from your cart.", category='danger')
            else:
                flash(f"Could not remove {sell_item_object.name} from your cart", category='danger')


        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selliing_form)  



@app.route("/register", methods=['GET','POST' ])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                            email_address=form.email_address.data,
                            password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash (f'Success! {user_to_create.username}, your account has been created!',category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')


    return render_template("register.html", form=form)


@app.route('/login', methods= ['GET', 'POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user= User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
            ):
            login_user(attempted_user)
            flash (f'Success! You are logged in as: {attempted_user.username} ',category='success') 
            return redirect(url_for('market_page'))
        else:
            flash('User name and password do not match',category='danger')
        
    return render_template('login.html', form=form )

@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have been logged out', category='info')
    
    return redirect(url_for('home_page'))
