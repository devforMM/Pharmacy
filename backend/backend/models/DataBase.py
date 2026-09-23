from sqlalchemy.orm import declarative_base,sessionmaker,relationship
from sqlalchemy import Text,Integer,create_engine,Column,Float,JSON,ForeignKey

db_url=""
engine=create_engine(url=db_url)
session_maker=sessionmaker(bind=engine,autoflush=False)
base=declarative_base()


class Pharmacist(base):
    __tablename__="pharmacists"
    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    first_name=Column(Text,nullable=False)
    last_name=Column(Text,nullable=False)
    email=Column(Text,nullable=False,unique=True)
    password=Column(Text,nullable=False)
    phone_number=Column(Text,nullable=False)
    adress=Column(Text,nullable=False)
    sales=relationship("Sale",back_populates="pharmacist",foreign_keys="Sale.pharmacist_id")
    products=relationship("Product",back_populates="pharmacist",foreign_keys="Product.pharmacist_id")
    messages=relationship("Message",back_populates="pharmacist",foreign_keys="Message.pharmacist_id")
    requests=relationship("StockSupply",back_populates="pharmacist",foreign_keys="StockSupply.pharmacist_id")
    


class Supplier(base):
    __tablename__="suppliers"
    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    first_name=Column(Text,nullable=False)
    last_name=Column(Text,nullable=False)
    email=Column(Text,nullable=False,unique=True)
    password=Column(Text,nullable=False)
    phone_number=Column(Text,nullable=False)
    adress=Column(Text,nullable=False)
    stocks=relationship("Stock",back_populates="supplier",foreign_keys="Stock,supplier_id")
    requests=relationship("StockSupply",back_populates="supplier",foreign_keys="StockSupply.supplier_id")
    messages=relationship("Message",back_populates="supplier",foreign_keys="Message.supplier_id")
    

class Stock(base):
    __tablename__="stock"
    id=Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    product_name=Column(Text,nullable=False)
    cost_price=Column(Float,nullable=False)
    reference=Column(Text,nullable=False)
    expiration_date=Column(Text,nullable=False)
    quantity=Column(Integer,nullable=False)
    supplier_id=Column(Integer,ForeignKey("suppliers.id"),nullable=False)
    supplier=relationship("Supplier",foreign_keys=supplier_id,back_populates="stocks")








class Product(base):
    __tablename__="products"
    id=Column(Integer,nullable=False,primary_key=True,autoincrement=True)
    name=Column(Text,nullable=False)
    cost_price=Column(Float,nullable=False)
    reference=Column(Text,nullable=False)
    selling_price=Column(Float,nullable=True)
    quantity=Column(Integer,nullable=False)
    expiration_date=Column(Text,nullable=False)
    pharmacist_id=Column(Integer,ForeignKey("pharmacist.id"),nullable=True)
    pharmacist=relationship("Pharmacist",foreign_keys=pharmacist_id,back_populates="products")
    stock_id=Column(Integer,ForeignKey("stocks.id"),nullable=False)
    stock=relationship("Stock",foreign_keys=stock_id)
    supplier_id=Column(Integer,ForeignKey("suppliers.id"),nullable=False)
    supplier=relationship("Supplier",foreign_keys=supplier_id)


    







class Sale(base):
    __tablename__="sales"
    id=Column(Integer,nullable=False,autoincrement=True,primary_key=True)
    date=Column(Text,nullable=False)
    client=Column(Text,nullable=False)
    products=Column(JSON,nullable=False)
    pharmacist_id=Column(Integer,ForeignKey("pharmacists.id"),nullable=False)
    pharmacist=relationship("Pharmacist",back_populates="sales",foreign_keys=pharmacist_id)
    total=Column(Float,nullable=False)
    Profit=Column(Float,nullable=False)
    Cost=Column(Float,nullable=False)




class Supplyrequest(base):
    __tablename__="stocksupply"
    id=Column(Integer,nullable=False,autoincrement=True,primary_key=True)
    date=Column(Text,nullable=False)
    product_name=Column(Text,nullable=False)
    quantity=Column(Integer,nullable=False)
    supplier_id=Column(Integer,ForeignKey("Supplier.id"),nullable=False)
    supplier=relationship("Supplier",foreign_keys=supplier_id,back_populates="supplies")
    status=Column(Text,nullable=False)
    pharmacist_id=Column(Integer,ForeignKey("Pharmacist.id"),nullable=False)
    stock_id=Column(Integer,ForeignKey("Stock.id"))
    all_costs=Column(Float,nullable=False)



class Message(base):
    __tablename__="message"
    id=Column(Integer,nullable=False,autoincrement=True,primary_key=True)
    message_content=Column(Text,nullable=False)
    object=Column(Text,nullable=False)
    supplier_id=Column(Integer,ForeignKey("suppliers.id"))
    pharmacist_id=Column(Integer,ForeignKey("pharmacists.id"))
    supplier=relationship("Supplier",back_populates="messages",foreign_keys=supplier_id)
    pharmacist=relationship("Pharmacist",back_populates="messages",foreign_keys=pharmacist_id)


