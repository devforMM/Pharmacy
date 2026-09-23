from fastapi import APIRouter,Depends,Form
from sqlalchemy.orm import Session
from models.Bridge import get_session
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from models.DataBase import Supplier,Sale,Product,Stock,Supplyrequest,Message,Pharmacist
from server.server_utils import get_current_Pharmacist
from fastapi.exceptions import HTTPException
from datetime import datetime
from server.server_utils import hash_password,verify_password,create_token
from fastapi.responses import RedirectResponse
templates=Jinja2Templates(directory="../frontend/Pharmacist")





############################ Login/Register/Dashboard ##########################################

pharmasict_router=APIRouter()


@pharmasict_router.get("/login")
def login_template(request:Request):
    try:
        return templates.TemplateResponse(
            name="LoginTemplate.html",
            request=request
        )

    except  Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)



@pharmasict_router.get("/register")
def register_template(request:Request):
    try:
        return templates.TemplateResponse(
            request=request,
            name="RegisterTemplate.html"
        )

    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)



@pharmasict_router.post("/register")
def register(request:Request,first_name=Form(...),last_name=Form(...),email=Form(...),
            password=Form(...),phone_number=Form(...),adress=Form(...),bd:Session=Depends(get_session)
             ):
    try:
        new_pharmacist=Pharmacist(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password= hash_password(password) ,
            phone_number=phone_number,
            adress=adress
        )
        bd.add(new_pharmacist)
        bd.commit()
        return RedirectResponse(
            url="/pharmacist/login",
            status_code=303
        )

    except Exception as e:
        return templates.TemplateResponse(
            name="RegisterTemplate.html",
            request=request,
            context={"Error_Message":f"Registration Error: {e}"}
        )


@pharmasict_router.post("/login")
def login(request:Request,email=Form(...),password=Form(...),db:Session=Depends(get_session)):
    try:
        pharmacists=db.query(Pharmacist).all()
        emails=[ph.email for ph in pharmacists]
        print(emails)
        pharmacist=db.query(Pharmacist).filter(Pharmacist.email==email).first()
        if pharmacist:
            print("PHARMACIST:", pharmacist)

            if pharmacist:
                print("PASSWORD:", verify_password(password, pharmacist.password))

                if verify_password(password, pharmacist.password):
                    print("LOGIN SUCCESS")
                    
                    token = create_token({
                        "id": pharmacist.id,
                        "email": pharmacist.email
                    })

                    response = RedirectResponse(
                        url="/pharmacist/dashboard",
                        status_code=303
                    )

                    response.set_cookie(
                        "access_token",
                        token,
                        httponly=True
                    )

                    return response
            else:
                 return templates.TemplateResponse(
                     request=request,
                     name="LoginTemplate.html",
                     context={"message":"Invalid Password"}
                 )

        else:
            return templates.TemplateResponse(
                request=request,
                name="LoginTemplate.html",
                context={"message":"Invalid Email"}
            )   


    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="LoginTemplate.html",
            context={"message":f"Error {e}  while Login"}
        )


@pharmasict_router.get("/dashboard")
def dashboard_template(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try: 
        num_sales=len(pharmacist.sales)
        num_products=len(pharmacist.products)
        num_messages=len(pharmacist.messages)
        return templates.TemplateResponse(
            request=request,
            name="DashboardTemplate.html",
            context={
                "pharmacist":pharmacist,
                "num_sales":num_sales,
                "num_products":num_products,
                "num_messages":num_messages
            }
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")


@pharmasict_router.get("/logout")
def logout(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    return templates.TemplateResponse(
        request=request,
        name="LoginTemplate.html"
    )

@pharmasict_router.get("/daily_statistics")
def get_stastics(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:

        Sales=[sale for sale in pharmacist.sales if sale.date==datetime.today().strftime("%d/%m/%Y")]
        revenues=0
        profits=0
        costs=0
        sales_number=len(Sales)

        for s in Sales:
            revenues+=s.total
            profits+=s.Profit
            costs+=s.Cost    


        return templates.TemplateResponse(
            request=request,
            name="StatisticTemplate.html",
            context={
                "sales_number":sales_number,
                "revenues":revenues,
                "profits":profits,
                "costs":costs
            }
        )


    except Exception as e:
        raise HTTPException(detail=f"Server Error : {e}",status_code=400)






################################ suppliers ######################################################

@pharmasict_router.get("/suppliers")
def get_suppliers(request:Request,db:Session=Depends(get_session),pharmacist=Depends(get_current_Pharmacist)):
    try:
        suppliers=db.query(Supplier).all()
        return templates.TemplateResponse(
            request=request,
            name="AllSuppliersTemplate.html",
            context={
                "suppliers":suppliers
            }
        )

    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)



@pharmasict_router.get("/supplier_stock")
def supplier_details(request:Request,id_supplier:int,db:Session=Depends(get_session)):
    try:
        supplier=db.query(Supplier).filter(Supplier.id==id_supplier).first()
        return templates.TemplateResponse(
            request=request,
            name="SupplierStockTemplate.html",
            context={
                "supplier":supplier,
                "stocks":supplier.stocks
            }
        )

    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)


@pharmasict_router.post("/new_request")
def new_request(request:Request,stock_id:int,quantity:int,pharmacist=Depends(get_current_Pharmacist),bd:Session=Depends(get_session),
                
                 ):
    try:
        stock=bd.query(Stock).filter(Stock.id==stock_id).first()
        supplier=bd.query(Supplier).filter(Stock.id==stock_id).first()
        costs=stock.cost_price*quantity
        new_request=Supplyrequest(
            date=datetime.today().strftime(),
            product_name=stock.product_name,
            qantity=stock.quantity,
            supplier_id=stock.supplier_id,
            status="requested",
            pharmacist_id=pharmacist.id,
            stock_id=stock_id,
            all_costs=costs
        )
        bd.add(new_request)
        bd.commit()
        return templates.TemplateResponse(
            request=request,
            name="RequestsTemplate.html",
            context={"Message":"Request Added succesfully"}
        )


    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="SupplierStockTemplate.html",
            context={
                "supplier":supplier,
                "stocks":supplier.stocks,
                "Error_message":f"Error {e} while adding request"
            }
        )



########################################### Sales ##########################################################################

@pharmasict_router.get("/sale_details")
def sale_details(request:Request,sale_id:int,pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session)):
    try:
        sale=db.query(Sale).filter(Sale.id==sale_id).first()
        return templates.TemplateResponse(
            request=request,
            name="SaleDetailsTemplate.html",
            context={"sale":sale}
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")






@pharmasict_router.get("/sales")
def get_sales(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
 
        return templates.TemplateResponse(
            request=request,
            name="SalesTemplate.html",
            context={"sales":pharmacist.sales}
        )
    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)






#################################### products ########################################


@pharmasict_router.get("/products")
def store_products(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        products=pharmacist.products
        return templates.TemplateResponse(
           request=request,
           name="ProductsTemplate.html",
           context={
               "products":products
           }
       )

    except Exception as e:
        raise HTTPException(detail=F"Server Error: {e}",status_code=400)





@pharmasict_router.get("/alert_products")
def  expiring_products(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        alert_products = [
    stock
    for stock in pharmacist.products
    if 0 <= (
        datetime.strptime(stock.expiration_date, "%d/%m/%Y")
        - datetime.today()
    ).days <= 30
]

        return templates.TemplateResponse(
                request=request,
                name="AlertProductsTemplate copy.html",
                context={
                    "products":alert_products
                }

            )


    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)



@pharmasict_router.get("/low_products")
def  low_products(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        low_products = [prod for prod in pharmacist.products if product.quantity<10]
    

        return templates.TemplateResponse(
                request=request,
                name="LowProductsTemplate.html",
                context={
                    "products":low_products
                }

            )


    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)





@pharmasict_router.post("/delete_product")
def delete_prodcut(request:Request,product_id:int,pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session)):
    try:

       product=db.query(Product).filter(Product.id==product_id).first()
       db.delete(product)
       db.commit()
       return {"messsage":"Product deleted succesfully"}



    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")


    






@pharmasict_router.post("/define_price")
def define_price(request:Request,id_product:int,pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session),
                 selling_price:float=Form(...)):

    try:
        product=db.query(Product).filter(Product.id==id_product).first()
        product.selling_price=selling_price
        db.commit()
        db.refresh(product)
        products=pharmacist.products
        return templates.TemplateResponse(
           request=request,
           name="ProductsTemplate.html",
           context={
               "products":products
           }
       )
    
    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)







############################################# messages ##################################



@pharmasict_router.get("/message_form")
def message_form(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="AddMessageTemplate.html"
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error : {e}")




@pharmasict_router.post("/send_message")
def send_message(request:Request,supplier_email:str=Form(...),content:str=Form(...),object:str=Form(...),
                 pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session)):

    try:
        receiver=db.query(Supplier).filter(Supplier.email==supplier_email).first()
        if receiver:
            new_message=Message(
                object=object,
                message_content=content,
                supplier_id=receiver.id,
                pharmacist_id=pharmacist.id,
            )
            db.add(new_message)
            db.commit()
            return templates.TemplateResponse(
                request=request,
                name="MessagesTemplate.html",
                context={
                    "message":"Message added succesfully"
                }
            )
        else:
            return templates.TemplateResponse(
                request=request,
                name="AddMessageTemplate.html",
                context={
                    "message":"Invalid Email"
                }
            )



    except Exception as e:
        raise HTTPException(status_code=400,detail=F"Server Error: {e}")



@pharmasict_router.get("/messages")
def get_messages(request:Request,pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session)):
    try:

        emails=[
            db.query(Supplier).filter(Supplier.id==msg.supplier_id).first().email for msg in pharmacist.messages ]

        results=[
            {"id":msg.id,
             "object":msg.object,
             "content":msg.message_content,
             "email":email
             }

             for msg,email in zip(pharmacist.messages,emails)
        ]
        
        
        return templates.TemplateResponse(
            name="MessagesTemplate.html",
            request=request,
            context={
                "messages":results
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")












@pharmasict_router.get("/request")
def requests_template(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        
        return templates.TemplateResponse(
            request=request,
            name="RequestsTemplate.html",
            context={
                "requests":pharmacist.requests
            }
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")




@pharmasict_router.get("/request_details")
def request_details(request:Request,request_id:int,db:Session=Depends(get_session),pharmacist=Depends(get_current_Pharmacist)):
    try:
        supply_request=db.query(Supplyrequest).filter(Supplyrequest.id==request_id).filter().first()

        return templates.TemplateResponse(
            request=request,
            name="RequestDetailsTemplate.html",
            context={
                "supply_request":supply_request
            }
        )



    except Exception as e:
        raise HTTPException(detail=f"Server Error : {e}",status_code=400)



@pharmasict_router.get("/stock_details")
def sotck_details(request:Request,stock_id:int,pharmacist=Depends(get_current_Pharmacist),
                  db:Session=Depends(get_session)):
    try:
         stock=db.query(Stock).filter(Stock.id==stock_id).first()
         return templates.TemplateResponse(
             request=request,
             name="StockDetailsTemplate.html",
             context={
                 "stock":stock
             }   
         )


    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")



@pharmasict_router.post("/send_request")
def send_request(request:Request,stock_id:int,pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session),
                 quantity:int=Form(...),
                 ):
    try:

        stock=db.query(Stock).filter(Stock.id==stock_id).first()
        all_costs=quantity*stock.cost_price
        new_request=Supplyrequest(
            date=datetime.today().strftime(""),
            product_name=stock.product_name,
            quantity=quantity,
            supplier_id=stock.supplier_id,
            status="Pending",
            pharmacist_id=pharmacist.id,
            stock_id=stock.id,
            all_costs=all_costs

        )
        db.add(new_request)
        db.commit()
        return templates.TemplateResponse(
            request=request,
            name="RequestsTemplate.html",
            context={
                "requests":pharmacist.requests
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="StockDetailsTemplate.html",
            context={
                "Error_message":f"Error:  {e} ",
                "stock":stock
            }


        )




@pharmasict_router.post("/complete_request")
def complete_request(request:Request,request_id:int,pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session)):
    try:

        Supply_request=db.query(Supplyrequest).filter(Supplyrequest.id==request_id).first()
        stock=db.query(Stock).filter(Stock.id==Supply_request.stock_id).first()
        Supply_request.status="completed"
        stock.quantity-=Supply_request.quantity
        new_products=Product(
            name=stock.product_name,
            cost_price=stock.cost_price,
            reference=stock.reference,
            quantity=Supply_request.quantity,
            expiration_date=stock.expiration_date,
            pharmacist_id=pharmacist.id,
            stock_id=stock.id,
            supplier_id=stock.supplier_id
        )
        db.add(new_products)
        db.commit()
        return templates.TemplateResponse(
            request=request,
            name="ProductsTemplate.html",
            context={
                "products":pharmacist.products
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="RequestDetailsTemplate.html",
            context={

                "Error_message":f"Error:  {e} ",
                "supply_request":Supply_request
            }
        )

####################### Big Functions  ########################################################################




@pharmasict_router.post("/add_sale")
def add_sale(request:Request,db:Session=Depends(get_session),pharmacist=Depends(get_current_Pharmacist),
            client_informations=Form(...),quantities:list[int]=Form(...)):
    
    try:
       Total_cost=0
       Total_revenue=0
       products_sold=[]

       pharmacist_products=pharmacist.products

       for product,qte in zip(pharmacist_products,quantities):
            if qte>0:
                Total_revenue+=product.selling_price*qte
                Total_cost+=product.cost_price*qte
                
                products_sold.append(
                                {
                                    "Name":product.name,
                                    "Reference":product.reference,
                                    "quantity":qte,
                                    "Selling_price":product.selling_price,
                                }
                            )
                product.quantity-=qte
       
       Profit=Total_revenue-Total_cost
       new_sale=Sale(
                    date = datetime.today().strftime("%Y-%m-%d",),
                    client=client_informations,
                    products=products_sold,
                    pharmacist_id=pharmacist.id,
                    total=Total_revenue,
                    Profit=Profit,
                    Cost=Total_cost,

        )
       db.add(new_sale)
       db.commit()


       return templates.TemplateResponse(
            request=request,
            name="SaleDetailsTemplate.html",
            context={"sale":new_sale}
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")





@pharmasict_router.get("/requests")
def get_requests(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="RequestsTemplate.html",
            context={
                "requests":pharmacist.requests
            }
        )


    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)