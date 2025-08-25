from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from app import db
from app.forms import LoginForm, RegistrationForm, DepositForm, WithdrawForm, TransferForm
from app.models import User, Account, Transaction
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from functools import wraps

main = Blueprint('main', __name__)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You must be an admin to view this page.")
            return redirect(url_for('main.index'))
        return fn(*args, **kwargs)
    return wrapper

@main.route('/')
@main.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    accounts = current_user.accounts.all()
    account_ids = [account.id for account in accounts]
    transactions = Transaction.query.filter(Transaction.account_id.in_(account_ids)).order_by(Transaction.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['TRANSACTIONS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('main.index', page=transactions.prev_num) \
        if transactions.has_prev else None
    return render_template('dashboard.html', title='Dashboard', accounts=accounts, transactions=transactions.items,
                           next_url=next_url, prev_url=prev_url)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        if user.is_suspended:
            flash('Your account has been suspended.')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()  # Commit user to get an ID

        # Create default accounts for the new user
        checking_account = Account(account_type='checking', user_id=user.id)
        savings_account = Account(account_type='savings', user_id=user.id)
        db.session.add(checking_account)
        db.session.add(savings_account)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', title='Admin Dashboard', users=users)

@main.route('/user/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    accounts = user.accounts.all()
    account_ids = [account.id for account in accounts]
    transactions = Transaction.query.filter(Transaction.account_id.in_(account_ids)).order_by(Transaction.timestamp.desc()).all()
    return render_template('user_details.html', title=f'Details for {user.username}',
                           user=user, accounts=accounts, transactions=transactions)

@main.route('/user/<int:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('You cannot suspend an admin user.')
    else:
        user.is_suspended = not user.is_suspended
        db.session.commit()
        flash(f'User {user.username} has been {"suspended" if user.is_suspended else "unsuspended"}.')
    return redirect(url_for('main.user_details', user_id=user_id))

@main.route('/user/<int:user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own admin status.')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'User {user.username} is now {"an admin" if user.is_admin else "not an admin"}.')
    return redirect(url_for('main.user_details', user_id=user_id))

@main.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    form = DepositForm()
    if form.validate_on_submit():
        # For simplicity, we deposit to the user's checking account
        account = current_user.accounts.filter_by(account_type='checking').first()
        if account:
            amount = form.amount.data
            account.balance += amount
            transaction = Transaction(amount=amount, type='deposit', account_id=account.id)
            db.session.add(transaction)
            db.session.commit()
            flash(f'Successfully deposited ${amount:.2f}.')
            return redirect(url_for('main.index'))
        else:
            flash('Checking account not found.')
    return render_template('deposit.html', title='Deposit', form=form)

@main.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    form = WithdrawForm()
    if form.validate_on_submit():
        # For simplicity, we withdraw from the user's checking account
        account = current_user.accounts.filter_by(account_type='checking').first()
        if account:
            amount = form.amount.data
            if account.balance >= amount:
                account.balance -= amount
                transaction = Transaction(amount=amount, type='withdrawal', account_id=account.id)
                db.session.add(transaction)
                db.session.commit()
                flash(f'Successfully withdrew ${amount:.2f}.')
                return redirect(url_for('main.index'))
            else:
                flash('Insufficient funds.')
        else:
            flash('Checking account not found.')
    return render_template('withdraw.html', title='Withdraw', form=form)

@main.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    form = TransferForm()
    if form.validate_on_submit():
        amount = form.amount.data
        recipient_email = form.recipient_email.data

        sender_account = current_user.accounts.filter_by(account_type='checking').first()

        if sender_account is None:
            flash('Your checking account was not found.')
            return redirect(url_for('main.transfer'))

        if sender_account.balance < amount:
            flash('Insufficient funds.')
            return redirect(url_for('main.transfer'))

        recipient = User.query.filter_by(email=recipient_email).first()
        if recipient is None:
            flash('Recipient not found.')
            return redirect(url_for('main.transfer'))

        if recipient.id == current_user.id:
            flash('You cannot transfer money to yourself.')
            return redirect(url_for('main.transfer'))

        recipient_account = recipient.accounts.filter_by(account_type='checking').first()
        if recipient_account is None:
            flash('Recipient does not have a checking account.')
            return redirect(url_for('main.transfer'))

        try:
            sender_account.balance -= amount
            recipient_account.balance += amount

            sender_transaction = Transaction(amount=-amount, type='transfer', account_id=sender_account.id)
            recipient_transaction = Transaction(amount=amount, type='transfer', account_id=recipient_account.id)

            db.session.add(sender_transaction)
            db.session.add(recipient_transaction)
            db.session.commit()

            flash(f'Successfully transferred ${amount:.2f} to {recipient.username}.')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during the transfer. Please try again.')

    return render_template('transfer.html', title='Transfer', form=form)
