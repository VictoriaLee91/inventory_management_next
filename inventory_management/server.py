import peeweedbevolve
from flask import Flask, flash, redirect, render_template, request, url_for
from models import *

app = Flask(__name__)

app.secret_key = os.getenv('secret_key')


@app.before_request  # new line
def before_request():
    db.connect()


@app.after_request  # new line
def after_request(response):
    db.close()
    return response


@app.cli.command()  # new
def migrate():  # new
    db.evolve(ignore_tables={'base_model'})  # new


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/store")
def store():
    return render_template('store.html')


@app.route("/store_form", methods=["POST"])
def store_form():
    if request.method == "POST":
        s = Store(name=request.form['name'])

        if s.save():
            flash("Successfully saved!")
            return redirect(url_for('store', id=s.id))
        else:
            flash("Name is already taken.")
            return render_template('store.html', name=request.form['name'], errors=s.errors)
    else:
        render_template('store.html')


@app.route("/stores")
def stores():
    return render_template('stores.html', stores=Store.select())


@app.route("/store/<id>", methods=["GET"])
def storepage(id):
    return render_template('storepage.html', store=Store.get_by_id(id), warehouse=Warehouse.select().join(Store).where(Store.id == id))


@app.route("/store/<id>/edit", methods=["POST"])
def edit_store(id):
    return render_template('storepage.html', store=Store.get_by_id(id))


@app.route("/store/<id>", methods=["POST"])
def update_store(id):
    store = Store.get_by_id(id)
    newname = request.form.get('newname')
    store.name = newname

    if not store.save():
        flash(f"Unsuccessfully edited:{store_name}")
        return render_template('storepage.html', store=store)

    flash(f"Successfully updated to {newname}")
    return redirect(url_for('edit_store', id=store.id))


@app.route("/warehouse")
def warehouse():
    return render_template('warehouse.html', stores=Store.select())


@app.route("/warehouse_form", methods=["POST"])
def warehouse_form():
    warehouse_location = request.form.get('warehouse_location')
    store_id = request.form.get('store_id')
    w = Warehouse(location=warehouse_location, store=store_id)

    if w.save():
        flash(f"Added Warehouse: {warehouse_location}")
        return redirect(url_for('warehouse'))
    else:
        flash("Store already taken")
        return render_template('warehouse.html', stores=Store.select())


@app.route("/stores/<id>/delete", methods=["POST"])
def delete(id):
    store = Store.get_by_id(id)
    if store.delete_instance(recursive=True):
        flash(f"{store.name} deleted")

    return redirect(url_for('stores'))


if __name__ == '__main__':
    app.run()
