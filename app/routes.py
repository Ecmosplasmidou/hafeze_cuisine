from flask import render_template, url_for, flash, redirect, session, request
from . import db, mail
from .models import Plat, Commande, User
from .forms import AddItemForm, ContactForm, LoginForm
from flask import current_app as app
from werkzeug.utils import secure_filename
from .forms import ContactForm
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
import os
import stripe
import json
from werkzeug.security import generate_password_hash

@app.route('/')
@app.route('/index/')
def index():
    print("Accès à l'index")
    return render_template('index.html')

@app.route('/nos_plats/')
def plats():
    print("Accès à nos plats")
    plats = Plat.query.all()
    return render_template('plats.html', plats=plats)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    print("Accès à l'admin")
    form = AddItemForm()
    if form.validate_on_submit():
        # Gérer le téléchargement de l'image
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_folder = os.path.join(app.static_folder, 'pics')
            
            # Vérifiez et créez le dossier de destination si nécessaire
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            filepath = os.path.join(upload_folder, filename)
            form.image.data.save(filepath)
            print(f"Image saved to {filepath}")
        else:
            print("No image uploaded")

        plat = Plat(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=f'pics/{filename}' if form.image.data else None,  # Utiliser le chemin relatif à static
            available=form.available.data
        )
        db.session.add(plat)
        db.session.commit()
        flash('Plat ajouté avec succès', 'success')
        return redirect(url_for('admin'))
    plats = Plat.query.all()
    return render_template('admin.html', form=form, plats=plats)

@app.route('/admin/gestion')
@login_required
def admin_gestion():
    plats = Plat.query.all()
    return render_template('admin_gestion.html', plats=plats)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_dish(id):
    plat = Plat.query.get_or_404(id)
    db.session.delete(plat)
    db.session.commit()
    flash('Plat supprimé avec succès', 'success')
    return

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_dish(id):
    plat = Plat.query.get_or_404(id)
    form = AddItemForm(obj=plat)
    if form.validate_on_submit():
        plat.name = form.name.data
        plat.description = form.description.data
        plat.price = form.price.data
        plat.available = form.available.data
        db.session.commit()
        flash('Plat modifié avec succès', 'success')
        return redirect(url_for('admin_gestion'))
    return render_template('edit_dish.html', form=form, plat=plat)

@app.route('/add_to_cart/<int:plat_id>')
def add_to_cart(plat_id):
    plat = Plat.query.get_or_404(plat_id)
    cart = session.get('cart', [])
    cart.append({'id': plat.id, 'name': plat.name, 'price': plat.price, 'image': plat.image})
    session['cart'] = cart
    session['cart_count'] = len(cart)
    flash(f'{plat.name} a été ajouté au panier.', 'success')
    return redirect(url_for('plats'))

@app.route('/remove_from_cart/<int:plat_id>')
def remove_from_cart(plat_id):
    cart = session.get('cart', [])
    plat = next((item for item in cart if item['id'] == plat_id), None)
    if plat:
        cart.remove(plat)
        session['cart'] = cart
        session['cart_count'] = len(cart)
        flash(f'{plat["name"]} a été retiré du panier.', 'success')
    return redirect(request.referrer)

@app.route('/panier')
def panier():
    plat = Plat.query.all()
    cart = session.get('cart', [])
    total = round(sum(item['price'] for item in cart), 2)
    return render_template('panier.html', cart=cart, total=total, plat=plat)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

stripe.api_key = 'sk_test_51QH81bGHACZE09YR9mEYXV0Ia0jewywByIS1ARNw3v5lZKsDWJeDPSubVYQ25pBgzoMpFvKAUyoC2H5bo4DpP5fA00TL2gwJGU'

@app.route('/create_checkout_session', methods=['POST'])
def create_checkout_session():
    cart = session.get('cart', [])
    if not cart:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('panier'))

    line_items = [
        {
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(item['price'] * 100),
            },
            'quantity': 1,
        }
        for item in cart
    ]

    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cancel', _external=True),
    )

    return redirect(stripe_session.url, code=303)


@app.route('/success')
def success():
    cart = session.get('cart', [])
    if not cart:
        flash('Votre panier est vide.', 'warning')
        return redirect(url_for('index'))

    total = round(sum(item['price'] for item in cart), 2)
    items = json.dumps(cart)  # Convertir les articles en JSON pour les stocker dans la base de données
    
    plat_ids = [item['id'] for item in cart]
    plats = Plat.query.filter(Plat.id.in_(plat_ids)).all()

    # Enregistrer la commande dans la base de données
    commande = Commande(total=total, items=items, plats=plats)
    db.session.add(commande)
    db.session.commit()

    # Vider le panier
    session.pop('cart', None)
    session.pop('cart_count', None)

    flash('Paiement réussi !', 'success')
    return render_template('success.html', cart=cart, total=total, plats=plats)

@app.route('/cancel')
def cancel():
    flash('Paiement annulé.', 'warning')
    return redirect(url_for('panier'))

@app.route('/admin/commandes')
@login_required
def admin_commandes():
    commandes = Commande.query.filter_by(archived=False).order_by(Commande.date.desc()).all()
    
    # Compter les occurrences des plats pour chaque commande
    commandes_with_counts = []
    for commande in commandes:
        plat_counts = {}
        for item in json.loads(commande.items):
            plat_id = item['id']
            if plat_id in plat_counts:
                plat_counts[plat_id]['count'] += 1
            else:
                plat = Plat.query.get(plat_id)
                plat_counts[plat_id] = {'name': plat.name, 'count': 1}
        commandes_with_counts.append({'commande': commande, 'plat_counts': plat_counts})
    
    return render_template('admin_commandes.html', commandes=commandes_with_counts)

@app.route('/archive_commande/<int:commande_id>', methods=['POST'])
def archive_commande(commande_id):
    commande = Commande.query.get_or_404(commande_id)
    commande.archived = True
    db.session.commit()
    flash('Commande archivée avec succès.', 'success')
    return redirect(url_for('admin_commandes'))


@app.route('/contact')
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        msg = Message('Nouveau message de contact',
                      sender=email,
                      recipients=['ecmosdev@gmail.com'])
        msg.body = f"""
        De: {name} <{email}>
        Message: {message}
        """
        mail.send(msg)
        flash('Votre message a été envoyé avec succès.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin'))
        else:
            flash('Connexion impossible. Mail ou mot de passe incorrectes', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/delete_account')
@login_required
def delete_account():
    return render_template('delete_account.html')
    
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        db.session.delete(user)
        db.session.commit()
        flash('Le compte a été supprimé.', 'success')
        return redirect(url_for('index'))
    else:
        flash('Vous n\'avez pas l\'habilitation pour supprimer ce compte.', 'danger')
        return redirect(url_for('index'))