import random

from sqlalchemy import func

from models.user import User, Role
from models.product import Product, ProductOrder, ProductTransaction
from models.client import Client
from util import db, bcrypt
from config import Config

#
# User examples
#

db.session.add(User(username='adm',
                    password=bcrypt.generate_password_hash("1234").decode('utf-8'),
                    role=Role.ADMIN))
db.session.add(User(username='man',
                    password=bcrypt.generate_password_hash("1234").decode('utf-8'),
                    role=Role.MANAGER))
db.session.add(User(username='op',
                    password=bcrypt.generate_password_hash("1234").decode('utf-8'),
                    role=Role.OPERATOR))
db.session.commit()

#
# Client example
#

db.session.add(Client(name="Torvaldo",
                      phone_number=81912345678,
                      is_deleted=False))
db.session.commit()
torvaldo = Client.query.first()
torvaldo_orders_to_do = Config.MAX_UNPAID_ORDERS

#
# Product examples
#

Product.add_to_db(name='Banana Nanica 1kg',
                  unit_price=350,
                  units_stored=100,
                  units_min=50)
Product.add_to_db(name='Tomate Italiano 1kg',
                  unit_price=850,
                  units_stored=80,
                  units_min=50)
Product.add_to_db(name='Cebola Branca 1kg',
                  unit_price=500,
                  units_stored=120,
                  units_min=80)
Product.add_to_db(name='Maçã Gala 1kg',
                  unit_price=699,
                  units_stored=60,
                  units_min=50)
Product.add_to_db(name='Batata Inglesa 1kg',
                  unit_price=320,
                  units_stored=150,
                  units_min=130)
Product.add_to_db(name='Abacaxi',
                  unit_price=389,
                  units_stored=50,
                  units_min=48)
Product.add_to_db(name='Abacate',
                  unit_price=650,
                  units_stored=20,
                  units_min=10)

Product.add_to_db(name='Queijo Mussarela 1kg',
                  unit_price=2990,
                  units_stored=40,
                  units_min=30)
leite = Product.add_to_db(name='Leite Desnatado 1L',
                          unit_price=420,
                          units_stored=230,
                          units_min=80)
manteiga = Product.add_to_db(name='Manteiga com Sal 200g',
                             unit_price=1190,
                             units_stored=110,
                             units_min=40)
iogurte = Product.add_to_db(name='Iogurte Natural 170g',
                            unit_price=290,
                            units_stored=125,
                            units_min=50)
Product.add_to_db(name='Requeijão Cremoso 200g',
                  unit_price=799,
                  units_stored=70,
                  units_min=60)

file_de_frango = Product.add_to_db(name='Filé de Frango 1kg',
                                   unit_price=1790,
                                   units_stored=100,
                                   units_min=45)
carne_moida_bovina = Product.add_to_db(name='Carne Moída Bovina 1kg',
                                       unit_price=3490,
                                       units_stored=150,
                                       units_min=45)
Product.add_to_db(name='Costela Suína 1kg',
                  unit_price=2990,
                  units_stored=30,
                  units_min=20)
Product.add_to_db(name='Linguiça Toscana 1kg',
                  unit_price=1590,
                  units_stored=60,
                  units_min=50)
Product.add_to_db(name='Picanha Bovina 1kg',
                  unit_price=5490,
                  units_stored=20,
                  units_min=15)

arroz = Product.add_to_db(name='Arroz Branco 5kg',
                          unit_price=2490,
                          units_stored=200,
                          units_min=80)
feijao = Product.add_to_db(name='Feijão Carioca 1kg',
                           unit_price=799,
                           units_stored=180,
                           units_min=70)
acucar = Product.add_to_db(name='Açúcar Cristal 5kg',
                           unit_price=1790,
                           units_stored=130,
                           units_min=60)
Product.add_to_db(name='Café em Pó 500g',
                  unit_price=1290,
                  units_stored=50,
                  units_min=40)
Product.add_to_db(name='Macarrão Espaguete 500g',
                  unit_price=399,
                  units_stored=100,
                  units_min=90)

refrigerante = Product.add_to_db(name='Refrigerante Coca-Cola 2L',
                                 unit_price=799,
                                 units_stored=200,
                                 units_min=80)
cerveja_skol = Product.add_to_db(name='Cerveja Skol Lata 350ml',
                                 unit_price=350,
                                 units_stored=210,
                                 units_min=150)
Product.add_to_db(name='Água Mineral 500ml',
                  unit_price=250,
                  units_stored=150,
                  units_min=130)
Product.add_to_db(name='Suco de Laranja 1L',
                  unit_price=499,
                  units_stored=60,
                  units_min=50)
Product.add_to_db(name='Vinho Tinto Seco 750ml',
                  unit_price=2490,
                  units_stored=40,
                  units_min=30)

Product.add_to_db(name='Detergente Neutro 500ml',
                  unit_price=250,
                  units_stored=100,
                  units_min=90)
sabao_em_barra = Product.add_to_db(name='Sabão em Barra 5 unidades',
                                   unit_price=599,
                                   units_stored=90,
                                   units_min=70)
Product.add_to_db(name='Desinfetante Pinho 1L',
                  unit_price=750,
                  units_stored=60,
                  units_min=50)
amaciante = Product.add_to_db(name='Amaciante de Roupas 2L',
                              unit_price=1290,
                              units_stored=50,
                              units_min=40)
agua_sanitaria = Product.add_to_db(name='Água Sanitária 1L',
                                   unit_price=450,
                                   units_stored=120,
                                   units_min=50)

Product.add_to_db(name='Papel Higiênico 12 rolos',
                  unit_price=1590,
                  units_stored=80,
                  units_min=70)
Product.add_to_db(name='Creme Dental Colgate 90g',
                  unit_price=499,
                  units_stored=90,
                  units_min=80)
Product.add_to_db(name='Sabonete Dove 90g',
                  unit_price=350,
                  units_stored=100,
                  units_min=90)
Product.add_to_db(name='Shampoo Pantene 400ml',
                  unit_price=1490,
                  units_stored=60,
                  units_min=50)
Product.add_to_db(name='Desodorante Rexona Aerosol 150ml',
                  unit_price=999,
                  units_stored=70,
                  units_min=60)

Product.add_to_db(name='Pneu Continental Aro 14',
                  unit_price=37490,
                  units_stored=40,
                  units_min=20)

#
# Order examples
#

association_examples = [
        [arroz, feijao, acucar],
        [leite, iogurte, manteiga],
        [file_de_frango, carne_moida_bovina, arroz],
        [refrigerante, cerveja_skol, carne_moida_bovina],
        [sabao_em_barra, amaciante, agua_sanitaria],
        ]

for assoc in association_examples:
    for _ in range(random.randint(6, 9)):
        order = ProductOrder()
        db.session.add(order)
        db.session.commit()
        quantities = [random.randint(1, 4) for _ in assoc]
        product_ts = []
        for i, product in enumerate(assoc):
            product_ts += [ProductTransaction(product_id=product.id,
                                              order_id=order.id,
                                              unit_price=product.unit_price,
                                              units=-quantities[i],
                                              is_valid=False)]
        if random.randint(0, 1) == 0:
            random_product = Product.query.order_by(func.random()).first()
            product_ts += [ProductTransaction(product_id=random_product.id,
                                              order_id=order.id,
                                              unit_price=random_product.unit_price,
                                              units=-1,
                                              is_valid=False)]
        if random.randint(0, 1) == 0:
            random_product = Product.query.order_by(func.random()).first()
            product_ts += [ProductTransaction(product_id=random_product.id,
                                              order_id=order.id,
                                              unit_price=random_product.unit_price,
                                              units=-1,
                                              is_valid=False)]
        db.session.add_all(product_ts)
        db.session.commit()
        if torvaldo_orders_to_do > 0:
            order.client_id = torvaldo.id
            torvaldo_orders_to_do -= 1
            order.is_paid = False
        else:
            order.is_paid = True
        order.add_to_db(*product_ts)
