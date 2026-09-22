from fastapi import APIRouter,Depends,Form
from sqlalchemy.orm import Session
from models.Bridge import get_session
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from models.DataBase import Supplier,Sale,Purchase,Product,Stock,Supplyrequest,Message,Pharmacist
from server.server_utils import get_current_Pharmacist
from fastapi.exceptions import HTTPException
from datetime import datetime
from server.server_utils import hash_password,verify_password,create_token
from fastapi.responses import RedirectResponse
templates=Jinja2Templates(directory="../templates/pharmacist")





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



@pharmasict_router.post("/regsiter")
def register(request:Request,first_name=Form(...),last_name=Form(...),email=Form(...),
            password=Form(...),phone_number=Form(...),adress=Form(...),bd:Session=Depends(get_session)
             ):
    try:
        new_supplier=Supplier(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password= hash_password(password) ,
            phone_number=phone_number,
            adress=adress
        )
        bd.add(new_supplier)
        bd.commit()
        return RedirectResponse(
            url="/pharmacist/login",
            status_code=303
        )

    except Exception as e:
        return templates.TemplateResponse(
            name="RegisterTemplate.html",
            request=request,
            context={"message":f"Registration Error: {e}"}
        )


@pharmasict_router.post("/login")
def login(request:Request,email=Form(...),password=Form(...),db:Session=Depends(get_session)):
    try:
        pharmacist=db.query(Pharmacist).filter(Pharmacist.email==email).first()
        if pharmacist:
            if verify_password(password,pharmacist.password):
                token=create_token({"id":pharmacist.id,"email":pharmacist.email})
                reponse=RedirectResponse(
                    url="pharmacist/dashboard",
                    status_code=303
                )
                reponse.set_cookie(
                    "access_token",
                    token,
                    httponly=True,
                    secure=True
                )
                return reponse
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
            context={"Error_Message":f"Error {e}  while Login"}
        )


@pharmasict_router.get("/dashboard")
def dashboard_template(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try: 
        num_sales=len(pharmacist.sales)
        num_purchases=len(pharmacist.purchases)
        num_products=len(pharmacist.products)
        num_messages=len(pharmacist.messages)
        return templates.TemplateResponse(
            request=request,
            name="DashboardTemplate.html",
            context={
                "pharmacist":pharmacist,
                "num_sales":num_sales,
                "num_purchases":num_purchases,
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
        name="Login.html"
    )

@pharmasict_router.get("/Daily_statistics")
def get_stastics(request:Request,date:str,pharmacist=Depends(get_current_Pharmacist)):
    try:

        Sales=[sale for sale in pharmacist.sales if sale.date==date]
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
            name="Statistic.html",
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
            name="SaledDetails.html",
            context={"sale":sale}
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")






@pharmasict_router.get("/sales")
def get_sales(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
 
        return templates.TemplateResponse(
            request=request,
            name="Sales.html",
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
           name="store_products.html",
           context={
               "products":products
           }
       )

    except Exception as e:
        raise HTTPException(detail=F"Server Error: {e}",status_code=400)





@pharmasict_router.get("/expiring_soon")
def  expiring_products(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        alert_products = [
    prod
    for prod in pharmacist.products
    if (datetime.today() - datetime.strptime(prod.expiration_date, "%Y-%m-%d")).days <= 30
]

        return templates.TemplateResponse(
                request=request,
                name="AlertProducts.html",
                context={
                    "products":alert_products
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
                 Selling_price:float=Form(...)):

    try:
        product=db.query(Product).filter(Product.id==id_product).first()
        product.selling_price=Selling_price
        db.refresh(product)
        db.commit()
        products=pharmacist.products
        return templates.TemplateResponse(
           request=request,
           name="store_products.html",
           context={
               "products":products
           }
       )
    
    except Exception as e:
        raise HTTPException(detail=f"Server Error: {e}",status_code=400)







############################################# messages ##################################



@pharmasict_router.post("/message_form")
def message_form(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        return templates.TemplateResponse(
            request=request,
            name="AddMessageTemplate.html"
        )

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error : {e}")




@pharmasict_router.post("/send_message")
def send_message(request:Request,supplier_id:int,content:str=Form(...),object:str=Form(...),
                 pharmacist=Depends(get_current_Pharmacist),db:Session=Depends(get_session)):

    try:
        receiver=db.query(Supplier).filter(Supplier.id==supplier_id).first()
        if receiver:

            new_message=Message(
                object=object,
                message_content=content,
                supplier_id=supplier_id,
                pharmacist_id=pharmacist,
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
def get_messages(request:Request,pharmacist=Depends(get_current_Pharmacist)):
    try:
        return templates.TemplateResponse(
            name="MessagesTemplate.html",
            request=request,
            context={
                "messages":pharmacist.messages
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
        supply_request=db.query(Supplyrequest).filter(Supplyrequest.id==request).filter()
        return templates.TemplateResponse(
            request=request,
            name="RequestDetailsTemplate.html",
            context={
                "request":supply_request
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
                 quantity=Form(...),
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
                "Error_message":f"Error:  {e} "
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
                "Error_message":f"Error:  {e} "
            }
        )

####################### Big Functions  ########################################################################




@pharmasict_router.post("/add_sale")
def add_sale(request:Request,db:Session=Depends(get_session),pharmacist=Depends(get_current_Pharmacist),
            client_informations=Form(...),products_ids:list[int]=Form(...),quantities:list[int]=Form(...)):
    
    try:
       Total_cost=0
       Total_revenue=0
       products_sold=[]

       target_products=[
           db.query(Product).filter(Product.id==prod_id).first() for prod_id in products_ids
       ]


       for product,qte in zip(target_products.copy(),quantities):
         
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
                    receiver=f"{pharmacist.first_name}-{pharmacist.last_name}",
                    products=products_sold,
                    pharmacist_id=pharmacist,
                    total=Total_revenue,
                    Profit=Profit,
                    Cost=Total_cost,

        )
       db.add(new_sale)
       db.commit()


       return templates.TemplateResponse(
            request=request,
            name="SaleDetails.html",
            context={"sale":new_sale}
        )
    except Exception as e:
        raise HTTPException(status_code=400,detail=f"Server Error: {e}")





